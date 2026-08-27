from .api import create_app

# Production entry point – creates a single shared Store per process.
app = create_app()

