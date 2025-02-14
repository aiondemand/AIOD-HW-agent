# src/hw_agent/api/configuration_router.py

import json
from typing import Any, Dict
from fastapi import APIRouter, HTTPException, Request, Response, status
from pydantic import BaseModel, Field
import yaml
from hw_agent.core.orchestrator_type import OrchestratorType
from hw_agent.exceptions.custom_exceptions import ConfigurationNotFoundError
from hw_agent.models.connection_config_models import ConnectionConfigResponse, ConnectionConfigCreate, ConnectionConfigRead
from hw_agent.services.repository_service import RepositoryService
from hw_agent.core.plugin_manager import PluginManager

router = APIRouter(prefix="/configurations", tags=["Configurations"])
repository_service = RepositoryService()


@router.post("/{orchestrator_type}", response_model=ConnectionConfigResponse, status_code=status.HTTP_201_CREATED)
async def store_configuration(orchestrator_type: OrchestratorType, request: Request):
    # Determine the content type
    content_type = request.headers.get('Content-Type', '')
    if 'application/json' in content_type:
        # Parse JSON body
        body = await request.json()
    elif 'application/x-yaml' in content_type or 'text/yaml' in content_type:
        # Parse YAML body
        raw_body = await request.body()
        body = yaml.safe_load(raw_body)
    else:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported Content-Type. Supported types are application/json and application/x-yaml."
        )

    # Validate the body
    if not isinstance(body, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload. Expected a dictionary"
        )

    # Bind the connection information to the model
    connection = ConnectionConfigCreate(**body)

    config_id = repository_service.save_configuration(connection)
    return ConnectionConfigResponse(config_id=config_id, orchestrator_type=orchestrator_type)


@router.get("/{config_id}", response_model=ConnectionConfigRead, status_code=status.HTTP_200_OK)
def get_configuration(config_id: str):
    config = repository_service.get_configuration(config_id)
    if not config:
        raise ConfigurationNotFoundError(
            f"Configuration with ID {config_id} not found.")
    return config


@router.get("/", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
def list_configurations():
    return repository_service.get_configurations()


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT, summary="Delete all configurations")
def delete_all_configurations():
    """
    Deletes all stored configurations.
    """
    repository_service.clear_all_configurations()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a configuration")
def delete_configuration(config_id: str):
    """Delete a configuration by its ID."""
    repository_service.delete_configuration(config_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
