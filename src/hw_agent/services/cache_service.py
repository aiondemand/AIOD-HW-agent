# src/hw_agent/services/cache_service.py

class CacheService:
    def __init__(self):
        self.cache = {}

    def store_plugin(self, plugin_name, plugin_instance):
        self.cache[plugin_name] = plugin_instance

    def retrieve_plugin(self, plugin_name):
        return self.cache.get(plugin_name)
    
    def clear_plugins(self):
        self.cache.clear()
