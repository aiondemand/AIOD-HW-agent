# src/hw_agent/api/catalogue_router.py

from fastapi import APIRouter, Depends, status
from hw_agent.models.computational_asset import ComputationalAsset
from hw_agent.services.catalogue_service import CatalogueService

router = APIRouter(prefix="/catalogue", tags=["Metadata Catalogue"])



def get_catalogue_service():
    return CatalogueService()

@router.get("/computational-assets/{asset_id}",  status_code=status.HTTP_200_OK,
            summary="Retrieve a computational asset from the Metadata Catalogue.")
def get_computational_asset(asset_id: str, catalogue_service: CatalogueService = Depends(get_catalogue_service)):
    return catalogue_service.get_computational_asset(asset_id)


@router.post("/computational-assets", status_code=status.HTTP_201_CREATED,
            summary="Post a computational asset to the Metadata Catalogue.")
def create_computational_asset(computational_asset: ComputationalAsset, catalogue_service: CatalogueService = Depends(get_catalogue_service)):
    return catalogue_service.create_computational_asset(computational_asset)


@router.get("/computational-assets", status_code=status.HTTP_200_OK,
            summary="Get all computational assets from the Metadata Catalogue.")
def get_all_computational_assets(catalogue_service: CatalogueService = Depends(get_catalogue_service)):
    return catalogue_service.get_all_computational_assets()