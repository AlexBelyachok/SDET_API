import allure
import pytest
import requests
from api.api_client import ApiClient
from api.models import EntityRequest, AdditionRequest
from helpers.data_generator import DataGenerator
from helpers.assertion_helpers import assert_status_code


@allure.epic("Entity Management")
@allure.feature("Core Functionality")
class TestEntityAPI:

    @allure.title("Получение сущности по ID")
    def test_get_entity_by_id(self, api_client: ApiClient, created_entity: tuple):
        entity_id, initial_payload = created_entity
        entity_data = api_client.get_entity(entity_id)
        assert (
            entity_data.id == entity_id
        ), f"ID сущности не совпадает. Ожидался {entity_id}, получен {entity_data.id}"
        assert (
            entity_data.title == initial_payload.title
        ), "Поле 'title' не совпадает с исходным"
        assert (
            entity_data.verified == initial_payload.verified
        ), "Поле 'verified' не совпадает с исходным"

    @allure.title("Обновление сущности")
    def test_update_entity(self, api_client: ApiClient, created_entity: tuple):
        entity_id, initial_payload = created_entity
        update_payload = DataGenerator.generate_entity_payload()
        update_payload.verified = not initial_payload.verified

        response = api_client.update_entity(entity_id, update_payload)
        # ВЫЗОВ КАК ПРОСТОЙ ФУНКЦИИ
        assert_status_code(response, 204)

        updated_entity = api_client.get_entity(entity_id)
        assert (
            updated_entity.title == update_payload.title
        ), "Поле 'title' не обновилось"
        assert (
            updated_entity.verified == update_payload.verified
        ), "Поле 'verified' не обновилось"

    @allure.title("Проверка наличия сущности в общем списке")
    def test_get_all_entities_contains_created(
        self, api_client: ApiClient, created_entity: tuple
    ):
        entity_id, _ = created_entity
        all_entities = api_client.get_all_entities()
        entity_ids = [entity.id for entity in all_entities]
        assert (
            entity_id in entity_ids
        ), f"Созданная сущность с ID {entity_id} не найдена в общем списке"

    @allure.title("Создание и удаление сущности")
    def test_delete_entity(self, api_client: ApiClient):
        payload = DataGenerator.generate_entity_payload()
        entity_id = api_client.create_entity(payload)

        delete_response = api_client.delete_entity(entity_id)

        assert_status_code(delete_response, 204)

        with pytest.raises(requests.exceptions.HTTPError) as e:
            api_client.get_entity(entity_id)

        assert_status_code(e.value.response, [404, 500])

    @allure.title("Проверка отсутствия удаленной сущности в общем списке")
    @allure.severity(allure.severity_level.NORMAL)
    def test_deleted_entity_is_not_in_list(self, api_client: ApiClient):
        """
        Тест-кейс:
        1. Создать сущность.
        2. Удалить ее.
        3. Запросить общий список и убедиться, что ID удаленной сущности там нет.
        """
        with allure.step("Шаг 1: Создание и получение ID сущности"):
            payload = DataGenerator.generate_entity_payload()
            entity_id = api_client.create_entity(payload)

        with allure.step("Шаг 2: Удаление созданной сущности"):
            delete_response = api_client.delete_entity(entity_id)
            assert_status_code(delete_response, 204)

        with allure.step("Шаг 3: Проверка, что удаленной сущности нет в общем списке"):
            all_entities = api_client.get_all_entities()
            all_ids = [entity.id for entity in all_entities]
            assert (
                entity_id not in all_ids
            ), f"Удаленная сущность с ID {entity_id} все еще присутствует в общем списке!"

    @allure.title("Фильтрация списка сущностей по заголовку")
    def test_get_all_entities_with_title_filter(
        self, api_client: ApiClient, created_entity: tuple
    ):
        entity_id, initial_payload = created_entity
        title_to_filter = initial_payload.title
        params = {"title": title_to_filter}
        filtered_entities = api_client.get_all_entities(params=params)

        assert (
            len(filtered_entities) > 0
        ), f"Фильтр по title='{title_to_filter}' вернул пустой список"

        entity_ids = [entity.id for entity in filtered_entities]
        assert (
            entity_id in entity_ids
        ), f"Созданная сущность с ID {entity_id} не найдена в отфильтрованном списке"

        for entity in filtered_entities:
            assert (
                entity.title == title_to_filter
            ), f"В отфильтрованном списке найдена сущность с неправильным title: '{entity.title}'"
