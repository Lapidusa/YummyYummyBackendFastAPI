from typing import Any, Optional

class ResponseUtils:
    @staticmethod
    def success(message: Optional[str] = None, **kwargs: Any) -> dict:
        response = {"result": True}
        if message:
            response["message"] = message
        if kwargs:
            response.update(kwargs)
        return response

    @staticmethod
    def error(message: str = "Произошла ошибка") -> dict:
        return {"result": False, "message": message}
