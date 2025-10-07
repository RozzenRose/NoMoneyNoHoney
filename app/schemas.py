from pydantic import BaseModel, field_validator, Field
from datetime import date
from pydantic.v1 import root_validator


class CreateUser(BaseModel):
    firstname: str
    lastname: str
    username: str
    email: str
    password: str

    @field_validator('firstname', 'lastname')
    @classmethod
    def names_check(cls, name):
        if name.isalpha():
            return name.capitalize()
        raise ValueError('Only letters in names, please')


class CreateIncome(BaseModel):
    description: str
    quantity: float
    currency: str

    @root_validator
    def check_currency(cls, values):
        if values.get('currency') not in ('EUR', 'RUB', 'RSD'):
            raise ValueError('Currency error: choose only EUR/RUB/RSD or leave this field blank')
        return values


class IncomeTimeLimits(BaseModel):
    start_date: date = date.today()
    end_date: date = date.today()

    @root_validator
    def check_dates(cls, values):
        start_date = values.get('start_date')
        end_date = values.get('end_date')
        if start_date >= end_date:
            raise ValueError('Date error: start_date must be earlier than end_date')
        return values


class PurchaseTimeLimits(IncomeTimeLimits):
    pass


class PurchaseBase(BaseModel):
    name: str
    description: str
    price: float
    currency: str
    category_id: int


class PurchasesListCreate(BaseModel):
    purchases: list[PurchaseBase]
