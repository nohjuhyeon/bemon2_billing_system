from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import mapped_column, relationship
from databases.connections import Base

class UserList(Base):
    __tablename__ = "USER_LIST"
    USER_ID = mapped_column(Integer, primary_key=True, autoincrement=True)
    USER_NAME = mapped_column(String(50), nullable=True)
    clouds = relationship("CloudList", back_populates="user", cascade='delete')

class CloudList(Base):
    __tablename__ = "CLOUD_LIST"
    CLOUD_ID = mapped_column(Integer, primary_key=True, autoincrement=True)
    USER_ID = mapped_column(Integer, ForeignKey("USER_LIST.USER_ID"))
    CLOUD_NAME = mapped_column(String(50), nullable=True)
    CLOUD_CLASS = mapped_column(String(50), nullable=True)
    CLOUD_KEY = mapped_column(String(50), nullable=True)
    START_DATE = mapped_column(Integer, nullable=True)
    user = relationship("UserList", back_populates="clouds")
    services = relationship("ServiceList", back_populates="cloud", cascade='delete')
    total_charges = relationship("TotalChargeList", back_populates="cloud", cascade='delete')

class ServiceList(Base):
    __tablename__ = "SERVICE_LIST"
    SERVICE_ID = mapped_column(Integer, primary_key=True, autoincrement=True)
    CLOUD_ID = mapped_column(Integer, ForeignKey("CLOUD_LIST.CLOUD_ID"))
    SERVICE_NAME = mapped_column(String(50), nullable=True)
    SERVICE_CODE = mapped_column(String(50), nullable=True)
    cloud = relationship("CloudList", back_populates="services")

class TotalCloudChargeList(Base):
    __tablename__ = "TOTAL_CLOUD_CHARGE_LIST"
    TOTAL_CLOUD_CHARGE_ID = mapped_column(Integer, primary_key=True, autoincrement=True)
    TOTAL_CHARGE_ID = mapped_column(Integer, ForeignKey("TOTAL_CHARGE_LIST.TOTAL_CHARGE_ID"))
    TOTAL_CLOUD_USE_AMT = mapped_column(Integer, nullable=True)
    TOTAL_CLOUD_DISCOUNT_AMT = mapped_column(Integer, nullable=True)
    TOTAL_CLOUD_VAT_AMT = mapped_column(Integer, nullable=True)
    TOTAL_CLOUD_VAT_INCLUDE_AMT = mapped_column(Integer, nullable=True)
    TOTAL_CLOUD_PAY_AMT = mapped_column(Integer, nullable=True)
    TOTAL_CLOUD_USER_PAY_AMT = mapped_column(Integer, nullable=True)
    TOTAL_CLOUD_NOTES = mapped_column(String(50), nullable=True)
    total_charge = relationship("TotalChargeList", back_populates="total_cloud_charges")
    cloud_service_charges = relationship("CloudServiceChargeList", back_populates="total_cloud_charge", cascade='delete')

class CloudServiceChargeList(Base):
    __tablename__ = "CLOUD_SERVICE_CHARGE_LIST"
    CLOUD_SERVICE_CHARGE_ID = mapped_column(Integer, primary_key=True, autoincrement=True)
    TOTAL_CLOUD_CHARGE_ID = mapped_column(Integer, ForeignKey("TOTAL_CLOUD_CHARGE_LIST.TOTAL_CLOUD_CHARGE_ID"))
    CLOUD_SERVICE_CHARGE_NAME = mapped_column(String(50), nullable=True)
    CLOUD_SERVICE_CHARGE_CODE = mapped_column(String(50), nullable=True)
    CLOUD_SERVICE_USE_AMT = mapped_column(Integer, nullable=True)
    CLOUD_SERVICE_DISCOUNT_AMT = mapped_column(Integer, nullable=True)
    CLOUD_SERVICE_PAY_AMT = mapped_column(Integer, nullable=True)
    CLOUD_SERVICE_NOTES = mapped_column(String(50), nullable=True)
    total_cloud_charge = relationship("TotalCloudChargeList", back_populates="cloud_service_charges")
    type_charges = relationship("TypeChargeList", back_populates="cloud_service_charge", cascade='delete')

