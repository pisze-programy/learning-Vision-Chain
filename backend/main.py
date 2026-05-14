from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
app = FastAPI()

@app.post("/api/upload")
async def upload_image():
    return {
        "status": "OK"
    }

app.mount("/assets", StaticFiles(directory="../static/assets"), name="assets")
@app.get("/{full_path:path}")
async def serve_react_app():
    return FileResponse("../static/index.html")