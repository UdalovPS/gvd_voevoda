from typing import Union

from pydantic import BaseModel


class VoevodaRegSchem(BaseModel):
    """Схема для подключения аккаунта телеграм воеводы к системе"""
    id: int


class PersonRegisterSchem(BaseModel):
    player_id: int
    voevoda_id: int
    role: int


class VoevodaAuthSchem(BaseModel):
    voevoda_id: int
    name: str
    clan_id: int
    sub_person_id: Union[int, None] = None