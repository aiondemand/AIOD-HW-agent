# src/hw_agent/services/error_handling.py

import json
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from pydantic import ValidationError
from hw_agent.exceptions.custom_exceptions import APIRequestError, AuthenticationError, ConfigurationNotFoundError, ConnectionConfigurationError, PluginNotFoundError, ExternalAPIError


class ErrorDescription:
    def __init__(self, exception: Exception = None, detail: str = None, error: str = None):
        
        # Use provided error message or convert exception to string
        self.error = error or (str(exception) if exception else "Unknown error")
        # Use provided detail or get default detail from exception
        self.detail = self.detail = detail or self.get_default_detail(exception)

    def get_default_detail(self, exception):
        if exception:
            return f"{exception.__class__.__name__} error occurred"
        return "An unspecified error occurred."

    def to_dict(self):
        return {
            "detail": self.detail,
            "error": self.error
        }
    


def add_exception_handlers(app):
    @app.exception_handler(ConfigurationNotFoundError)
    async def configuration_not_found_handler(request: Request, exc: ConfigurationNotFoundError):
        return JSONResponse(
            status_code=404,
            content=ErrorDescription(exc).to_dict()
        )

    @app.exception_handler(PluginNotFoundError)
    async def plugin_not_found_handler(request: Request, exc: PluginNotFoundError):
        return JSONResponse(
            status_code=404,
            content=ErrorDescription(exc, "The requested plugin was not found").to_dict()
        )

    @app.exception_handler(ExternalAPIError)
    async def external_api_error_handler(request: Request, exc: ExternalAPIError):
        return JSONResponse(
            status_code=502,
            content=ErrorDescription(exc, "The external API could not be reached").to_dict()
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content=ErrorDescription(exc,  exc.body).to_dict()
        )

    @app.exception_handler(AuthenticationError)
    async def authentication_error_handler(request: Request, exc: AuthenticationError):
        return JSONResponse(
            status_code=401,
            content=ErrorDescription(exc).to_dict()
        )

    @app.exception_handler(APIRequestError)
    async def api_request_error_handler(request: Request, exc: APIRequestError):
        return JSONResponse(
            status_code=400,
            content=ErrorDescription(exc).to_dict()
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content=ErrorDescription(exc).to_dict()
        )

    @app.exception_handler(ResponseValidationError)
    async def validation_exception_handler(request: Request, exc: ResponseValidationError):
        # exc.errors() is a list of validation error details from FastAPI
        error_details = []
        for err in exc.errors():
            loc = err.get("loc", [])
            msg = err.get("msg", "")
            error_details.append({
                "location": loc,
                "message": msg
            })

        return JSONResponse(
            status_code=422,
            content=ErrorDescription(exc, error_details).to_dict()
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_error_handler(request: Request, exc: ValidationError):
        # This handles if a raw Pydantic ValidationError is raised outside the usual request body context
        error_details = []
        for err in exc.errors():
            loc = err.get("loc", [])
            msg = err.get("msg", "")
            error_details.append({
                "location": loc,
                "message": msg
            })

        return JSONResponse(
            status_code=422,
            content=ErrorDescription(exc, "Model validation error", error_details).to_dict()
        )

    @app.exception_handler(ConnectionConfigurationError)
    async def validate_connection_info(request: Request, exc: ConnectionConfigurationError):
        return JSONResponse(
            status_code=400,
            content=ErrorDescription(exc)
        )