class TypeChargeList(Base):
    __tablename__ = "TYPE_CHARGE_LIST"
    TYPE_CHARGE_ID = mapped_column(Integer, primary_key=True, autoincrement=True)
    CLOUD_SERVICE_CHARGE_ID = mapped_column(Integer, ForeignKey("CLOUD_SERVICE_CHARGE_LIST.CLOUD_SERVICE_CHARGE_ID"))
    TYPE_NAME = mapped_column(String(50), nullable=True)
    TYPE_USE_AMT = mapped_column(Integer, nullable=True)
    TYPE_NOTES = mapped_column(String(50), nullable=True)
    cloud_service_charge = relationship("CloudServiceChargeList", back_populates="type_charges")
    items = relationship("ItemChargeList", back_populates="type_charge", cascade='delete')

class ItemChargeList(Base):
    __tablename__ = "ITEM_CHARGE_LIST"
    ITEM_CHARGE_ID = mapped_column(Integer, primary_key=True, autoincrement=True)
    TYPE_CHARGE_ID = mapped_column(Integer, ForeignKey("TYPE_CHARGE_LIST.TYPE_CHARGE_ID"))
    ITEM_NAME = mapped_column(String(50), nullable=True)
    ITEM_REGION = mapped_column(String(50), nullable=True)
    ITEM_USE_AMT = mapped_column(Integer, nullable=True)
    ITEM_START_DATE = mapped_column(DateTime, nullable=True)
    ITEM_NOTES = mapped_column(String(50), nullable=True)
    type_charge = relationship("TypeChargeList", back_populates="items")

class ThirdPartyChargeList(Base):
    __tablename__ = "THIRD_PARTY_CHARGE_LIST"
    THIRD_PARTY_CHARGE_ID = mapped_column(Integer, primary_key=True, autoincrement=True)
    TOTAL_THIRD_PARTY_CHARGE_ID = mapped_column(Integer, ForeignKey("TOTAL_THIRD_PARTY_CHARGE_LIST.TOTAL_THIRD_PARTY_CHARGE_ID"))
    THIRD_PARTY_NAME = mapped_column(String(50), nullable=True)
    THIRD_PARTY_PRODUCT_NAME = mapped_column(String(50), nullable=True)
    THIRD_PARTY_USE_AMT = mapped_column(Integer, nullable=True)
    THIRD_PARTY_PAY_AMT = mapped_column(Integer, nullable=True)
    THIRD_PARTY_NOTES = mapped_column(String(50), nullable=True)
    total_third_party_charge = relationship("TotalThirdPartyChargeList", back_populates="total_third_party_charges")

class ManagedServiceList(Base):
    __tablename__ = "MANAGED_SERVICE_LIST"
    MANAGED_SERVICE_CHARGE_ID = mapped_column(Integer, primary_key=True, autoincrement=True)
    TOTAL_MANAGED_SERVICE_CHARGE_ID = mapped_column(Integer, ForeignKey("TOTAL_MANAGED_SERVICE_CHARGE_LIST.TOTAL_MANAGED_SERVICE_CHARGE_ID"))
    MANAGED_SERVICE_NAME = mapped_column(String(50), nullable=True)
    MANAGED_PRODUCT_NAME = mapped_column(String(50), nullable=True)
    MANAGED_SERVICE_USE_AMT = mapped_column(Integer, nullable=True)
    MANAGED_SERVICE_PAY_AMT = mapped_column(Integer, nullable=True)
    MANAGED_SERVICE_NOTES = mapped_column(String(50), nullable=True)
    total_managed_service_charge = relationship("TotalManagedServiceChargeList", back_populates="total_managed_service_charges")

