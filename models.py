from typing import Optional

from sqlmodel import Field, SQLModel


class Photo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    url: str


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    preferred_name: str
    email_address: str
