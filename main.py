import os

from backend.app import create_app

app = create_app()

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "127.0.0.1")
    is_dev = os.environ.get("ENV", "development").lower() == "development"
    print(f"🚀 Starting Tinhat FastAPI + Svelte 5 server at http://{host}:{port} (dev={is_dev})")
    uvicorn.run("main:app", host=host, port=port, reload=is_dev)
