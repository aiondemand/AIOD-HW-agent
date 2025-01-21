# src/hw_agent/api/computational_data_router.py

from typing import Any, Dict
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from hw_agent.core.broker import Broker
from hw_agent.models.computational_models import ComputationalData
from hw_agent.models.computational_asset import ComputationalAsset

router = APIRouter(tags=["Infrastructure Information"])


def get_broker_service() -> Broker:
    return Broker()


@router.get("/computational-assets/{config_id}", response_model=ComputationalAsset, status_code=status.HTTP_200_OK,
            summary="Retrieve a computational asset transformed using the specified configuration ID.")
def get_computational_asset(config_id: str, broker_service: Broker = Depends(get_broker_service)):
    """
    ## Retrieve Computational Asset

    Fetch a computational asset based on the provided configuration ID. The configuration contain data to connect to the infrastructure.

    - **Parameters**:
        - **config_id** (*str*): The unique identifier for the configuration.
    - **Returns**:
        - A `ComputationalAsset` object containing the requested data that must be aligned with the Metadata Catalogue. 

    
    **Notes**:
    - The `config_id` is the unique identifier for the configuration.
    - The `ComputationalAsset` object contains mormalized data from multiple orchestrators.
    """
    
    return broker_service.fetch_and_transform(config_id)


@router.get("/computational-data/{config_id}", response_model=ComputationalData, status_code=status.HTTP_200_OK,
            summary="Retrieve computational data using the specified configuration ID")
def get_computational_data(config_id: str, broker_service: Broker = Depends(get_broker_service)) -> ComputationalData:  
    """
    ## Retrieve Computational Data

    Fetch raw computational data based on the provided configuration ID.

    - **Parameters**:
        - **config_id** (*str*): The unique identifier for the configuration.
    - **Returns**:
        - A `ComputationalData` object containing the requested data. ComputationalData contains data from multiple orchestrators.

    **Example**:

    ```bash
    curl -X GET "http://localhost:8000/computational-data/12345" -H "accept: application/json"
    ```

    **Notes**:

    - The data returned is unprocessed and may require further handling.
    - Use this endpoint when you need access to the raw computational results.
    """
    
    return broker_service.fetch_computational_data(config_id)
