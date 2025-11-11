import pytest
import os
import allure
from dotenv import load_dotenv
from api.api_client import ApiClient
from api.models import EntityRequest
from helpers.data_generator import DataGenerator
from helpers.assertion_helpers import assert_status_code

load_dotenv()


@pytest.fixture(scope="session")
def base_url() -> str:
    url = os.getenv("API_HOST")
    if not url:
        pytest.fail("Переменная окружения не задана в .env файле")
    return f"{url}/api"


@pytest.fixture(scope="session")
def api_client(base_url: str) -> ApiClient:
    return ApiClient(base_url=base_url)


@pytest.fixture(scope="function")
def entity_payload() -> EntityRequest:
    return DataGenerator.generate_entity_payload()


@pytest.fixture(scope="function")
def created_entity(api_client: ApiClient, entity_payload: EntityRequest) -> tuple:
    entity_id = None
    with allure.step(
        "Предварительное условие: создание сущности со случайными данными"
    ):
        try:
            entity_id = api_client.create_entity(entity_payload)
            assert isinstance(
                entity_id, int
            ), "ID созданной сущности должен быть числом"
        except Exception as e:
            pytest.fail(f"Не удалось создать тестовую сущность в фикстуре: {e}")

    yield entity_id, entity_payload

    with allure.step(f"Очистка: удаление сущности с ID {entity_id}"):
        if entity_id:
            response = api_client.delete_entity(entity_id)
            # Вызываем просто как функцию
            assert_status_code(response, [204, 404, 500])
