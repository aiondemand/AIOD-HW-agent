# hw_agent/plugins/openstack/openstack_plugin.py

from hw_agent.core.base_plugin import BasePlugin
from hw_agent.core.orchestrator_type import OrchestratorType
from hw_agent.core.plugin_context import PluginContext
from openstack import connection
from openstack.exceptions import SDKException
from hw_agent.models.computational_asset import Description, ComputationalAsset, CPUProperties, MemoryProperties, StorageProperties, NetworkProperties, AcceleratorProperties
from hw_agent.models.computational_models import ComputationalData
from hw_agent.utils.logger import get_logger
from typing import Any, Dict

class OpenStackPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.name = "OpenStack Plugin"
        self.logger = get_logger(self.name)

    def fetch_computational_data(self, plugin_context: PluginContext) -> Dict[str, Any]:

        # TODO: Build a model for this as a responsability of the plugin
        # Retrieve connection details from the context
        auth_url = plugin_context.get_connection_info('auth_url')
        username = plugin_context.get_connection_info('username')
        password = plugin_context.get_connection_info('password')
        project_name = plugin_context.get_connection_info('project_name')
        user_domain_name = plugin_context.get_connection_info('user_domain_name', 'Default')
        project_domain_name = plugin_context.get_connection_info('project_domain_name', 'Default')
        region_name = plugin_context.get_connection_info('region_name', 'RegionOne')

        if not auth_url or not username or not password or not project_name:
            self.logger.error("Missing required connection details for OpenStack.")
            raise ValueError("Connection details are required for OpenStack plugin.")

        # Establish connection to OpenStack
        try:
            socket_timeout = self.plugin_definition.get_config_value('client_socket_timeout', 20)
            conn = connection.Connection(
                auth_url=auth_url,
                username=username,
                password=password,
                project_name=project_name,
                user_domain_name=user_domain_name,
                project_domain_name=project_domain_name,
                region_name=region_name,
                verify=False,
                client_socket_timeout=socket_timeout # Adjust as necessary for SSL verification
            )
            
            
            self.logger.info("Successfully connected to OpenStack.")
        except SDKException as e:
            self.logger.error(f"Failed to connect to OpenStack: {e}")
            raise

        # Retrieve Openstack data            
        try:
            data = {}
        
            try:
                self.logger.info("Retrieving compute limits...")
                limits = conn.compute.get_limits()
                absolute_limits = limits.absolute
                data["limits"] = absolute_limits
                self.logger.info("Compute limits retrieved successfully.")
            except SDKException as e:
                self.logger.warning(f"Unable to fetch compute limits: {e}")
                data["limits"] = {}

            try:
                self.logger.info("Retrieving hypervisors...")
                hypervisors = list(conn.compute.hypervisors())
                data["hypervisors"] = hypervisors
                self.logger.info("Hypervisors retrieved successfully.")
            except SDKException as e:
                self.logger.warning(f"Unable to fetch hypervisors: {e}")
                data["hypervisors"] = []
            
            return data

        except SDKException as e:
            self.logger.error(f"Error retrieving OpenStack data: {e}")
            raise

    def transform_computational_data(self, computational_data: ComputationalData) -> ComputationalAsset:
        computational_info = computational_data.computational_info
        plugin_info = computational_data.metadata.plugin_definition
        cpu_properties = []
        memory_properties = []
        storage_properties = []
                
        for hypervisor in computational_info.get("hypervisors", []):
            try:
                cpu_info = hypervisor.cpu_info
                if isinstance(cpu_info, str):
                    import json
                    cpu_info = json.loads(cpu_info)
                    
                num_sockets = cpu_info.get("topology", {}).get("sockets", 1)
                cores_per_socket = cpu_info.get("topology", {}).get("cores", 1)
                
                for _ in range(num_sockets):
                    cpu_properties.append(CPUProperties(
                        num_cpu_cores=cores_per_socket,
                        vendor=cpu_info.get("vendor"),
                        cpu_model_name=cpu_info.get("model"),
                        architecture=cpu_info.get("arch"),
                        clock_speed=f"{cpu_info.get('frequency', '')} MHz" if cpu_info.get('frequency') else None
                    ))        
            except Exception as e:
                self.logger.warning(f"Error processing CPU info for hypervisor: {e}")
                cpu_properties.append(CPUProperties(
                    num_cpu_cores=hypervisor.vcpus
                ))
                
            try:
                memory_gb = getattr(hypervisor, 'memory_mb', 0) // 1024
                memory_properties.append(MemoryProperties(
                    amount_gb=memory_gb,
                    type="RAM"
                ))
                self.logger.debug(f"Successfully processed memory information for hypervisor {hypervisor.id}")
            except AttributeError as e:
                self.logger.warning(f"Unable to process memory information for hypervisor: {e}")
                memory_properties.append(MemoryProperties(amount_gb=0))

            try:
                storage_properties.append(StorageProperties(
                    amount=getattr(hypervisor, 'local_gb', 0),
                ))
                self.logger.debug(f"Successfully processed storage information for hypervisor {hypervisor.id}")
            except AttributeError as e:
                self.logger.warning(f"Unable to process storage information for hypervisor: {e}")
                storage_properties.append(StorageProperties(amount=0))

        try:
            asset = ComputationalAsset(
                name=plugin_info.name or "OpenStack Cluster",
                geographical_location=computational_info.get("region_name", ""),
                description=Description(
                    plain=f"OpenStack cluster",
                    html=f"<p>OpenStack cluster</p>"
                ),
                owner=plugin_info.get_config_value("project_name", ""),
                pricing_scheme="",
                underlying_orchestrating_technology="OpenStack",
                cpu=cpu_properties,
                memory=memory_properties,
                storage=storage_properties
            )
            
            self.logger.info("Successfully transformed computational data into asset")
            return asset
            
        except Exception as e:
            self.logger.error(f"Error creating ComputationalAsset: {e}")
            return ComputationalAsset(
                name="OpenStack Cluster (Minimal)",
                cpu=[CPUProperties(num_cpu_cores=0)]
            )