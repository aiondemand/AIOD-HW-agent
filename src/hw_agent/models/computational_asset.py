
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import List, Optional

class Description(BaseModel):
    plain: str = ""
    html: str = ""

class AiodEntry(BaseModel):
    editor: List[str]
    status: str

class Resource(BaseModel):
    platform: Optional[str] = None
    platform_resource_identifier: Optional[str] = None
    name: str
    date_published: Optional[datetime] = None
    same_as: Optional[HttpUrl] = None
    is_accessible_for_free: Optional[bool] = None
    version: Optional[str] = None
    status_info: Optional[HttpUrl] = None
    aiod_entry: Optional[AiodEntry] = None
    alternate_name: Optional[List[str]] = []
    application_area: Optional[List[str]] = []
    citation: Optional[List[str]] = []
    contact: Optional[List[str]] = []
    creator: Optional[List[str]] = []
    description: Optional[Description] = None
    distribution: Optional[List[str]] = []
    has_part: Optional[List[str]] = []
    industrial_sector: Optional[List[str]] = []
    is_part_of: Optional[List[str]] = []
    keyword: Optional[List[str]] = []
    license: Optional[HttpUrl] = None
    media: Optional[List[str]] = []
    note: Optional[List[str]] = []
    relevant_link: Optional[List[HttpUrl]] = []
    relevant_resource: Optional[List[str]] = []
    relevant_to: Optional[List[str]] = []
    research_area: Optional[List[str]] = []
    scientific_domain: Optional[List[str]] = []
    type: Optional[str] = None


class CPUProperties(BaseModel):
    # num_cpu: Optional[int] = None
    num_cpu_cores: int
    architecture: Optional[str] = None
    vendor: Optional[str] = None
    cpu_model_name: Optional[str] = None
    cpu_family: Optional[str] = None
    clock_speed: Optional[str] = None # Clock speed could be a string to include units, e.g., "3.5 GHz"
    # cache_L1: Optional[int] = None 
    # cache_L2: Optional[int] = None
    # cache_L3: Optional[int] = None
    # cache_L1_D: Optional[int] = None # L1 Data cache
    # cache_L1_I: Optional[int] = None # L1 Instruction cache


class AcceleratorProperties(BaseModel):
    cores: Optional[int] = None
    architecture: Optional[str] = None
    vendor: Optional[str] = None
    acc_model_name: Optional[str] = None
    type: Optional[str] = None  # This could be GPU, TPU, FPGA, etc.
    # computation_framework_supported: List[str]  # E.g., CUDA, OpenCL
    memory: Optional[int]  # Memory size in gigabytes

class NetworkProperties(BaseModel):
    latency: Optional[float] = None # Latency in milliseconds
    bandwith_Mbps: Optional[float] = None  # Bandwidth in Megabits per second
    topology: Optional[str] = None

class MemoryProperties(BaseModel):
    type: Optional[str] = None  # Type of memory, e.g., DDR4, GDDR6, HBM
    amount_gb: Optional[int] = None # Size of memory in gigabytes
    read_bandwidth: Optional[float] = None  # Memory bandwidth in gigabytes per second
    write_bandwidth: Optional[float] = None  # Memory bandwidth in gigabytes per second
    rdma: Optional[bool] = None  # Indicates if RDMA is supported

class StorageProperties(BaseModel):
    model: Optional[str] = None
    vendor: Optional[str] = None
    amount: Optional[int] = None # Capacity of storage in gigabytes
    type: Optional[str] = None  # Type of storage, e.g., SSD, HDD, NVMe
    read_bandwidth: Optional[int] = None # Read bandwidth in Megabytes per second
    write_bandwidth: Optional[int] = None # Write bandwidth in Megabytes per second
    # data_transfer_mechanisms: List[str]  # List of supported data transfer mechanisms, e.g., SATA, SAS, PCIe

class AddressProperties(BaseModel):
    region: Optional[str] = None  # Region or state
    locality: Optional[str] = None  # City or town
    street: Optional[str] = None  # Street address
    postal_code: Optional[str] = None  # Postal or ZIP code
    address: Optional[str] = None  # Full address as a single string
    country: Optional[str] = None  # Country code (assuming ISO format)

class GeoProperties(BaseModel):
    latitude: float = 0  # Latitude in degrees
    longitude: float = 0  # Longitude in degrees
    elevation_millimeters: Optional[int] = 0  # Elevation in millimeters

class LocationProperties(BaseModel):
    address: Optional[AddressProperties] = None
    geo: Optional[GeoProperties] = None

class ComputationalAsset(Resource):
    id: Optional[int] = None
    geographical_location: Optional[str] = None # Country, Region, City, etc. ?
    description: Optional[Description] = None
    os: Optional[str] = None
    owner: Optional[str] = None 
    pricing_scheme: Optional[str] = None
    underlying_orchestrating_technology: Optional[str] = None # OpenStack, Kubernetes, Mesos, etc.
    kernel: Optional[str] = None # Kernel version?
    cpu: Optional[List[CPUProperties]] = None
    accelerator: Optional[List[AcceleratorProperties]] = []
    # network: Optional[NetworkProperties] = None
    memory: Optional[List[MemoryProperties]] = []
    storage: Optional[List[StorageProperties]] = []
    location: Optional[List[LocationProperties]] = []


