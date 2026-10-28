from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey,
    Integer, String, Table,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

experiment_subject = Table(
    "experiment_subject",
    Base.metadata,
    Column(
        "experiment_id", Integer,
        ForeignKey("experiments.id"), primary_key=True,
    ),
    Column(
        "subject_id", Integer,
        ForeignKey("subjects.id"), primary_key=True,
    ),
)


class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    created_at = Column(DateTime)
    type = Column(Integer)
    finished = Column(Boolean, default=False, server_default="0")

    data_points = relationship("DataPoint", back_populates="experiment")

    subjects = relationship(
        "Subject",
        secondary=experiment_subject,
        back_populates="experiments",
    )


class DataPoint(Base):
    __tablename__ = "data_points"

    id = Column(Integer, primary_key=True)
    real_value = Column(Float)
    target_value = Column(Float)

    experiment_id = Column(
        Integer, ForeignKey("experiments.id"), nullable=False
    )
    experiment = relationship("Experiment", back_populates="data_points")


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True)
    gdpr_accepted = Column(
        Boolean, default=False, server_default="0", nullable=False
    )

    experiments = relationship(
        "Experiment",
        secondary=experiment_subject,
        back_populates="subjects",
    )