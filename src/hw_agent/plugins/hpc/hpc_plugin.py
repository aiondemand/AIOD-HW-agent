import os
import io
import base64
import paramiko
from dotenv import load_dotenv
import yaml

from hw_agent.core.base_plugin import BasePlugin
from hw_agent.core.plugin_context import PluginContext
from hw_agent.models.computational_models import ComputationalData
from hw_agent.models.computational_asset import Description, ComputationalAsset, CPUProperties, MemoryProperties
from hw_agent.plugins.hpc.hpc_domain import ClustersInfo
from typing import Any, Dict, List

# Load environment variables from .env file inside src/
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

class HPCPlugin(BasePlugin):
    def __init__(self):
        super().__init__()

    def fetch_computational_data(self, plugin_context: PluginContext) -> ComputationalData:
        clusters_info = self._read_static_info()
        self.logger.info(f"Retrieved hardware information from {len(clusters_info.clusters)} nodes.")
        
        ssh_credentials = plugin_context.get_connection_info('ssh_credentials')
        login_node      = ssh_credentials.get('login_node')
        user            = ssh_credentials.get('user')
        private_key     = ssh_credentials.get('private_key')
        
        ssh_data = self._retrieve_hpc_metadata_via_ssh(login_node, user, private_key)
        print(ssh_data)
        # self.logger.debug(f"HPC metadata (CPU info snippet): {hpc_metadata.get('cpu_info', '')[:100]}")
                
        computational_info = {
            "clusters": clusters_info,
            "ssh_data": ssh_data,
        }
        print(clusters_info)

        self.logger.info(f"{self.name}: fetch completed.")
        return computational_info

    def transform_computational_data(self, computational_data: ComputationalData) -> ComputationalAsset:
        # Transform the data from the plugin into the standard format for the AIOD catalog.
        clusters_info = computational_data.computational_info.get("clusters")
        ssh_data = computational_data.computational_info.get("ssh_data")
        
        if not clusters_info or not clusters_info.clusters:
            self.logger.error("No clusters found in computational data.")
            raise ValueError("No clusters available to transform.")
        
        cpu_properties: List[CPUProperties] = []
        memory_properties: List[MemoryProperties] = []
        cluster_names: List[str] = []
        
        print(ssh_data["cpu_info"]["clock_speed"])
        
        # Process one node per cluster for illustration purposes.
        for cluster in clusters_info.clusters:
            cluster_names.append(cluster.name)
            cpu_properties.append(
                CPUProperties(
                    num_cpu_cores   = cluster.cores_per_node,
                    vendor          = ssh_data["cpu_info"]["vendor"],
                    cpu_family      = ssh_data["cpu_info"]["cpu_family"],
                    cpu_model_name  = ssh_data["cpu_info"]["cpu_model_name"],
                    architecture    = ssh_data["cpu_info"]["architecture"],
                    clock_speed     = ssh_data["cpu_info"]["clock_speed"],
                )
            )
            memory_properties.append(
                MemoryProperties(
                    amount_gb=cluster.memory_per_node,
                    # TODO: Retrieve via ssh
                    # model=memory["model"],
                    # vendor=memory["vendor"],
                    # type=memory["type"],
                    # read_bandwidth=memory["read_bandwidth"],
                )
            )
        
        # Create a combined asset name from all cluster names or use a generic label.
        asset_name = ", ".join(cluster_names)
        
        print("*" * 100)
        computational_asset = ComputationalAsset(
            name=asset_name,
            id=1,
            geographical_location="",
            description=Description(plain="test"),
            os="",
            owner="",
            pricing_schema="",
            underlying_orchestrating_technology="",
            kernel="",
            cpu=cpu_properties,
            memory=memory_properties,
            accelerator=[],
            network=[],
            storage=[],
            # More properties: current load? available quota? accelerator?
        )
        return computational_asset
    
    ####################
    # HELPER FUNCTIONS #
    ####################

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


    def _retrieve_hpc_metadata_via_ssh(self, login_node, user, password_base64) -> dict:
        """
        Connects via SSH to the HPC environment and retrieves data.
        Returns a dictionary with partial HPC metadata.
        """
        
        # ----- LOGIN -----
        

        if not (login_node and user and password_base64):
            self.logger.warning("SSH environment variables incomplete; skipping SSH retrieval.")
            return {"cpu_info": None, "parsed_cpu_properties": None}
        
        password = base64.b64decode(password_base64)


        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        
        
        # ----- RETRIEVE DATA -----
        
        cpu_props = None
        # ...
        
        try:
            ssh_client.connect(
                hostname    = login_node,
                username    = user,
                password    = password,
                timeout     = 15
            )
            self.logger.info(f"SSH connected to {login_node}.")

            # 1. Get the data
            # cpu data:
            _, stdout, stderr   = ssh_client.exec_command("lscpu")
            lscpu_output        = stdout.read().decode("utf-8", errors="replace")

            # 2. Parse the data
            cpu_props = self._parse_ssh_cpu_properties(lscpu_output)

        except Exception as e:
            self.logger.error(f"SSH connection failed: {e}")
        finally:
            ssh_client.close()

        # We can maybe extend it in the future
        return {
            "cpu_info": cpu_props,
        }

    def _parse_ssh_cpu_properties(self, lscpu_output: str) -> dict:
        """
        Helper to parse the lscpu output lines.
            => Parse 'lscpu' output lines into a CPUProperties object.
        """
        data_map = {}
        for line in lscpu_output.splitlines():
            line_stripped = line.strip()
            if ":" in line_stripped:
                key, val = line_stripped.split(":", 1)
                key = key.strip()
                val = val.strip()
                data_map[key] = val

        clock_speed_val = data_map.get("CPU max MHz")
        clock_speed_str = f"{clock_speed_val} MHz" if clock_speed_val else None

        cores_str = data_map.get("CPU(s)", "0")
        try:
            total_cores = int(cores_str)
        except ValueError:
            total_cores = 0

        cache_l1d   = data_map.get("L1d")
        cache_l1i   = data_map.get("L1i")
        cache_l2    = data_map.get("L2")
        cache_l3    = data_map.get("L3")

        return {
            "num_cpu_cores" : total_cores,
            "architecture"  : data_map.get("Architecture"),
            "vendor"        : data_map.get("Vendor ID"),
            "cpu_model_name": data_map.get("Model name"),
            "cpu_family"    : data_map.get("CPU family"),
            "clock_speed"   : clock_speed_str,

            # Not yet implemented:
            # "cache_L1_D"  : cache_l1d if cache_l1d else None,
            # "cache_L1_I"  : cache_l1i if cache_l1i else None,
            # "cache_L2"    : cache_l2 if cache_l2 else None,
            # "cache_L3"    : cache_l3 if cache_l3 else None
        }