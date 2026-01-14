# src/hw_agent/exceptions/custom_exceptions.py

class ConfigurationNotFoundError(Exception):
    """Exception raised when a configuration is not found."""

class PluginNotFoundError(Exception):
    """Exception raised when a plugin is not found."""

class ExternalAPIError(Exception):
    """Exception raised when an external API call fails."""
    
class AuthenticationError(Exception):
    """Exception raised when authentication fails."""   
    
class APIRequestError(Exception):
    """Exception raised when an API request fails."""

class PluginLoadError(Exception):
    """Exception raised when a plugin configuration is invalid."""
    
class ConnectionConfigurationError(Exception):
    """Exception raised when a connection configuration is invalid."""