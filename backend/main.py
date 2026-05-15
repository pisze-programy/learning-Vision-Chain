from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from routers import upload

app = FastAPI()
app.mount("/assets", StaticFiles(directory="../static/assets"), name="assets")
app.include_router(upload.router, prefix="/api")

@app.get("/{full_path:path}")
async def serve_react_app():
    return FileResponse("../static/index.html")