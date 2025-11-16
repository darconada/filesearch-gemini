"""Servicio para gestión de File Search Stores"""
from typing import Optional
from app.models.store import StoreCreate, StoreResponse, StoreList
from app.services.google_client import google_client
import logging

logger = logging.getLogger(__name__)


class StoreService:
    """Servicio para operaciones con stores"""

    def __init__(self):
        self.google_client = google_client

    def create_store(self, store_data: StoreCreate) -> StoreResponse:
        """Crear un nuevo File Search store"""
        try:
            client = self.google_client.get_client()

            # Crear el store usando el nuevo SDK
            store = client.file_search_stores.create(display_name=store_data.display_name)

            logger.info(f"Store created: {store.name}")

            return StoreResponse(
                name=store.name,
                display_name=store.display_name,
                create_time=getattr(store, 'create_time', None),
                update_time=getattr(store, 'update_time', None)
            )
        except Exception as e:
            logger.error(f"Error creating store: {e}")
            raise

    def list_stores(self, page_size: int = 50, page_token: Optional[str] = None) -> StoreList:
        """Listar stores disponibles"""
        try:
            client = self.google_client.get_client()

            # Listar stores usando el nuevo SDK
            config = {"page_size": page_size}
            if page_token:
                config["page_token"] = page_token

            stores_response = client.file_search_stores.list(**config)

            stores = []
            next_token = None

            # Procesar stores
            for store in stores_response:
                stores.append(StoreResponse(
                    name=store.name,
                    display_name=store.display_name,
                    create_time=getattr(store, 'create_time', None),
                    update_time=getattr(store, 'update_time', None)
                ))

            # Obtener next_page_token si existe
            if hasattr(stores_response, 'next_page_token'):
                next_token = stores_response.next_page_token

            logger.info(f"Listed {len(stores)} stores")

            return StoreList(stores=stores, next_page_token=next_token)

        except Exception as e:
            logger.error(f"Error listing stores: {e}")
            raise

    def get_store(self, store_id: str) -> StoreResponse:
        """Obtener un store por ID"""
        try:
            client = self.google_client.get_client()

            store = client.file_search_stores.get(name=store_id)

            return StoreResponse(
                name=store.name,
                display_name=store.display_name,
                create_time=getattr(store, 'create_time', None),
                update_time=getattr(store, 'update_time', None)
            )
        except Exception as e:
            logger.error(f"Error getting store {store_id}: {e}")
            raise

    def delete_store(self, store_id: str) -> dict:
        """Eliminar un store"""
        try:
            client = self.google_client.get_client()

            # Eliminar con force=True para borrar todos los documentos
            client.file_search_stores.delete(name=store_id, force=True)

            logger.info(f"Store deleted: {store_id}")

            return {"success": True, "message": f"Store {store_id} deleted successfully"}
        except Exception as e:
            logger.error(f"Error deleting store {store_id}: {e}")
            raise


# Instancia global del servicio
store_service = StoreService()
