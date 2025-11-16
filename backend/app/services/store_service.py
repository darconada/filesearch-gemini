"""Servicio para gestión de File Search Stores"""
import google.generativeai as genai
from typing import Optional, List
from app.models.store import StoreCreate, StoreResponse, StoreList
from app.services.google_client import google_client
import logging

logger = logging.getLogger(__name__)


class StoreService:
    """Servicio para operaciones con stores"""

    def __init__(self):
        self.client = google_client

    def create_store(self, store_data: StoreCreate) -> StoreResponse:
        """Crear un nuevo File Search store"""
        try:
            if not self.client.is_configured():
                self.client.configure()

            # Crear el store
            store = genai.create_file_search_store(display_name=store_data.display_name)

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
            if not self.client.is_configured():
                self.client.configure()

            # Listar stores
            kwargs = {"page_size": page_size}
            if page_token:
                kwargs["page_token"] = page_token

            stores_page = genai.list_file_search_stores(**kwargs)

            stores = []
            next_token = None

            # Procesar stores
            for store in stores_page:
                stores.append(StoreResponse(
                    name=store.name,
                    display_name=store.display_name,
                    create_time=getattr(store, 'create_time', None),
                    update_time=getattr(store, 'update_time', None)
                ))

            # Obtener next_page_token si existe
            if hasattr(stores_page, 'next_page_token'):
                next_token = stores_page.next_page_token

            logger.info(f"Listed {len(stores)} stores")

            return StoreList(stores=stores, next_page_token=next_token)

        except Exception as e:
            logger.error(f"Error listing stores: {e}")
            raise

    def get_store(self, store_id: str) -> StoreResponse:
        """Obtener un store por ID"""
        try:
            if not self.client.is_configured():
                self.client.configure()

            store = genai.get_file_search_store(name=store_id)

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
            if not self.client.is_configured():
                self.client.configure()

            # Eliminar con force=True para borrar todos los documentos
            genai.delete_file_search_store(name=store_id, force=True)

            logger.info(f"Store deleted: {store_id}")

            return {"success": True, "message": f"Store {store_id} deleted successfully"}
        except Exception as e:
            logger.error(f"Error deleting store {store_id}: {e}")
            raise


# Instancia global del servicio
store_service = StoreService()
