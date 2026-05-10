from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from routes import badges, contests, docs, heatmap, legacy, profile, rating, stats, summary, topics
from config import Config
from core.middleware import CacheRateLimitMiddleware

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
app.add_middleware(CacheRateLimitMiddleware, platform="codeforces")

app.include_router(docs.router)
app.include_router(profile.router)
app.include_router(stats.router)
app.include_router(contests.router)
app.include_router(rating.router)
app.include_router(heatmap.router)
app.include_router(topics.router)
app.include_router(badges.router)
app.include_router(summary.router)
app.include_router(legacy.router)

if __name__ == '__main__':
    uvicorn.run("app:app", 
                host=Config.get_host(), 
                port=Config.get_port(), 
                reload=Config.RELOAD if Config.is_dev() else False)
