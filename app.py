from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn
from routes import user_routes, contest_routes, unified_routes
from models.templates import html_template
from config import Config

app = FastAPI(
    title=Config.TITLE,
    description=Config.DESCRIPTION,
    version=Config.VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ALLOW_ORIGINS,
    allow_credentials=Config.CORS_ALLOW_CREDENTIALS,
    allow_methods=Config.CORS_ALLOW_METHODS,
    allow_headers=Config.CORS_ALLOW_HEADERS,
)

app.include_router(unified_routes.router)
app.include_router(user_routes.router)
app.include_router(contest_routes.router)

@app.get("/",
    summary="API Documentation",
    response_class=HTMLResponse)
async def root():
    """Custom HTML documentation for the API (default landing page)."""
    return HTMLResponse(content=html_template)

if __name__ == '__main__':
    uvicorn.run("app:app", 
                host=Config.get_host(), 
                port=Config.get_port(), 
                reload=Config.RELOAD if Config.is_dev() else False)
