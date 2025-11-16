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
            store = client.file_search_stores.create(
                config={"displayName": store_data.display_name}
            )

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

    def list_stores(self, page_size: int = 20, page_token: Optional[str] = None) -> StoreList:
        """Listar stores disponibles"""
        try:
            client = self.google_client.get_client()

            # Listar stores usando el nuevo SDK (sintaxis correcta)
            # IMPORTANTE: pageSize en camelCase, dentro de config dict
            config_dict = {"pageSize": page_size}
            if page_token:
                config_dict["pageToken"] = page_token

            # El método list() retorna un pager
            pager = client.file_search_stores.list(config=config_dict)

            stores = []
            next_token = None

            # Procesar stores desde el pager
            for store in pager.page:
                stores.append(StoreResponse(
                    name=store.name,
                    display_name=store.display_name,
                    create_time=getattr(store, 'create_time', None),
                    update_time=getattr(store, 'update_time', None)
                ))

            # Obtener next_page_token si hay más páginas
            if hasattr(pager, 'next_page_token') and pager.next_page_token:
                next_token = pager.next_page_token

            logger.info(f"Listed {len(stores)} stores")

            return StoreList(stores=stores, next_page_token=next_token)

        except Exception as e:
            logger.error(f"Error listing stores: {e}")
            raise

    def get_store(self, store_id: str) -> StoreResponse:
        """Obtener un store por ID - Nota: get() puede no estar disponible, usamos list()"""
        try:
            client = self.google_client.get_client()

            # El SDK puede no tener get(), intentamos listar y buscar
            pager = client.file_search_stores.list(config={"pageSize": 20})

            for store in pager.page:
                if store.name == store_id:
                    return StoreResponse(
                        name=store.name,
                        display_name=store.display_name,
                        create_time=getattr(store, 'create_time', None),
                        update_time=getattr(store, 'update_time', None)
                    )

            # Si no lo encontramos, lanzar 404
            raise ValueError(f"Store {store_id} not found")

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
