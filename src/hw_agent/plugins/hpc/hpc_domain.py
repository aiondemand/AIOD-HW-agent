from typing import Set

from pydantic import BaseModel, field_validator


class ClusterInfo(BaseModel):
    name: str
    node_count: int
    cores_per_node: int
    memory_per_node: int
    
    class Config:
        frozen = True

    @field_validator('name')
    def name_must_not_be_empty(cls, p):
        if not p:
            raise ValueError("cluster name cannot be empty")
        return p

    @field_validator('node_count')
    def node_count_must_not_be_empty(cls, p):
        if not p:
            raise ValueError("cluster node count cannot be empty")
        return p

    @field_validator('cores_per_node')
    def cores_per_node_must_not_be_empty(cls, p):
        if not p:
            raise ValueError("cluster cores per node cannot be empty")
        return p

    @field_validator('memory_per_node')
    def memory_per_node_must_not_be_empty(cls, p):
        if not p:
            raise ValueError("cluster memory per node cannot be empty")
        return p


class ClustersInfo(BaseModel):
    clusters: Set[ClusterInfo]

    @field_validator('clusters')
    def unique_identifiers(cls, clusters):
        cluster_names = [cluster.name for cluster in clusters]
        if len(set(cluster_names)) != len(cluster_names):
            raise ValueError("clusters must have unique names")
        return clusters

    @field_validator('clusters')
    def clusters_list_must_not_be_empty(cls, clusters):
        if not clusters:
            raise ValueError("clusters cannot be empty")
        return clusters


