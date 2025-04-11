from typing import Optional,List
  # 데이터베이스와 연결하거나 데이터를 상호작용할 때 사용

from beanie import Document, Link  # 데이터베이스의 데이터를 문서나 링크 형태로 가져올 수 있는 기능을 제공

# from pydantic import BaseModel, EmailStr


# 개발자 실수로 들어가는 field 제한
class Total_charge(
    Document
):  # 상속을 위한 것                 # 데이터 베이스에서 이용할 값들을 설정
    cloud_id: Optional[str] = None
    bill_month: Optional[int] = None
    use_amt: Optional[int] = None
    total_discount_amt: Optional[int] = None
    coin_use_amt: Optional[int] = None
    default_amt: Optional[int] = None
    pay_amt: Optional[int] = None
    vat_amt: Optional[int] = None
    pay_amt_including_vat: Optional[int] = None
    charge_id: Optional[str] = None

    class Settings:  # 데이터 베이스에서 이용할 collection을 지정
        name = "total_charge_list"  # collection의 이름
