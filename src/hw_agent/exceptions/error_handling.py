# src/hw_agent/services/error_handling.py

import json
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from pydantic import ValidationError
from hw_agent.exceptions.custom_exceptions import APIRequestError, AuthenticationError, ConfigurationNotFoundError, PluginNotFoundError, ExternalAPIError

def add_exception_handlers(app):
    @app.exception_handler(ConfigurationNotFoundError)
    async def configuration_not_found_handler(request: Request, exc: ConfigurationNotFoundError):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)}
        )

    @app.exception_handler(PluginNotFoundError)
    async def plugin_not_found_handler(request: Request, exc: PluginNotFoundError):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)}
        )

    @app.exception_handler(ExternalAPIError)
    async def external_api_error_handler(request: Request, exc: ExternalAPIError):
        return JSONResponse(
            status_code=502,
            content={"detail": str(exc)}
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors(), "body": exc.body}
        )

    @app.exception_handler(AuthenticationError)
    async def authentication_error_handler(request: Request, exc: AuthenticationError):
        return JSONResponse(
            status_code=401,
            content={"detail": str(exc)}    
    )
        
    @app.exception_handler(APIRequestError)
    async def api_request_error_handler(request: Request, exc: APIRequestError):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)}
        )
            

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred", "error": str(exc)}
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
            content={
                "detail": "Validation Error",
                "errors": error_details
            }
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
            content={
                "detail": "Model Validation Error",
                "errors": error_details
            }
        )