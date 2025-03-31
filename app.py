from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
from routes import user_routes, contest_routes
from models.templates import html_template
from config import Config

app = FastAPI(
    title=Config.TITLE,
    description=Config.DESCRIPTION,
    version=Config.VERSION,
)

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