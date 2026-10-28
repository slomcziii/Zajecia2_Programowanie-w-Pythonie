"""Ćwiczenia praktyczne 2–5: SQLAlchemy + SQLite + Alembic.

Uruchomienie (z folderu baza-eksperymentow):
    uv run python main.py
albo:
    .venv\\Scripts\\python.exe main.py

Skrypt wykonuje po kolei:
  Ćw. 2   – tworzy plik bazy eksperymenty.db i wszystkie tabele
            (przez migracje Alembic),
  Ćw. 3/4 – dodaje 2 eksperymenty i 20 punktów danych (po 10 na eksperyment),
  Ćw. 5b  – dodaje 2 obiekty Subject i łączy je z eksperymentami
            (relacja wiele-do-wielu),
  Ćw. 3   – pobiera dodane dane i wyświetla informacje o nich,
  Ćw. 5   – liczy sumę i średnią DataPoint dla każdego eksperymentu,
  Ćw. 3   – ustawia finished=True we wszystkich eksperymentach,
  Ćw. 3   – usuwa wszystkie wiersze ze wszystkich tabel.
"""

import random
from datetime import datetime
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, delete, func, select, update
from sqlalchemy.orm import Session, selectinload

from models import Base, DataPoint, Experiment, Subject, experiment_subject

KATALOG = Path(__file__).resolve().parent
PLIK_BAZY = KATALOG / "eksperymenty.db"
ADRES_BAZY = f"sqlite:///{PLIK_BAZY}"

engine = create_engine(ADRES_BAZY, echo=False)


def naglowek(tekst):
    print(f"\n=== {tekst} ===")


def przygotuj_baze():
    """Ćw. 2: tworzy plik bazy danych i wszystkie zdefiniowane tabele.

    Przed wprowadzeniem Alembica (ćw. 5) robiła to jedna linijka:
        Base.metadata.create_all(engine)
    Teraz schemat opisują migracje w katalogu alembic/versions,
    więc aplikujemy je do najnowszej wersji ("head").
    """
    naglowek("Ćw. 2 – przygotowanie bazy danych")
    config = Config(str(KATALOG / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", ADRES_BAZY)
    command.upgrade(config, "head")
    print(f"Plik bazy: {PLIK_BAZY} (istnieje: {PLIK_BAZY.exists()})")
    print("Tabele:", ", ".join(Base.metadata.tables))


def dodaj_dane(session):
    """Ćw. 3 (pkt 1–2) i ćw. 4: 2 eksperymenty, po 10 DataPoint na każdy."""
    naglowek("Ćw. 3/4 – dodawanie danych")
    eksperymenty = [
        Experiment(title="Eksperyment 1", created_at=datetime.now(), type=1),
        Experiment(title="Eksperyment 2", created_at=datetime.now(), type=2),
    ]
    for eksperyment in eksperymenty:
        for _ in range(10):
            eksperyment.data_points.append(
                DataPoint(
                    real_value=random.random(),
                    target_value=random.random(),
                )
            )
    session.add_all(eksperymenty)

    # Ćw. 5b – relacja wiele-do-wielu Subject <-> Experiment.
    subject1 = Subject()  # gdpr_accepted domyślnie False
    subject2 = Subject(gdpr_accepted=True)
    subject1.experiments.extend(eksperymenty)
    subject2.experiments.append(eksperymenty[0])
    session.add_all([subject1, subject2])

    session.commit()
    print("Eksperymenty:", session.scalar(select(func.count(Experiment.id))))
    print("Punkty danych:", session.scalar(select(func.count(DataPoint.id))))
    print("Subjects:", session.scalar(select(func.count(Subject.id))))


def wyswietl_dane(session):
    """Ćw. 3 (pkt 3): pobiera dodane dane i wyświetla informacje o nich."""
    naglowek("Ćw. 3 – odczyt danych")
    eksperymenty = session.scalars(
        select(Experiment)
        .options(selectinload(Experiment.data_points))
        .order_by(Experiment.id)
    ).all()

    for e in eksperymenty:
        print(
            f"Experiment id={e.id}, title={e.title!r}, "
            f"created_at={e.created_at:%Y-%m-%d %H:%M:%S}, "
            f"type={e.type}, finished={e.finished}"
        )
        for dp in e.data_points:
            print(
                f"    DataPoint id={dp.id}: "
                f"real_value={dp.real_value:.4f}, "
                f"target_value={dp.target_value:.4f}"
            )

    for s in session.scalars(select(Subject).order_by(Subject.id)):
        print(
            f"Subject id={s.id}, gdpr_accepted={s.gdpr_accepted}, "
            f"eksperymenty={[e.id for e in s.experiments]}"
        )


def agregacja(session):
    """Ćw. 5: suma i średnia wszystkich DataPoint dla każdego eksperymentu."""
    naglowek("Ćw. 5 – agregacja")
    stmt = (
        select(
            Experiment.id,
            Experiment.title,
            func.count(DataPoint.id).label("liczba"),
            func.sum(DataPoint.real_value).label("suma_real"),
            func.avg(DataPoint.real_value).label("srednia_real"),
            func.sum(DataPoint.target_value).label("suma_target"),
            func.avg(DataPoint.target_value).label("srednia_target"),
        )
        .join(Experiment.data_points)
        .group_by(Experiment.id, Experiment.title)
        .order_by(Experiment.id)
    )

    for w in session.execute(stmt):
        print(f"{w.title} (id={w.id}): {w.liczba} punktów")
        print(
            f"    real_value:   suma={w.suma_real:.4f}, "
            f"średnia={w.srednia_real:.4f}"
        )
        print(
            f"    target_value: suma={w.suma_target:.4f}, "
            f"średnia={w.srednia_target:.4f}"
        )


def zaktualizuj_eksperymenty(session):
    """Ćw. 3 (pkt 4): ustawia finished=True we wszystkich eksperymentach."""
    naglowek("Ćw. 3 – aktualizacja")
    wynik = session.execute(update(Experiment).values(finished=True))
    session.commit()
    print(f"Zaktualizowano wierszy: {wynik.rowcount}")
    for e in session.scalars(select(Experiment).order_by(Experiment.id)):
        print(f"Experiment id={e.id}: finished={e.finished}")


def usun_wszystko(session):
    """Ćw. 3 (pkt 5): usuwa wszystkie wiersze z obu tabel.

    Po dodaniu relacji trzeba zachować kolejność: najpierw tabele
    z kluczami obcymi, na końcu experiments.
    """
    naglowek("Ćw. 3 – usuwanie")
    session.execute(delete(experiment_subject))
    usuniete_dp = session.execute(delete(DataPoint)).rowcount
    usuniete_s = session.execute(delete(Subject)).rowcount
    usuniete_e = session.execute(delete(Experiment)).rowcount
    session.commit()

    print(
        f"Usunięto: {usuniete_e} eksperymentów, {usuniete_dp} punktów danych, "
        f"{usuniete_s} subjects"
    )
    print(
        "Pozostało – eksperymenty:",
        session.scalar(select(func.count(Experiment.id))),
        "punkty danych:",
        session.scalar(select(func.count(DataPoint.id))),
        "subjects:",
        session.scalar(select(func.count(Subject.id))),
    )


if __name__ == "__main__":
    przygotuj_baze()

    with Session(engine) as session:
        dodaj_dane(session)
        wyswietl_dane(session)
        agregacja(session)
        zaktualizuj_eksperymenty(session)
        usun_wszystko(session)

    engine.dispose()
