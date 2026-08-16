import uvicorn

from .backend.infrastructure.server.server import create_application

app = create_application()

if __name__ == "__main__":
    uvicorn.run(app, host="localhost")
    