from pydantic import BaseModel
from enums import ServicesEnum


class ServiceRequest(BaseModel):
    type: ServicesEnum
    data: dict | None