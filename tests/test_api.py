import allure
import pytest
import requests
from api.api_client import ApiClient
from api.models import EntityRequest
from helpers.data_generator import DataGenerator
from helpers.assertion_helpers import assert_status_code
import json


@allure.epic("Entity Management")
@allure.feature("Core Functionality")
class TestEntityAPI:

    @allure.story("Получение одной сущности")
    @allure.title("Успешное получение сущности по ее ID")
    @allure.description(
        "Этот тест проверяет, что после создания сущности ее можно успешно получить по ID, и все поля в ответе соответствуют отправленным данным.")
    @allure.link("https://.../test-cases/TC-001", name="TC-001: Получение сущности по ID")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_entity_by_id(self, api_client: ApiClient, created_entity: tuple):
        entity_id, initial_payload = created_entity

        with allure.step("Шаг 1: Выполнение запроса на получение сущности по ID"):
            entity_data = api_client.get_entity(entity_id)
            allure.attach(entity_data.model_dump_json(indent=2), "Полученный ответ от API", allure.attachment_type.JSON)

        with allure.step("Шаг 2: Валидация полученных данных"):
            with allure.step(f"Проверка, что ID сущности в ответе равен {entity_id}"):
                assert entity_data.id == entity_id, f"ID сущности не совпадает. Ожидался {entity_id}, получен {entity_data.id}"

            with allure.step(f"Проверка, что поле 'title' равно '{initial_payload.title}'"):
                assert entity_data.title == initial_payload.title, "Поле 'title' не совпадает с исходным"

            with allure.step(f"Проверка, что поле 'verified' равно {initial_payload.verified}"):
                assert entity_data.verified == initial_payload.verified, "Поле 'verified' не совпадает с исходным"

    @allure.story("Обновление существующей сущности")
    @allure.title("Успешное частичное обновление сущности")
    @allure.description(
        "Тест проверяет, что данные существующей сущности можно обновить через PATCH запрос и изменения корректно сохраняются.")
    @allure.link("https://.../test-cases/TC-002", name="TC-002: Обновление данных сущности")
    @allure.severity(allure.severity_level.NORMAL)
    def test_update_entity(self, api_client: ApiClient, created_entity: tuple):
        entity_id, initial_payload = created_entity

        with allure.step("Шаг 1: Подготовка новых данных для обновления"):
            update_payload = DataGenerator.generate_entity_payload()
            update_payload.verified = not initial_payload.verified
            allure.attach(update_payload.model_dump_json(indent=2), "Payload для обновления",
                          allure.attachment_type.JSON)

        with allure.step("Шаг 2: Выполнение запроса на обновление (PATCH)"):
            response = api_client.update_entity(entity_id, update_payload)
            with allure.step("Проверка, что статус-код ответа равен 204"):
                assert_status_code(response, 204)

        with allure.step("Шаг 3: Проверка, что данные в системе изменились"):
            updated_entity = api_client.get_entity(entity_id)

            with allure.step(f"Проверка, что поле 'title' обновилось на '{update_payload.title}'"):
                assert updated_entity.title == update_payload.title, "Поле 'title' не обновилось"

            with allure.step(f"Проверка, что поле 'verified' обновилось на {update_payload.verified}"):
                assert updated_entity.verified == update_payload.verified, "Поле 'verified' не обновилось"

    @allure.story("Получение списка сущностей")
    @allure.title("Проверка наличия созданной сущности в общем списке")
    @allure.description(
        "Тест проверяет, что после создания новой сущности, ее ID появляется в общем списке, получаемом через GET /getAll.")
    @allure.link("https://.../test-cases/TC-003", name="TC-003: Наличие сущности в общем списке")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_all_entities_contains_created(self, api_client: ApiClient, created_entity: tuple):
        entity_id, _ = created_entity

        with allure.step("Шаг 1: Получение всех сущностей"):
            all_entities = api_client.get_all_entities()

        with allure.step("Шаг 2: Проверка наличия созданной сущности в списке"):
            entity_ids = [entity.id for entity in all_entities]
            allure.attach(json.dumps(entity_ids, indent=2), "Список всех ID в ответе", allure.attachment_type.JSON)

            with allure.step(f"Проверка, что ID {entity_id} присутствует в списке"):
                assert entity_id in entity_ids, f"Созданная сущность с ID {entity_id} не найдена в общем списке"

    @allure.story("Удаление сущности")
    @allure.title("Полный цикл: создание и последующее удаление сущности")
    @allure.description(
        "Тест проверяет полный жизненный цикл: сущность создается, затем удаляется, после чего становится недоступной по прямому ID.")
    @allure.link("https://.../test-cases/TC-004", name="TC-004: Удаление сущности")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_delete_entity(self, api_client: ApiClient):
        with allure.step("Шаг 1: Создание сущности для последующего удаления"):
            payload = DataGenerator.generate_entity_payload()
            entity_id = api_client.create_entity(payload)

        with allure.step("Шаг 2: Выполнение запроса на удаление (DELETE)"):
            delete_response = api_client.delete_entity(entity_id)
            with allure.step("Проверка, что статус-код ответа равен 204"):
                assert_status_code(delete_response, 204)

        with allure.step("Шаг 3: Проверка, что сущность недоступна по ID"):
            with pytest.raises(requests.exceptions.HTTPError) as e:
                api_client.get_entity(entity_id)
            with allure.step("Проверка, что статус-код ответа 404 или 500"):
                assert_status_code(e.value.response, [404, 500])

    @allure.story("Получение списка сущностей")
    @allure.title("Проверка отсутствия удаленной сущности в общем списке")
    @allure.description(
        "Тест проверяет, что после удаления сущности, ее ID исчезает из общего списка, получаемого через GET /getAll.")
    @allure.severity(allure.severity_level.NORMAL)
    def test_deleted_entity_is_not_in_list(self, api_client: ApiClient):
        with allure.step("Шаг 1: Создание и получение ID сущности"):
            payload = DataGenerator.generate_entity_payload()
            entity_id = api_client.create_entity(payload)

        with allure.step("Шаг 2: Удаление созданной сущности"):
            delete_response = api_client.delete_entity(entity_id)
            with allure.step("Проверка, что статус-код ответа равен 204"):
                assert_status_code(delete_response, 204)

        with allure.step("Шаг 3: Проверка, что удаленной сущности нет в общем списке"):
            all_entities = api_client.get_all_entities()
            all_ids = [entity.id for entity in all_entities]

            with allure.step(f"Проверка, что ID {entity_id} отсутствует в списке"):
                assert entity_id not in all_ids, \
                    f"Удаленная сущность с ID {entity_id} все еще присутствует в общем списке!"

    @allure.story("Фильтрация списка сущностей")
    @allure.title("Успешная фильтрация списка сущностей по полю 'title'")
    @allure.description(
        "Тест проверяет корректную работу фильтрации по точному совпадению заголовка в эндпоинте GET /getAll.")
    @allure.link("https://.../test-cases/TC-005", name="TC-005: Фильтрация списка по заголовку")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_all_entities_with_title_filter(self, api_client: ApiClient, created_entity: tuple):
        entity_id, initial_payload = created_entity
        title_to_filter = initial_payload.title

        with allure.step(f"Шаг 1: Выполнение запроса с фильтром title='{title_to_filter}'"):
            params = {'title': title_to_filter}
            filtered_entities = api_client.get_all_entities(params=params)

            with allure.step("Проверка, что ответ не пустой"):
                assert len(filtered_entities) > 0, f"Фильтр по title='{title_to_filter}' вернул пустой список"

        with allure.step("Шаг 2: Проверка содержимого отфильтрованного списка"):
            entity_ids = [entity.id for entity in filtered_entities]
            with allure.step(f"Проверка, что ID {entity_id} присутствует в отфильтрованном списке"):
                assert entity_id in entity_ids, f"Созданная сущность с ID {entity_id} не найдена в отфильтрованном списке"

            with allure.step("Проверка, что все сущности в списке имеют правильный 'title'"):
                for entity in filtered_entities:
                    assert entity.title == title_to_filter, f"В отфильтрованном списке найдена сущность с неправильным title: '{entity.title}'"