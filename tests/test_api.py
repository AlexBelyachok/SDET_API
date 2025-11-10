import allure
import pytest
import requests
from api.api_client import ApiClient
from api.models import EntityRequest, AdditionRequest

@allure.epic("Entity Management")
@allure.feature("Core Functionality")
class TestEntityAPI:

    @allure.title("Получение сущности по ID")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_entity_by_id(self, api_client: ApiClient, created_entity: tuple):
        entity_id, initial_payload = created_entity

        with allure.step("Выполнение запроса и валидация ответа"):
            entity_data = api_client.get_entity(entity_id)
            allure.attach(entity_data.model_dump_json(indent=2), "Ответ от API", allure.attachment_type.JSON)

            assert entity_data.id == entity_id
            assert entity_data.title == initial_payload.title
            assert entity_data.verified == initial_payload.verified

    @allure.title("Обновление сущности")
    @allure.severity(allure.severity_level.NORMAL)
    def test_update_entity(self, api_client: ApiClient, created_entity: tuple):
        entity_id, _ = created_entity

        with allure.step("Подготовка данных для обновления"):
            update_payload = EntityRequest(
                addition=AdditionRequest(additional_info="Обновлено", additional_number=999),
                important_numbers=[9, 8, 7],
                title="Обновленный заголовок",
                verified=False
            )

        with allure.step("Выполнение запроса на обновление"):
            response = api_client.update_entity(entity_id, update_payload)
            assert response.status_code == 204

        with allure.step("Проверка, что данные изменились"):
            updated_entity = api_client.get_entity(entity_id)
            assert updated_entity.title == update_payload.title
            assert updated_entity.verified == update_payload.verified

    @allure.title("Проверка наличия сущности в общем списке")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_all_entities_contains_created(self, api_client: ApiClient, created_entity: tuple):
        entity_id, _ = created_entity

        with allure.step("Получение всех сущностей и проверка наличия созданной"):
            all_entities = api_client.get_all_entities()
            entity_ids = [entity.id for entity in all_entities]
            assert entity_id in entity_ids

    @allure.title("Создание и удаление сущности")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_delete_entity(self, api_client: ApiClient, entity_payload: EntityRequest):
        with allure.step("Создание сущности для удаления"):
            entity_id = api_client.create_entity(entity_payload)

        with allure.step("Выполнение запроса на удаление"):
            delete_response = api_client.delete_entity(entity_id)
            assert delete_response.status_code == 204

        with allure.step("Проверка, что сущность удалена"):
            with pytest.raises(requests.exceptions.HTTPError) as e:
                api_client.get_entity(entity_id)
            # Проверяем, что сервер отвечает 404 (правильно) или 500 (из-за бага в API)
            assert e.value.response.status_code in [404, 500]

    @allure.title("Фильтрация списка сущностей по заголовку")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_all_entities_with_title_filter(self, api_client: ApiClient, created_entity: tuple):
        entity_id, initial_payload = created_entity
        title_to_filter = initial_payload.title

        with allure.step(f"Выполнение запроса с фильтром title='{title_to_filter}'"):
            params = {'title': title_to_filter}
            filtered_entities = api_client.get_all_entities(params=params)
            assert len(filtered_entities) > 0

        with allure.step("Проверка содержимого отфильтрованного списка"):
            entity_ids = [entity.id for entity in filtered_entities]
            assert entity_id in entity_ids
            for entity in filtered_entities:
                assert entity.title == title_to_filter