class OtherServiceList(Base):
    __tablename__ = "OTHER_SERVICE_LIST"
    OTHER_SERVICE_CHARGE_ID = mapped_column(Integer, primary_key=True, autoincrement=True)
    TOTAL_OTHER_SERVICE_CHARGE_ID = mapped_column(Integer, ForeignKey("TOTAL_OTHER_SERVICE_CHARGE_LIST.TOTAL_OTHER_SERVICE_CHARGE_ID"))
    OTHER_SERVICE_NAME = mapped_column(String(50), nullable=True)
    OTHER_PRODUCT_NAME = mapped_column(String(50), nullable=True)
    OTHER_SERVICE_USE_AMT = mapped_column(Integer, nullable=True)
    OTHER_SERVICE_PAY_AMT = mapped_column(Integer, nullable=True)
    OTHER_SERVICE_NOTES = mapped_column(String(50), nullable=True)
    total_other_service_charge = relationship("TotalOtherServiceChargeList", back_populates="total_other_service_charges")

class TotalChargeList(Base):
    __tablename__ = "TOTAL_CHARGE_LIST"
    TOTAL_CHARGE_ID = mapped_column(Integer, primary_key=True, autoincrement=True)
    CLOUD_ID = mapped_column(Integer, ForeignKey("CLOUD_LIST.CLOUD_ID"))
    BILL_MONTH = mapped_column(Integer, nullable=True)
    TOTAL_USE_AMT = mapped_column(Integer, nullable=True)
    TOTAL_DISCOUNT_AMT = mapped_column(Integer, nullable=True)
    TOTAL_SALES_DISCOUNT_AMT = mapped_column(Integer, nullable=True)
    TOTAL_COIN_USE_AMT = mapped_column(Integer, nullable=True)
    TOTAL_DEFAULT_AMT = mapped_column(Integer, nullable=True)
    TOTAL_VAT_AMT = mapped_column(Integer, nullable=True)
    TOTAL_VAT_INCLUDE_AMT = mapped_column(Integer, nullable=True)
    TOTAL_PAY_AMT = mapped_column(Integer, nullable=True)
    TOTAL_DISCOUNT_INCLUDE_AMT = mapped_column(Integer, nullable=True)
    TOTAL_USER_PAY_AMT = mapped_column(Integer, nullable=True)
    TOTAL_USE_NOTES = mapped_column(String(50), nullable=True)
    TOTAL_COIN_USE_NOTES = mapped_column(String(50), nullable=True)
    TOTAL_VAT_NOTES = mapped_column(String(50), nullable=True)
    TOTAL_PAY_NOTES = mapped_column(String(50), nullable=True)
    TOTAL_VAT_INCLUDE_NOTES = mapped_column(String(50), nullable=True)
    TOTAL_DISCOUNT_INCLUDE_NOTES = mapped_column(String(50), nullable=True)
    TOTAL_DISCOUNT_NOTES = mapped_column(String(50), nullable=True)
    TOTAL_SALES_DISCOUNT_NOTES = mapped_column(String(50), nullable=True)
    TOTAL_DEFAULT_NOTES = mapped_column(String(50), nullable=True)
    cloud = relationship("CloudList", back_populates="total_charges")
    total_cloud_charges = relationship("TotalCloudChargeList", back_populates="total_charge", cascade='delete')
    total_third_party_charges = relationship("TotalThirdPartyChargeList", back_populates="total_charge", cascade='delete')
    total_managed_services = relationship("TotalManagedServiceChargeList", back_populates="total_charge", cascade='delete')
    total_other_services = relationship("TotalOtherServiceChargeList", back_populates="total_charge", cascade='delete')

