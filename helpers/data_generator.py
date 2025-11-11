import random
import string
from typing import List
from api.models import EntityRequest, AdditionRequest


class DataGenerator:

    @staticmethod
    def random_string(length: int = 10) -> str:
        """Генерирует случайную строку из букв и цифр."""
        letters_and_digits = string.ascii_letters + string.digits
        return "".join(random.choice(letters_and_digits) for _ in range(length))

    @staticmethod
    def random_number(start: int = 1, end: int = 1000) -> int:
        """Генерирует случайное число в заданном диапазоне."""
        return random.randint(start, end)

    @staticmethod
    def random_list_of_numbers(size: int = 3) -> List[int]:
        """Генерирует список случайных чисел."""
        return [random.randint(1, 100) for _ in range(size)]

    @staticmethod
    def random_boolean() -> bool:
        """Возвращает случайное булево значение."""
        return random.choice([True, False])

    @staticmethod
    def generate_entity_payload() -> EntityRequest:
        """
        Генерирует полный, валидный payload для создания/обновления сущности.
        """
        return EntityRequest(
            addition=AdditionRequest(
                additional_info=f"Info_{DataGenerator.random_string(5)}",
                additional_number=DataGenerator.random_number(),
            ),
            important_numbers=DataGenerator.random_list_of_numbers(),
            title=f"Title_{DataGenerator.random_string()}",
            verified=DataGenerator.random_boolean(),
        )
