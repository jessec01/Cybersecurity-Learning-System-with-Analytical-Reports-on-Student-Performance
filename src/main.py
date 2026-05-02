import uvicorn
from infrastructure.server.server import create_application

if __name__ == "__main__":
    app = create_application()
    uvicorn.run(app, host="localhost")
    