import httpx
from app.config import settings


async def email_validation(email):
    url = 'https://emailvalidation.abstractapi.com/v1/'
    params = {
        'api_key': settings.abstract_key,
        'email': email
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
    if response.json()['deliverability'] == 'DELIVERABLE':
        return True
    else:
        return False