class TotalManagedServiceChargeList(Base):
    __tablename__ = "TOTAL_MANAGED_SERVICE_CHARGE_LIST"
    TOTAL_MANAGED_SERVICE_CHARGE_ID = mapped_column(Integer, primary_key=True, autoincrement=True)
    TOTAL_CHARGE_ID = mapped_column(Integer, ForeignKey("TOTAL_CHARGE_LIST.TOTAL_CHARGE_ID"))
    TOTAL_MANAGED_SERVICE_USE_AMT = mapped_column(Integer, nullable=True)
    TOTAL_MANAGED_SERVICE_DISCOUNT_AMT = mapped_column(Integer, nullable=True)
    TOTAL_MANAGED_SERVICE_VAT_AMT = mapped_column(Integer, nullable=True)
    TOTAL_MANAGED_SERVICE_VAT_INCLUDE_AMT = mapped_column(Integer, nullable=True)
    TOTAL_MANAGED_SERVICE_PAY_AMT = mapped_column(Integer, nullable=True)
    TOTAL_MANAGED_SERVICE_USER_PAY_AMT = mapped_column(Integer, nullable=True)
    TOTAL_MANAGED_SERVICE_NOTES = mapped_column(String(50), nullable=True)
    total_charge = relationship("TotalChargeList", back_populates="total_managed_services")
    total_managed_service_charges = relationship("ManagedServiceList", back_populates="total_managed_service_charge", cascade='delete')

class TotalThirdPartyChargeList(Base):
    __tablename__ = "TOTAL_THIRD_PARTY_CHARGE_LIST"
    TOTAL_THIRD_PARTY_CHARGE_ID = mapped_column(Integer, primary_key=True, autoincrement=True)
    TOTAL_CHARGE_ID = mapped_column(Integer, ForeignKey("TOTAL_CHARGE_LIST.TOTAL_CHARGE_ID"))
    TOTAL_THIRD_PARTY_USE_AMT = mapped_column(Integer, nullable=True)
    TOTAL_THIRD_PARTY_DISCOUNT_AMT = mapped_column(Integer, nullable=True)
    TOTAL_THIRD_PARTY_VAT_AMT = mapped_column(Integer, nullable=True)
    TOTAL_THIRD_PARTY_VAT_INCLUDE_AMT = mapped_column(Integer, nullable=True)
    TOTAL_THIRD_PARTY_PAY_AMT = mapped_column(Integer, nullable=True)
    TOTAL_THIRD_PARTY_USER_PAY_AMT = mapped_column(Integer, nullable=True)
    TOTAL_THIRD_PARTY_NOTES = mapped_column(String(50), nullable=True)
    total_charge = relationship("TotalChargeList", back_populates="total_third_party_charges")
    total_third_party_charges = relationship("ThirdPartyChargeList", back_populates="total_third_party_charge", cascade='delete')

class TotalOtherServiceChargeList(Base):
    __tablename__ = "TOTAL_OTHER_SERVICE_CHARGE_LIST"
    TOTAL_OTHER_SERVICE_CHARGE_ID = mapped_column(Integer, primary_key=True, autoincrement=True)
    TOTAL_CHARGE_ID = mapped_column(Integer, ForeignKey("TOTAL_CHARGE_LIST.TOTAL_CHARGE_ID"))
    TOTAL_OTHER_SERVICE_USE_AMT = mapped_column(Integer, nullable=True)
    TOTAL_OTHER_SERVICE_DISCOUNT_AMT = mapped_column(Integer, nullable=True)
    TOTAL_OTHER_SERVICE_VAT_AMT = mapped_column(Integer, nullable=True)
    TOTAL_OTHER_SERVICE_VAT_INCLUDE_AMT = mapped_column(Integer, nullable=True)
    TOTAL_OTHER_SERVICE_PAY_AMT = mapped_column(Integer, nullable=True)
    TOTAL_OTHER_SERVICE_USER_PAY_AMT = mapped_column(Integer, nullable=True)
    TOTAL_OTHER_SERVICE_NOTES = mapped_column(String(50), nullable=True)
    total_charge = relationship("TotalChargeList", back_populates="total_other_services")
    total_other_service_charges = relationship("OtherServiceList", back_populates="total_other_service_charge", cascade='delete')
