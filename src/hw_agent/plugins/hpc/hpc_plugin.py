# src/hw_agent/plugins/hpc_plugin.py
import os

import yaml

from hw_agent.core.base_plugin import BasePlugin
from hw_agent.core.plugin_context import PluginContext
from hw_agent.models.computational_models import ComputationalData
from hw_agent.models.computational_asset import ComputationalAsset, CPUProperties, MemoryProperties
from hw_agent.plugins.hpc.hpc_domain import ClustersInfo


class HPCPlugin(BasePlugin):
    def __init__(self):
        super().__init__()

    def fetch_computational_data(self, plugin_context: PluginContext) -> ComputationalData:
        clusters_info = self._read_static_info()
        self.logger.info(f"Retrieved hardware information from {len(clusters_info.clusters)} nodes.")

        computational_info = {
            "clusters": clusters_info
        }

        self.logger.info(f"{self.name}: fetch completed.")
        return ComputationalData(computational_info=computational_info)

    def transform_computational_data(self, computational_data: ComputationalData) -> ComputationalAsset:
        return self._cluster_to_node(computational_data)

    def _read_static_info(self) -> ClustersInfo:
        static_info_file = os.path.join(os.path.dirname(__file__), 'static_info.yaml')
        if not os.path.exists(static_info_file):
            self.logger.error(f"Static info file not found: {static_info_file}")
            raise FileNotFoundError(f"Static info file not found: {static_info_file}")
        self.logger.info(f"Using static info file: {static_info_file}")
        try:
            with open(static_info_file, 'r') as static_info:
                clusters_data = yaml.safe_load(static_info)
                return ClustersInfo(**clusters_data)
        except Exception as e:
            self.logger.error(f"Error parsing static info file: {static_info_file}: {e}")
            raise e

    def _cluster_to_node(self, cluster):
        node_name = cluster.name
        self.logger.debug(f"Processing node: {node_name}")

        cpu_properties = [CPUProperties(
            num_cpu_cores=cluster.cores_per_node,
            # TODO: Retrieve via ssh
            # vendor=None,
            # cpu_family=None,
            # model=None,
        )] * cluster.node_count

        memory_properties = [MemoryProperties(
            amount_gb=cluster.memory_per_node,
            # TODO: Retrieve via ssh
            # model=memory["model"],
            # vendor=memory["vendor"],
            # type=memory["type"],
            # read_bandwidth=memory["read_bandwidth"],
        )] * cluster.node_count


        computational_asset = ComputationalAsset(
            name=cluster.name,
            cpu=cpu_properties,
            memory=memory_properties
            # More properties: current load? available quota? accelerator?
        )

        return computational_asset
