import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.endpoints import router as api_router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Multilingual Context-Aware Conversational Dashboard Generation and Modification System"
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API endpoints first
app.include_router(api_router)

# Mount static directory for Plotly assets
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Mount production frontend build if available
dist_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
assets_dir = os.path.join(dist_dir, "assets")

if os.path.exists(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="frontend_assets")

if os.path.exists(dist_dir):
    # Mount public files like plotly.min.js and sample datasets from dist
    app.mount("/sample_datasets", StaticFiles(directory=os.path.join(dist_dir, "sample_datasets")), name="dist_sample_datasets")
    
    @app.get("/plotly.min.js")
    def get_plotly_js():
        plotly_path = os.path.join(dist_dir, "plotly.min.js")
        if os.path.exists(plotly_path):
            return FileResponse(plotly_path, media_type="application/javascript")
        return FileResponse(os.path.join(static_dir, "plotly.min.js"), media_type="application/javascript")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        # Don't hijack API or static routes
        if full_path.startswith("api/") or full_path.startswith("static/") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
            return None
        file_path = os.path.join(dist_dir, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(dist_dir, "index.html"))
else:
    @app.get("/")
    def root():
        return {
            "name": settings.APP_NAME,
            "version": settings.VERSION,
            "docs": "/docs",
            "api_health": "/api/health"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
