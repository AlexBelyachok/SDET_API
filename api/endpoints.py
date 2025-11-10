class ApiEndpoints:
    """
    Класс для хранения и формирования эндпоинтов API.
    """
    create_entity = "/create"
    get_all_entities = "/getAll"

    @staticmethod
    def get_entity_by_id(entity_id: int) -> str:
        return f"/get/{entity_id}"

    @staticmethod
    def update_entity_by_id(entity_id: int) -> str:
        return f"/patch/{entity_id}"

    @staticmethod
    def delete_entity_by_id(entity_id: int) -> str:
        return f"/delete/{entity_id}"