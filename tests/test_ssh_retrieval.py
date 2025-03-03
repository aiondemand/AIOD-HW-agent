import os
import paramiko
import re

from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import List, Optional
    
def _retrieve_hpc_metadata_via_ssh() -> dict:
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
        # self.logger.info(f"SSH connected to {login_node}.")

        # 1. Get the data
        # cpu data:
        _, stdout, stderr   = ssh_client.exec_command("lscpu")
        lscpu_output        = stdout.read().decode("utf-8", errors="replace")

        # 2. Parse the data
        cpu_props = _parse_ssh_cpu_properties(lscpu_output)

    except Exception as e:
        print("error")
        # self.logger.error(f"SSH connection failed: {e}")
    finally:
        ssh_client.close()

    # We can maybe extend it in the future
    return {
        "cpu_info": cpu_props,
    }


def _parse_ssh_cpu_properties(lscpu_output: str) -> dict:
    """
    Helper to parse the lscpu output lines.
        => Parse 'lscpu' output lines into a dictionary.
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


# **Test Case**
if __name__ == "__main__":
    result = _retrieve_hpc_metadata_via_ssh()

    print("\nParsed CPU Metadata:")
    print(result["cpu_info"])
