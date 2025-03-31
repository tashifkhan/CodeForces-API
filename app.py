from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
from routes import user_routes, contest_routes
from models.templates import html_template

app = FastAPI(
    title="Codeforces Stats API",
    description="A FastAPI app for the Codeforces Stats",
    version="1.0.0",
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
    uvicorn.run("app:app", host="0.0.0.0", port=58353, reload=True)