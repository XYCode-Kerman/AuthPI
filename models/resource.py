from pydantic import BaseModel


class Resource(BaseModel):
    slug: str
    name: str
    description: str
    actions: list[str]
