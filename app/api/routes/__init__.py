"""
The `routes` module is responsible for setting up HTTP routes on the API Flask
blueprint.

Each module imported below will configure the API blueprint automatically on import.
"""

from app.api.routes import api_key
from app.api.routes import categories
from app.api.routes import languages
from app.api.routes import resource_retrieval
from app.api.routes import resource_updating
from app.api.routes import resource_voting
from app.api.routes import searching
