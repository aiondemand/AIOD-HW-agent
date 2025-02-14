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

        try:
            self.logger.info("Retrieving compute limits...")
            # quotas = conn.get_compute_quotas(project_domain_name)
            limits = conn.compute.get_limits()
            absolute_limits = limits.absolute
            self.logger.info("Compute limits retrieved successfully.")

            return absolute_limits

        except SDKException as e:
            self.logger.error(f"Error retrieving compute limits: {e}")
            raise

    def transform_computational_data(self, plugin_context: PluginContext, computational_data: ComputationalData) -> ComputationalAsset:
        
        asset_name = plugin_context.get_resource_metadata().name
        asset_contact = plugin_context.get_resource_metadata().contact
        asset_description = plugin_context.get_resource_metadata().description
        
        computational_info = computational_data.computational_info
        
        asset = ComputationalAsset(
            creator=[asset_contact],
            name=asset_name,
            contact=[asset_contact],
            id="1",
            os="",
            geographical_location="",
            description=Description(plain=asset_description),
            owner=asset_contact,
            pricing_schema="",
            underlying_orchestrating_technology=OrchestratorType.OPENSTACK,
            kernel="",
            cpu=[CPUProperties(num_cpu_cores=computational_info["total_cores"], architecture="x86_64", vendor="Intel", cpu_model_name="")],
            accelerator=[AcceleratorProperties(cores=256, architecture="NVIDIA", vendor="NVIDIA", acc_model_name="Tesla V100", type="GPU", memory=16)],
            network=NetworkProperties(latency=10.5, bandwith_Mbps=1000, topology="Star"),
            memory=[MemoryProperties(type="DDR4", amount_gb=computational_info["total_ram"])],
            storage=[StorageProperties(model="Samsung SSD", vendor="Samsung", amount=512, type="SSD", read_bandwidth=3500, write_bandwidth=3000)]
        )
        
        return asset 