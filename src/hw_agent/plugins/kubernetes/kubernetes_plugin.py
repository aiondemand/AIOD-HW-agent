# src/hw_agent/plugins/kubernetes_plugin.py

from hw_agent.core.base_plugin import BasePlugin
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from hw_agent.core.plugin_context import PluginContext
from hw_agent.models.computational_models import ComputationalData
from hw_agent.models.computational_asset import ComputationalAsset, CPUProperties, MemoryProperties
from hw_agent.utils.logger import get_logger
from typing import Any, Dict

class KubernetesPlugin(BasePlugin):
    def __init__(self):
        super().__init__()

    def fetch_computational_data(self, plugin_context: PluginContext) -> ComputationalData:
        
        # Load kubeconfig from the provided data
        kubeconfig_data = plugin_context.get_connection_info("kubeconfig")
        
        if not kubeconfig_data:
            self.logger.error("Kubeconfig data is missing in the connection details.")
            raise ValueError("Kubeconfig data is required to connect to the Kubernetes cluster.")

        # Load kubeconfig from the provided data
        try:
            config.load_kube_config_from_dict(kubeconfig_data)
            self.logger.info("Successfully loaded kubeconfig.")
        except Exception as e:
            self.logger.error(f"Failed to load kubeconfig: {e}")
            raise

        # Initialize Kubernetes API client
        v1 = client.CoreV1Api()

        try:
            # Retrieve all nodes in the cluster
            nodes = v1.list_node()
            node_list = []

            for node in nodes.items:
                node_name = node.metadata.name
                labels = node.metadata.labels or {}
                self.logger.debug(f"Processing node: {node_name} with labels: {labels}")

                # Filter labels added by Node Feature Discovery
                nfd_labels = {
                    key: value
                    for key, value in labels.items()
                    if key.startswith('feature.node.kubernetes.io/')
                }

                node_info = {
                    "name": node_name,
                    "nfd_labels": nfd_labels,
                    "kernel_version": node.status.node_info.kernel_version,
                    "os_image": node.status.node_info.os_image,
                    "cpu_architecture": node.status.node_info.architecture,
                    "cpu_number": node.status.capacity.get("cpu", 0),
                    "cpu_vendor": node.metadata.labels.get("feature.node.kubernetes.io/cpu-model.vendor_id", ""),
                    "cpu_family": node.metadata.labels.get("feature.node.kubernetes.io/cpu-model.family", "")
                }
                node_list.append(node_info)

            self.logger.info(f"Retrieved hardware information from {len(node_list)} nodes.")

            computational_info = {
                "nodes": node_list
            }

            self.logger.info(f"{self.name}: Execution completed.")
            return computational_info

        except ApiException as e:
            self.logger.error(f"Exception when calling CoreV1Api->list_node: {e}")
            raise

    #def transform_computational_data(self, computational_data: ComputationalData) -> ComputationalAsset:
    #        return computational_data

    def transform_computational_data(self, computational_data: ComputationalData) -> ComputationalAsset:
        
        nodes = computational_data.computational_info["nodes"]
        cpu_properties = []
        for node in nodes:
            vendor = ""
            cpu_family = ""
            model = ""
            
            labels = node["nfd_labels"]
            
            # CPU properties
            if "feature.node.kubernetes.io/cpu-model.vendor_id" in labels:
                vendor = labels["feature.node.kubernetes.io/cpu-model.vendor_id"]
            if "feature.node.kubernetes.io/cpu-model.family" in labels:
                cpu_family = labels["feature.node.kubernetes.io/cpu-model.family"]  
            if "feature.node.kubernetes.io/cpu-model.model" in labels:
                model = labels["feature.node.kubernetes.io/cpu-model.model"]
            
            cpu_properties.append(
                CPUProperties(
                    vendor=vendor,
                    cpu_family=cpu_family,
                    model=model,
                    num_cpu_cores=int(node["cpu_number"])
            ))
            
            # Memory properties (this code does not work)
           # memory_properties = []
           # for memory in node["memory"]:
           #     memory_properties.append(
           #         MemoryProperties(
           #             model=memory["model"],
           #             vendor=memory["vendor"],
           #             amount=memory["amount"],
           #             type=memory["type"],
           #             read_bandwidth=memory["read_bandwidth"],
           #         )
           #     )
            
         
            
        computational_asset = ComputationalAsset(
            name=node["name"],
            cpu=cpu_properties
        )
        
                               
        return computational_asset
    
    
