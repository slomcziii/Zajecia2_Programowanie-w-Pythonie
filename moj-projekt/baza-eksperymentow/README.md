# baza-eksperymentow – ćwiczenia 2–5 (SQLAlchemy, SQLite, Alembic)

## Pliki

- `models.py` – modele `Experiment`, `DataPoint`, `Subject` oraz tabela
  łącząca `experiment_subject` (relacja jeden-do-wielu Experiment → DataPoint,
  relacja wiele-do-wielu Subject ↔ Experiment).
- `main.py` – skrypt wykonujący po kolei: utworzenie bazy (migracje Alembic),
  dodanie 2 eksperymentów i 20 punktów danych, odczyt, agregację (suma i średnia),
  aktualizację `finished=True` i usunięcie wszystkich wierszy.
- `alembic.ini`, `alembic/` – konfiguracja i migracje:
  - `3d5d4a344eee` – tabele `experiments` i `data_points`,
  - `0abb2f14eacc` – tabela `subjects` i `experiment_subject`.
- `eksperymenty.db` – plik bazy SQLite (tworzony automatycznie).

## Uruchomienie

```bash
uv run python main.py
```

Jeśli `uv` nie jest w PATH:

```bash
python -m uv run python main.py
```

## Migracje ręcznie

```bash
uv run alembic upgrade head      # zaaplikuj wszystkie migracje
uv run alembic current           # pokaż aktualną wersję bazy
uv run alembic check             # sprawdź, czy modele zgadzają się z bazą
uv run alembic revision --autogenerate -m "opis"   # nowa migracja po zmianie modeli
```

Żeby zacząć od zera, wystarczy usunąć plik `eksperymenty.db` i ponownie
uruchomić `main.py`.
