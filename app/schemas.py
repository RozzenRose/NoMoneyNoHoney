from pydantic import BaseModel, field_validator
from datetime import datetime
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
