from pydantic import BaseModel


class ReaderItem(BaseModel):
    phone: str
    nick_name: str = ''
    age: int = 0
    gender: str = 'male'
    password: str
    avatar: str = ''
