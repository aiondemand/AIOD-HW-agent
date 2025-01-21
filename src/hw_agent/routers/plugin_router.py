# src/hw_agent/api/plugin_router.py

from typing import List
from fastapi import APIRouter, Depends, status
from hw_agent.core.plugin_manager import PluginManager
from hw_agent.models.plugin_models import PluginDefinition

router = APIRouter(prefix="/plugins", tags=["Plugins"])
plugin_manager = PluginManager()

@router.get("/", summary="Get all available plugins", status_code=status.HTTP_200_OK)
def get_all_plugins():
    return plugin_manager.get_all_plugins()

@router.post("/reload", summary="Reload all available plugins", status_code=status.HTTP_200_OK)
def reload_plugins():
    return plugin_manager.reload_plugins()
