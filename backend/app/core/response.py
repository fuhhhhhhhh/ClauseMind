from typing import Any

from fastapi.responses import JSONResponse


def success(data: Any = None, message: str = "success", code: int = 200) -> dict[str, Any]:
    return {"code": code, "message": message, "data": data}


def error(message: str, code: int = 500, data: Any = None, status_code: int | None = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code or code,
        content={"code": code, "message": message, "data": data},
    )
