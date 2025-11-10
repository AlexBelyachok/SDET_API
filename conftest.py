# conftest.py (ПОЛНОСТЬЮ ИСПРАВЛЕННЫЙ)

import pytest
import os
import allure
from dotenv import load_dotenv
from api.api_client import ApiClient
from api.models import EntityRequest, AdditionRequest

load_dotenv()

@pytest.fixture(scope="session")
def base_url() -> str:
    url = os.getenv("BASE_URL", "http://localhost:8080")
    return f"{url}/api"

@pytest.fixture(scope="session")
def api_client(base_url: str) -> ApiClient:
    return ApiClient(base_url=base_url)

@pytest.fixture(scope="function")
def entity_payload() -> EntityRequest:
    return EntityRequest(
        addition=AdditionRequest(
            additional_info="Тестовая информация",
            additional_number=123
        ),
        important_numbers=[1, 2, 3],
        title="Тестовый заголовок",
        verified=True
    )

@pytest.fixture(scope="function")
def created_entity(api_client: ApiClient, entity_payload: EntityRequest) -> tuple:
    """
    Создает сущность перед тестом и удаляет после.
    """
    entity_id = None
    with allure.step("Предварительное условие: создание сущности"):
        try:
            # ТЕПЕРЬ ПРАВИЛЬНО: create_entity сразу возвращает ID
            entity_id = api_client.create_entity(entity_payload)
            assert isinstance(entity_id, int)
        except Exception as e:
            pytest.fail(f"Не удалось создать тестовую сущность в фикстуре: {e}")

    yield entity_id, entity_payload

    with allure.step(f"Очистка: удаление сущности с ID {entity_id}"):
        if entity_id:
            response = api_client.delete_entity(entity_id)
            assert response.status_code in [204, 404, 500], "Очистка после теста не удалась"