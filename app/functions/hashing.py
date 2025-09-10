from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


ph = PasswordHasher(time_cost=3, memory_cost=256*1024, parallelism=2)  # ~256 MiB


async def PassHasher(password: str) -> str:
    hash_str = ph.hash(password)          # храните hash_str
    return hash_str


async def PassVerify(hash_str: str, password_input: str) -> bool:
    try:
        ph.verify(hash_str, password_input)   # True/исключение
        return True
    except VerifyMismatchError:
        return False