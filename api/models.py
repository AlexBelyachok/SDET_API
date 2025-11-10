from typing import List
from pydantic import BaseModel, Field

class AdditionRequest(BaseModel):
    """ Модель для дополнительной информации в запросе """
    additional_info: str = Field(..., json_schema_extra={'example': "Дополнительные сведения"})
    additional_number: int = Field(..., json_schema_extra={'example': 123})

class EntityRequest(BaseModel):
    """ Модель для создания/обновления сущности """
    addition: AdditionRequest
    important_numbers: List[int] = Field(..., json_schema_extra={'example': [42, 87, 15]})
    title: str = Field(..., json_schema_extra={'example': "Заголовок сущности"})
    verified: bool = Field(..., json_schema_extra={'example': True})

class AdditionResponse(BaseModel):
    """ Модель для дополнительной информации в ответе """
    additional_info: str
    additional_number: int
    id: int

class EntityResponse(BaseModel):
    """ Модель для ответа при получении сущности """
    addition: AdditionResponse
    id: int
    important_numbers: List[int]
    title: str
    verified: bool

class GetAllResponse(BaseModel):
    """ Модель для полного ответа от GET /getAll, содержащего список сущностей """
    entity: List[EntityResponse]