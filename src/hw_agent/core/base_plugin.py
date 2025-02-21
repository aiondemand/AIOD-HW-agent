# src/hw_agent/core/base_plugin.py

from abc import ABC, abstractmethod

from datetime import datetime, timezone
import time
from typing import Any, Dict

from hw_agent.core.plugin_context import PluginContext
from hw_agent.models.computational_models import ComputationalData, ComputationalInfo, ComputationalMetadata
from hw_agent.models.computational_asset import ComputationalAsset
from hw_agent.models.plugin_models import PluginDefinition
from hw_agent.utils.logger import get_logger

class BasePlugin(ABC):
    def __init__(self):
        self.name = self.__class__.__name__
        self._plugin_definition: PluginDefinition  =  {}   
        self.logger = get_logger(self.name)
        

    @abstractmethod
    def fetch_computational_data(self, plugin_context: PluginContext) -> ComputationalData:
        """
        Fetches the data from the infrastructure and returns as a dict. It contains the orchestrator-specific data
        """
        raise NotImplementedError("Plugins must implement the fecth_computational_data method.")
    @abstractmethod
    def transform_computational_data(self, plugin_context: PluginContext, computational_data: ComputationalData) -> ComputationalAsset:
        """
        Transforms the data from the plugin into the standard format for the AIOD catalog.
        """
        raise NotImplementedError("Plugins must implement the transform_computational_data method.")


    @property
    def plugin_definition(self) -> PluginDefinition:
        """Get the configuration of the plugin."""
        return self._plugin_definition  # type: ignore[return-value]  # noqa: E501

    @plugin_definition.setter
    def plugin_definition(self, value: PluginDefinition):
        """Set the configuration of the plugin."""
        self._plugin_definition = value
        
    
    def fetch(self, plugin_context: PluginContext) -> ComputationalData:
        """Fetches computational data through the plugin.
        This method orchestrates the data collection process by calling the plugin-specific
        fetch_computational_data implementation and wrapping the results with timing and context information.
        Args:
            plugin_context (PluginContext): Context information required by the plugin to fetch data.
        Returns:
            ComputationalData: A wrapper object containing the collected computational data along with
            metadata like start time and duration.
        Note:
            This is a template method that relies on fetch_computational_data() being implemented
            by concrete plugin classes.
        """
        
        start_time = time.time()
        start_time_in_utc = datetime.now(timezone.utc)

        # Plugins implement this method to collect data
        self.logger.info("Starting fetching computational data through the plugin...")
        computational_info = self.fetch_computational_data(plugin_context)

        duration_time_in_seconds = time.time() - start_time
        
        self.logger.info("Building computational data...")
        computational_data = self._build_computational_data(
            computational_info=computational_info,
            plugin_context=plugin_context,
            start_time_in_utc=start_time_in_utc,
            duration_time_in_seconds=duration_time_in_seconds
        )        
        
        return computational_data
    
    def fetch_and_transform(self, plugin_context: PluginContext) -> ComputationalAsset:
        """Executes the fetch and transform pipeline for the plugin.
        This method orchestrates the data processing by first fetching the raw data
        using the plugin's fetch method, and then transforming it into a computational asset
        using the plugin-specific transformation logic.
        Args:
            plugin_context (PluginContext): The context object containing parameters and
                configuration needed for fetching and transforming the data.
        Returns:
            ComputationalAsset: The processed and transformed computational asset.
        Note:
            This method is part of the base plugin interface and coordinates the two main
            steps (fetch and transform) that all plugins must implement.
        """

        computational_data = self.fetch(plugin_context)
        
        # Plugins implement this method to transform the data
        self.logger.info("Starting transforming computational asset through the plugin...")

        return self.transform_computational_data(plugin_context, computational_data)
    
    
    def _build_computational_data(
        self,
        computational_info: ComputationalInfo,
        plugin_context: PluginContext,
        start_time_in_utc: datetime,
        duration_time_in_seconds: float
    ) -> ComputationalData:
        """
        Builds the ComputationalData model.

        Args:
            computational_info (ComputationalInfo): The computational info provided by the plugin.
            plugin_context (PluginContext): The plugin context with configuration details.
            start_time_in_utc (datetime): The start time of execution.
            duration_time_in_seconds (float): The duration of execution.

        Returns:
            ComputationalData: The complete data model.
        """
        metadata = ComputationalMetadata(
            plugin_definition=plugin_context.get_plugin_definition(),
            start_time_in_utc=start_time_in_utc,
            duration_time_in_seconds=duration_time_in_seconds
        )

        computational_data = ComputationalData(
            metadata=metadata,
            computational_info=computational_info
        )

        return computational_data