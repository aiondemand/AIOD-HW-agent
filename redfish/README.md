# DMTF Redfish example implementation
This folder includes examples on how to collect HW info using [DMTF Redfish standard] (https://www.dmtf.org/standards/redfish) in a python program.

## Installation
In order to use redfish in a python program, the redfish library needs to be installed:

__*pip install redfish*__

## Run the script
The Python script takes 3 positional arguments:
__url user password__

Where __url__ is the redfish url (e.g., `https://172.20.20.20`), __user__ is the admin user for redfish (e.g. Administrator), and __password__ is the admin user password (e.g. LMDT64WK)

## Example run command:
`python redfish-get-cpu-info.py https://172.20.20.20 Administrator LMDT64WK`

When I run this on my HPE Gen 10 server I get this json formatted output (Note that even more details about the server is available using Redfish, this is just an example and names on attributes can be changed to conform with the meta data model under construction):
```
{
    "CPUs": {
        "TotalCores": 56,
        "TotalThreads": 112,
        "CPUs": [
            {
                "Model": "Intel(R) Xeon(R) Gold 6238R CPU @ 2.20GHz",
                "ProcessorArchitecture": "x86",
                "InstructionSet": "x86-64",
                "VendorId": "N/A",
                "CoresEnabled": "N/A",
                "TotalCores": 28,
                "TotalThreads": 56
            },
            {
                "Model": "Intel(R) Xeon(R) Gold 6238R CPU @ 2.20GHz",
                "ProcessorArchitecture": "x86",
                "InstructionSet": "x86-64",
                "VendorId": "N/A",
                "CoresEnabled": "N/A",
                "TotalCores": 28,
                "TotalThreads": 56
            }
        ]
    },
    "Memory": {
        "TotalMemoryGB": 256.0,
        "MemoryModules": [
            {
                "Id": "proc1dimm3",
                "Name": "proc1dimm3",
                "MemoryType": "DRAM",
                "MemoryDeviceType": "DDR4",
                "CapacityMiB": 32768,
                "MaxOperatingSpeedMTs": 2933,
                "Manufacturer": "HPE",
                "SerialNumber": "F2AFBEC6"
            },
            {
                "Id": "proc1dimm5",
                "Name": "proc1dimm5",
                "MemoryType": "DRAM",
                "MemoryDeviceType": "DDR4",
                "CapacityMiB": 32768,
                "MaxOperatingSpeedMTs": 2933,
                "Manufacturer": "HPE",
                "SerialNumber": "F2AFC80E"
            },
            {
                "Id": "proc1dimm8",
                "Name": "proc1dimm8",
                "MemoryType": "DRAM",
                "MemoryDeviceType": "DDR4",
                "CapacityMiB": 32768,
                "MaxOperatingSpeedMTs": 2933,
                "Manufacturer": "HPE",
                "SerialNumber": "F2AFBEC7"
            },
            {
                "Id": "proc1dimm10",
                "Name": "proc1dimm10",
                "MemoryType": "DRAM",
                "MemoryDeviceType": "DDR4",
                "CapacityMiB": 32768,
                "MaxOperatingSpeedMTs": 2933,
                "Manufacturer": "HPE",
                "SerialNumber": "F2AFBEC8"
            },
            {
                "Id": "proc2dimm3",
                "Name": "proc2dimm3",
                "MemoryType": "DRAM",
                "MemoryDeviceType": "DDR4",
                "CapacityMiB": 32768,
                "MaxOperatingSpeedMTs": 2933,
                "Manufacturer": "HPE",
                "SerialNumber": "F2AFC301"
            },
            {
                "Id": "proc2dimm5",
                "Name": "proc2dimm5",
                "MemoryType": "DRAM",
                "MemoryDeviceType": "DDR4",
                "CapacityMiB": 32768,
                "MaxOperatingSpeedMTs": 2933,
                "Manufacturer": "HPE",
                "SerialNumber": "F2AFC308"
            },
            {
                "Id": "proc2dimm8",
                "Name": "proc2dimm8",
                "MemoryType": "DRAM",
                "MemoryDeviceType": "DDR4",
                "CapacityMiB": 32768,
                "MaxOperatingSpeedMTs": 2933,
                "Manufacturer": "HPE",
                "SerialNumber": "F2AFC194"
            },
            {
                "Id": "proc2dimm10",
                "Name": "proc2dimm10",
                "MemoryType": "DRAM",
                "MemoryDeviceType": "DDR4",
                "CapacityMiB": 32768,
                "MaxOperatingSpeedMTs": 2933,
                "Manufacturer": "HPE",
                "SerialNumber": "F2AFBDC9"
            }
        ]
    },
    "Storage": {
        "TotalStorageCapacityGB": 4000,
        "DiskDrives": [
            {
                "Id": "0",
                "Name": "HpeSmartStorageDiskDrive",
                "Model": "MM2000JEFRC",
                "CapacityGB": 2000,
                "BlockSizeBytes": 512,
                "InterfaceSpeedMbps": 12000,
                "RotationalSpeedRpm": 7200,
                "MediaType": "HDD",
                "SerialNumber": "W4633667"
            },
            {
                "Id": "1",
                "Name": "HpeSmartStorageDiskDrive",
                "Model": "MM2000JEFRC",
                "CapacityGB": 2000,
                "BlockSizeBytes": 512,
                "InterfaceSpeedMbps": 12000,
                "RotationalSpeedRpm": 7200,
                "MediaType": "HDD",
                "SerialNumber": "W46336E1"
            }
        ]
    }
}
```
