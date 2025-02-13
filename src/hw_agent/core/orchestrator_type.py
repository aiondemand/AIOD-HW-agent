# src/hw_agent/utils/orchestrator_types.py

from enum import Enum

class OrchestratorType(str, Enum):
    KUBERNETES = "kubernetes"
    OPENSTACK = "openstack"
    SLURM = "slurm"
    HPC = "hpc"
    # Add other orchestrator types as needed

    def __str__(self):
        return self.value