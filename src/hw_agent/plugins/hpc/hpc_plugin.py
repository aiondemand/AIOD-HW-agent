import os
import io
import paramiko
from dotenv import load_dotenv
import yaml

from hw_agent.core.base_plugin import BasePlugin
from hw_agent.core.plugin_context import PluginContext
from hw_agent.models.computational_models import ComputationalData
from hw_agent.models.computational_asset import ComputationalAsset, CPUProperties, MemoryProperties
from hw_agent.plugins.hpc.hpc_domain import ClustersInfo

# Load environment variables from .env file inside src/
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

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
        
        hpc_metadata = self._retrieve_hpc_metadata_via_ssh()
        self.logger.debug(f"HPC metadata (CPU info snippet): {hpc_metadata.get('cpu_info', '')[:100]}")
        
        cpu_info = hpc_metadata["cpu_info"]

        cpu_properties = [CPUProperties(
            num_cpu_cores   = cluster.cores_per_node,
            vendor          = cpu_info['vendor'],
            cpu_family      = cpu_info['cpu_family'],
            model           = cpu_info['cpu_model_name'],
            # i added these, as I had them and they were in the CPUProperties:
            architecture    = cpu_info['architecture'],
            clock_speed     = cpu_info['clock_speed'],
            
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

    def _retrieve_hpc_metadata_via_ssh(self) -> dict:
        """
        Connects via SSH to the HPC environment and retrieves data.
        Returns a dictionary with partial HPC metadata.
        """
        
        # ----- LOGIN -----
        
        login_node  = os.getenv("HPC_LOGIN_NODE")
        user        = os.getenv("HPC_USER")
        password    = os.getenv("HPC_PASSWORD")

        if not (login_node and user and password):
            self.logger.warning("SSH environment variables incomplete; skipping SSH retrieval.")
            return {"cpu_info": None, "parsed_cpu_properties": None}

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
            cpu_props = self._parse_lscpu_output(lscpu_output)

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