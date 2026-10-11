from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    create_engine,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from backend.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


# These two classes mirror db/schema.sql, which is what creates the tables.


class Customer(Base):
    __tablename__ = "customers"

    customer_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    gender: Mapped[str | None] = mapped_column(String(10))
    senior_citizen: Mapped[bool | None] = mapped_column(Boolean)
    partner: Mapped[bool | None] = mapped_column(Boolean)
    dependents: Mapped[bool | None] = mapped_column(Boolean)
    tenure: Mapped[int | None] = mapped_column(Integer)
    phone_service: Mapped[bool | None] = mapped_column(Boolean)
    multiple_lines: Mapped[str | None] = mapped_column(String(20))
    internet_service: Mapped[str | None] = mapped_column(String(20))
    online_security: Mapped[str | None] = mapped_column(String(20))
    online_backup: Mapped[str | None] = mapped_column(String(20))
    device_protection: Mapped[str | None] = mapped_column(String(20))
    tech_support: Mapped[str | None] = mapped_column(String(20))
    streaming_tv: Mapped[str | None] = mapped_column(String(20))
    streaming_movies: Mapped[str | None] = mapped_column(String(20))
    contract_type: Mapped[str | None] = mapped_column(String(20))
    paperless_billing: Mapped[bool | None] = mapped_column(Boolean)
    payment_method: Mapped[str | None] = mapped_column(String(30))
    monthly_charges: Mapped[float | None] = mapped_column(Numeric(10, 2, asdecimal=False))
    total_charges: Mapped[float | None] = mapped_column(Numeric(10, 2, asdecimal=False))
    churn_label: Mapped[bool | None] = mapped_column(Boolean)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())


class Prediction(Base):
    __tablename__ = "predictions"

    prediction_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[str | None] = mapped_column(
        String(50), ForeignKey("customers.customer_id", ondelete="SET NULL")
    )
    churn_probability: Mapped[float | None] = mapped_column(Float)
    churn_prediction: Mapped[bool | None] = mapped_column(Boolean)
    model_version: Mapped[str | None] = mapped_column(String(20))
    threshold_used: Mapped[float | None] = mapped_column(Float)
    predicted_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())


def get_db():
    """
    FastAPI dependency that hands a route a database session and closes it
    once the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
