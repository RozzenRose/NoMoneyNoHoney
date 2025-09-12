from pydantic import BaseModel, field_validator
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
    is_rub: bool
    is_euro: bool
    is_rsd: bool

    @root_validator
    def check_only_one_currency(cls, values):
        is_rub = values.get('is_rub')
        is_euro = values.get('is_euro')
        is_rsd = values.get('is_rsd')
        if sum([is_rub, is_euro, is_rsd]) != 1:
            raise ValueError('Currency error: choose only one currency')
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


class PurchaseBase(BaseModel):
    name: str
    description: str
    price: float
    is_rub: bool
    is_euro: bool
    is_rsd: bool
    category_id: int


class PurchasesListCreate(BaseModel):
    purchases: list[PurchaseBase]
