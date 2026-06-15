from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.response import error


class AppError(Exception):
    def __init__(self, message: str, code: int = 500, status_code: int | None = None) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code or code


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        return error(exc.message, code=exc.code, status_code=exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        return error("请求参数校验失败", code=422, data=exc.errors(), status_code=422)
