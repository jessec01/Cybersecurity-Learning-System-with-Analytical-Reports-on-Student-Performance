import uvicorn
from infrastructure.server.server import create_application

if __name__ == "__main__":
    app = create_application()
    #arranque del programa
    uvicorn.run(app, host="localhost")
    