from .mock_api import api as mock_api
from .real_api import api as real_api

# Default to mock API
api = mock_api

__all__ = ['api', 'mock_api', 'real_api']