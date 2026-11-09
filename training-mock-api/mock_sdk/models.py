from pydantic import BaseModel


class Parcel(BaseModel):
    id: int
    name: str
    status: str
    category: str
    created: str
