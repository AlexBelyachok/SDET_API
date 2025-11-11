from requests import Response


def assert_status_code(response: Response, expected_code):
    """
    Проверяет, что статус-код ответа соответствует ожидаемому.
    Принимает как одно число, так и список/кортеж возможных кодов.
    """
    actual_code = response.status_code

    if isinstance(expected_code, (list, tuple)):
        assert (
            actual_code in expected_code
        ), f"ОШИБКА: Неожиданный статус-код. Ожидался один из {expected_code}, но получен {actual_code}."
    else:
        assert (
            actual_code == expected_code
        ), f"ОШИБКА: Неожиданный статус-код. Ожидался {expected_code}, но получен {actual_code}."
