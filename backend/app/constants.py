"""Constantes de la aplicación"""

# Modelos Gemini disponibles con soporte para File Search
AVAILABLE_MODELS = [
    {
        "id": "gemini-2.5-flash",
        "name": "Gemini 2.5 Flash",
        "description": "Rápido y económico, ideal para la mayoría de casos",
        "recommended": True,
    },
    {
        "id": "gemini-2.5-pro",
        "name": "Gemini 2.5 Pro",
        "description": "Más potente, mejor para tareas complejas",
        "recommended": False,
    },
    {
        "id": "gemini-2.0-flash-exp",
        "name": "Gemini 2.0 Flash (Experimental)",
        "description": "Versión experimental, puede cambiar",
        "recommended": False,
    },
    # Gemini 3.0 - Añadir cuando esté disponible
    # {
    #     "id": "gemini-3.0-flash",
    #     "name": "Gemini 3.0 Flash",
    #     "description": "Nueva generación (disponible próximamente)",
    #     "recommended": False,
    # },
]

# Modelo por defecto si no se especifica
DEFAULT_MODEL = "gemini-2.5-flash"

# IDs de modelos (para validación)
MODEL_IDS = [model["id"] for model in AVAILABLE_MODELS]
