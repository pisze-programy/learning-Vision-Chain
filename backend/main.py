from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from routers.agents.router import router as agents_router
from routers.upload import router as upload_router

app = FastAPI()
app.mount("/assets", StaticFiles(directory="../static/assets"), name="assets")
app.include_router(upload_router, prefix="/api")
app.include_router(agents_router, prefix="/api")

@app.get("/{full_path:path}")
async def serve_react_app():
    return FileResponse("../static/index.html")