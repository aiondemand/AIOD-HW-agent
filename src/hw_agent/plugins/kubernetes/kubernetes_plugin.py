# src/hw_agent/plugins/kubernetes_plugin.py

from hw_agent.core.base_plugin import BasePlugin
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from hw_agent.core.plugin_context import PluginContext
from hw_agent.models.computational_models import ComputationalData
from hw_agent.models.computational_asset import ComputationalAsset, CPUProperties, MemoryProperties, StorageProperties, Description
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
        data = {}

        try:
            self.logger.info("Retrieving nodes information...")
            nodes = v1.list_node()
            data["nodes"] = nodes.items
            self.logger.info("Nodes retrieved successfully.")
        except ApiException as e:
            self.logger.warning(f"Unable to fetch nodes: {e}")
            data["nodes"] = []
            
        return data

    def transform_computational_data(self, computational_data: ComputationalData) -> ComputationalAsset:
        try:
            computational_info = computational_data.computational_info
            plugin_info = computational_data.metadata.plugin_definition
            cpu_properties = []
            memory_properties = []
            storage_properties = []

            for node in computational_info.get("nodes", []):
                capacity = node.status.capacity
                node_info = node.status.node_info
                cpu_info = {}

                # Process CPU information
                try:
                    labels = node.metadata.labels
                    nfd_labels = {
                        "vendor": labels.get("feature.node.kubernetes.io/cpu-model.vendor_id", ""),
                        "model": labels.get("feature.node.kubernetes.io/cpu-model.model", ""),
                        "family": labels.get("feature.node.kubernetes.io/cpu-model.family", "")
                    }

                    if not any(nfd_labels.values()):
                        self.logger.info("NFD labels not found, using system info")
                        cpu_model = node_info.cpu_model_name if hasattr(node_info, 'cpu_model_name') else ""
                        if "Intel" in cpu_model:
                            cpu_info["vendor"] = "Intel"
                        elif "AMD" in cpu_model:
                            cpu_info["vendor"] = "AMD"
                        
                        cpu_info["model"] = cpu_model
                    else:
                        cpu_info = nfd_labels

                    cpu_properties.append(CPUProperties(
                        num_cpu_cores=int(capacity.get("cpu", 0)),
                        architecture=node_info.architecture,
                        vendor=cpu_info.get("vendor", ""),
                        cpu_model_name=cpu_info.get("model", ""),
                        cpu_family=cpu_info.get("family", "")
                    ))
                    self.logger.debug(f"Successfully processed CPU information for node {node.metadata.name}")
                except Exception as e:
                    self.logger.warning(f"Unable to process CPU information for node: {e}")

                # Process Memory information
                try:
                    memory_kb = capacity.get("memory", "0Ki")
                    memory_gb = self._convert_k8s_memory_to_gb(memory_kb)
                    memory_properties.append(MemoryProperties(
                        amount_gb=round(memory_gb),
                        type="RAM"
                    ))
                    self.logger.debug(f"Successfully processed memory information for node {node.metadata.name}")
                except Exception as e:
                    self.logger.warning(f"Unable to process memory information for node: {e}")
                    
                # Process Storage information
                try:
                    storage_bytes = capacity.get('ephemeral-storage', '0Gi')
                    storage_gb = self._convert_k8s_storage_to_gb(storage_bytes)
                    storage_properties.append(StorageProperties(
                        amount=round(storage_gb),
                    ))
                except Exception as e:
                    self.logger.warning(f"Unable to process storage information for node: {e}")


            description = plugin_info.documentation.description or "Kubernetes cluster"
            asset = ComputationalAsset(
                name=plugin_info.name or "Kubernetes Cluster",
                description=Description(
                    plain=description,
                    html="<p>"+description+"</p>"
                ),
                owner=plugin_info.get_config_value("project_name", ""),
                pricing_scheme="",
                underlying_orchestrating_technology="Kubernetes",
                cpu=cpu_properties,
                memory=memory_properties,
                storage=storage_properties
            )
            
            self.logger.info("Successfully transformed computational data into asset")
            return asset

        except Exception as e:
            self.logger.error(f"Error creating ComputationalAsset: {e}")

    def _convert_k8s_memory_to_gb(self, memory_str: str) -> float:
        """Convert Kubernetes memory string (e.g., '16Gi', '1000Ki') to GB"""
        try:
            import re
            number = float(re.match(r'(\d+)', memory_str).group(1))
            unit = re.search(r'([A-Za-z]+)', memory_str).group(1)
            
            conversions = {
                'Ki': lambda x: x / (1024 * 1024),
                'Mi': lambda x: x / 1024,
                'Gi': lambda x: x,
                'Ti': lambda x: x * 1024
            }
            
            return conversions.get(unit, lambda x: x)(number)
        except Exception:
            return 0
            
    def _convert_k8s_storage_to_gb(self, storage_str: str) -> float:
        """Convert Kubernetes storage string to GB"""
        return self._convert_k8s_memory_to_gb(storage_str)
