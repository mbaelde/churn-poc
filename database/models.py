from typing import List, Optional

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# Define the Customer table
class Customer(Base):
    __tablename__ = "Customer"

    id: Mapped[str] = mapped_column(primary_key=True, unique=True)
    gender: Mapped[str] = mapped_column(String)
    seniorCitizen: Mapped[str] = mapped_column(String)
    partner: Mapped[str] = mapped_column(String)
    dependents: Mapped[str] = mapped_column(String)

    # Define the one-to-one relationship between Customer and Contract
    contracts: Mapped[List["Contract"]] = relationship(back_populates="customer")
    churns: Mapped[List["CustomerChurn"]] = relationship(back_populates="customer")

    def __repr__(self) -> str:
        return f"Customer(id={self.id!r}, gender={self.gender!r}, seniorCitizen={self.seniorCitizen!r}, partner={self.partner!r}, dependents={self.dependents!r})"


# Define the PhoneService table
class PhoneService(Base):
    __tablename__ = "PhoneService"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    hasPhoneService: Mapped[str] = mapped_column(String)
    multipleLines: Mapped[str] = mapped_column(String)

    contract_id: Mapped[int] = mapped_column(ForeignKey("Contract.id"))
    contract: Mapped["Contract"] = relationship(back_populates="phone_service")

    def __repr__(self) -> str:
        return f"PhoneService(id={self.id!r}, hasPhoneService={self.hasPhoneService!r}, multipleLines={self.multipleLines!r})"


# Define the InternetService table
class InternetService(Base):
    __tablename__ = "InternetService"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    internetServiceType: Mapped[str] = mapped_column(String)
    onlineSecurity: Mapped[str] = mapped_column(String)
    onlineBackup: Mapped[str] = mapped_column(String)
    deviceProtection: Mapped[str] = mapped_column(String)
    techSupport: Mapped[str] = mapped_column(String)
    streamingTV: Mapped[str] = mapped_column(String)
    streamingMovies: Mapped[str] = mapped_column(String)

    contract_id: Mapped[int] = mapped_column(ForeignKey("Contract.id"))
    contract: Mapped["Contract"] = relationship(back_populates="internet_service")

    def __repr__(self) -> str:
        return f"InternetService(id={self.id!r}, internetServiceType={self.internetServiceType!r}, onlineSecurity={self.onlineSecurity!r}, onlineBackup={self.onlineBackup!r}, deviceProtection={self.deviceProtection!r}, techSupport={self.techSupport!r}, streamingTV={self.streamingTV!r}, streamingMovies={self.streamingMovies!r})"


# Define the Contract table
class Contract(Base):
    __tablename__ = "Contract"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    contractType: Mapped[str] = mapped_column(String)
    tenure: Mapped[int] = mapped_column(Integer)
    paperlessBilling: Mapped[str] = mapped_column(String)
    paymentMethod: Mapped[str] = mapped_column(String)
    monthlyCharges: Mapped[float] = mapped_column(Float)
    totalCharges: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    customer_id: Mapped[int] = mapped_column(ForeignKey("Customer.id"))
    customer: Mapped["Customer"] = relationship(back_populates="contracts")

    # Define the one-to-one relationship between Contract and PhoneService
    phone_service: Mapped["PhoneService"] = relationship(back_populates="contract")

    # Define the one-to-one relationship between Contract and InternetService
    internet_service: Mapped["InternetService"] = relationship(
        back_populates="contract"
    )

    def __repr__(self) -> str:
        return f"Contract(id={self.id!r}, contractType={self.contractType!r}, tenure={self.tenure!r}, paperlessBilling={self.paperlessBilling!r}, paymentMethod={self.paymentMethod!r}, monthlyCharges={self.monthlyCharges!r}, totalCharges={self.totalCharges!r})"


# Define the Churn table
class CustomerChurn(Base):
    __tablename__ = "CustomerChurn"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    churn: Mapped[str] = mapped_column(String)

    customer_id: Mapped[int] = mapped_column(ForeignKey("Customer.id"))
    customer: Mapped["Customer"] = relationship(back_populates="churns")

    def __repr__(self) -> str:
        return f"CustomerChurn(id={self.id!r}, churn={self.churn!r})"
