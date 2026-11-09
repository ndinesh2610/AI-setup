from pydantic import BaseModel


class CVData(BaseModel):
    full_name: str
    email: str
    phone: str
    location: str
    years_experience: int
    skills: list[str]
