from datetime import date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Float, Boolean, ForeignKey, Date
from typing import List


class Base(DeclarativeBase):
    pass


class RFP(Base):
    __tablename__ = "rfps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    external_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    title: Mapped[str] = mapped_column(String)
    source_url: Mapped[str] = mapped_column(String)

    # ✅ FIXED LINE ↓↓↓
    due_date: Mapped[date] = mapped_column(Date, nullable=False)

    line_items: Mapped[List["RFPLineItem"]] = relationship(
        back_populates="rfp", cascade="all, delete-orphan"
    )
    tests: Mapped[List["RFPTest"]] = relationship(
        back_populates="rfp", cascade="all, delete-orphan"
    )


class RFPLineItem(Base):
    __tablename__ = "rfp_line_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rfp_id: Mapped[int] = mapped_column(ForeignKey("rfps.id"))
    line_no: Mapped[int] = mapped_column(Integer)

    description: Mapped[str] = mapped_column(String)
    quantity_m: Mapped[float] = mapped_column(Float)

    conductor: Mapped[str] = mapped_column(String)
    insulation: Mapped[str] = mapped_column(String)
    voltage_kv: Mapped[float] = mapped_column(Float)
    cores: Mapped[float] = mapped_column(Float)
    size_sqmm: Mapped[float] = mapped_column(Float)
    armoured: Mapped[bool] = mapped_column(Boolean)

    rfp: Mapped["RFP"] = relationship(back_populates="line_items")


class RFPTest(Base):
    __tablename__ = "rfp_tests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rfp_id: Mapped[int] = mapped_column(ForeignKey("rfps.id"))

    test_code: Mapped[str] = mapped_column(String)

    rfp: Mapped["RFP"] = relationship(back_populates="tests")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sku: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String)
    category: Mapped[str] = mapped_column(String)

    conductor: Mapped[str] = mapped_column(String)
    insulation: Mapped[str] = mapped_column(String)
    voltage_kv: Mapped[float] = mapped_column(Float)
    cores: Mapped[float] = mapped_column(Float)
    size_sqmm: Mapped[float] = mapped_column(Float)
    application: Mapped[str] = mapped_column(String)
    armoured: Mapped[bool] = mapped_column(Boolean)


class SkuPrice(Base):
    __tablename__ = "sku_prices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sku: Mapped[str] = mapped_column(String, index=True)
    unit_price: Mapped[float] = mapped_column(Float)


class TestPrice(Base):
    __tablename__ = "test_prices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    test_code: Mapped[str] = mapped_column(String, unique=True)
    price: Mapped[float] = mapped_column(Float)
