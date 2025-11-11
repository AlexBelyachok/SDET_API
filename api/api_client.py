import allure
import json
import requests
from requests import Response
from typing import List
from api.models import EntityRequest, EntityResponse, GetAllResponse
from api.endpoints import ApiEndpoints


class ApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()

    def _request(self, method: str, url: str, **kwargs) -> Response:
        """Единый метод для отправки всех запросов через сессию."""
        response = self.session.request(method, url, **kwargs)
        return response

    @allure.step("Создание сущности (POST /create)")
    def create_entity(self, payload: EntityRequest) -> int:
        """Создает сущность и возвращает ее ID."""
        url = f"{self.base_url}{ApiEndpoints.create_entity}"
        payload_dict = payload.model_dump()
        allure.attach(
            json.dumps(payload_dict, indent=2),
            "Request Body",
            allure.attachment_type.JSON,
        )

        response = self._request("POST", url, json=payload_dict)
        response.raise_for_status()
        entity_id = response.json()
        allure.attach(
            str(entity_id),
            f"ID созданной сущности: {entity_id}",
            allure.attachment_type.TEXT,
        )
        return entity_id

    @allure.step("Получение сущности по ID (GET /get/{entity_id})")
    def get_entity(self, entity_id: int) -> EntityResponse:
        """Получает сущность и возвращает ее как объект EntityResponse."""
        url = f"{self.base_url}{ApiEndpoints.get_entity_by_id(entity_id)}"
        response = self._request("GET", url)
        response.raise_for_status()
        return EntityResponse.model_validate(response.json())

    @allure.step("Получение списка всех сущностей (GET /getAll)")
    def get_all_entities(self, params: dict = None) -> List[EntityResponse]:
        """Получает список сущностей и возвращает его как List[EntityResponse]."""
        url = f"{self.base_url}{ApiEndpoints.get_all_entities}"
        response = self._request("GET", url, params=params)
        response.raise_for_status()
        return GetAllResponse.model_validate(response.json()).entity

    @allure.step("Обновление сущности по ID (PATCH /patch/{entity_id})")
    def update_entity(self, entity_id: int, payload: EntityRequest) -> Response:
        """Обновляет сущность. Возвращает полный объект Response для проверки статус-кода."""
        url = f"{self.base_url}{ApiEndpoints.update_entity_by_id(entity_id)}"
        payload_dict = payload.model_dump()
        allure.attach(
            json.dumps(payload_dict, indent=2),
            "Request Body",
            allure.attachment_type.JSON,
        )
        return self._request("PATCH", url, json=payload_dict)

    @allure.step("Удаление сущности по ID (DELETE /delete/{entity_id})")
    def delete_entity(self, entity_id: int) -> Response:
        """Удаляет сущность. Возвращает полный объект Response для проверки статус-кода."""
        url = f"{self.base_url}{ApiEndpoints.delete_entity_by_id(entity_id)}"
        return self._request("DELETE", url)
