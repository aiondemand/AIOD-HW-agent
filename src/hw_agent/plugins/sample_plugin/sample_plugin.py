# hw_agent/plugins/openstack/openstack_plugin.py

from hw_agent.core.base_plugin import BasePlugin
from hw_agent.core.plugin_context import PluginContext
from hw_agent.models.computational_asset import ComputationalAsset
from hw_agent.models.computational_models import ComputationalData
from hw_agent.utils.logger import get_logger
from typing import Any, Dict

class SamplePlugin(BasePlugin):
    def __init__(self):
        super().__init__()

    def fetch_computational_data(self, plugin_context: PluginContext) -> Dict[str, Any]:
        """
        Fetches the data from the infrastructure and returns as a dict. It contains the 
        orchestrator-specific data
        """
        return None

    def transform_computational_data(self, plugin_context: PluginContext, computational_data: ComputationalData) -> ComputationalAsset:
        """
        Transforms the data from the infrastructure into a computational asset
        """
        return None