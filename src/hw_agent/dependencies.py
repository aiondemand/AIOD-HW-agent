# src/hw_agent/dependencies.py

from hw_agent.services.cache_service import CacheService
from hw_agent.services.plugin_manager_configuration_service import PluginManagerConfigurationService
from hw_agent.services.settings_service import SettingsService

# Singleton instances to avoid multiple loads
_plugin_manager_config_service_instance = None
_plugin_cache_service_instance = None
_setting_service_instance = None


def get_plugin_manager_configuration_service() -> PluginManagerConfigurationService:
    global _plugin_manager_config_service_instance
    if _plugin_manager_config_service_instance is None:
        _plugin_manager_config_service_instance = PluginManagerConfigurationService()
    return _plugin_manager_config_service_instance

def get_plugin_cache_service() -> CacheService:
    global _plugin_cache_service_instance
    if _plugin_cache_service_instance is None:
        _plugin_cache_service_instance = CacheService()
    return _plugin_cache_service_instance

def get_setting_service() -> SettingsService:
    global _setting_service_instance
    if _setting_service_instance is None:
        _setting_service_instance = SettingsService()
    return _setting_service_instance

