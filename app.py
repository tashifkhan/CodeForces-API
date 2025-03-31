from fastapi.responses import HTMLResponse
import requests
import json
import time
from typing import Dict, List, Optional, Any, Set
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, Query, Path
import uvicorn

class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str


class UserInfo(BaseModel):
    """Model for user information from Codeforces."""
    handle: str
    rating: Optional[int] = None
    maxRating: Optional[int] = None
    rank: Optional[str] = None
    maxRank: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    organization: Optional[str] = None
    contribution: Optional[int] = None
    registrationTimeSeconds: Optional[int] = None
    friendOfCount: Optional[int] = None
    titlePhoto: Optional[str] = None
    avatar: Optional[str] = None


class RatingChangeContest(BaseModel):
    """Model for contest in a rating change."""
    id: int
    name: str


class RatingHistory(BaseModel):
    """Model for rating change history."""
    contestId: int
    contestName: str
    handle: str
    rank: int
    ratingUpdateTimeSeconds: int
    oldRating: int
    newRating: int


class SolvedProblemsCount(BaseModel):
    """Model for the number of solved problems."""
    handle: str
    count: int


class Contest(BaseModel):
    """Model for a contest."""
    id: int
    name: str
    type: str
    phase: str
    frozen: bool
    durationSeconds: int
    startTimeSeconds: int
    relativeTimeSeconds: Optional[int] = None
    preparedBy: Optional[str] = None
    websiteUrl: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[int] = None
    kind: Optional[str] = None
    icpcRegion: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    season: Optional[str] = None


class UserAllStats(UserInfo):
    """Model for comprehensive user statistics including profile, contests, and problems."""
    contests_count: int = Field(0, description="Number of contests participated in")
    solved_problems_count: int = Field(0, description="Number of problems solved")
    rating_history: Optional[List[RatingHistory]] = Field(None, description="History of rating changes")


app = FastAPI(
    title="Codeforces API",
    description="A FastAPI wrapper for the Codeforces API",
    version="1.0.0",
)

@app.get("/",
    summary="API Documentation",
    response_class=HTMLResponse)
async def root():
    """
    Custom HTML documentation for the API (default landing page).
    """
    html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>CodeForces Stats API Documentation</title>
            <style>
                :root {
                    --primary-color: #e4e4e4;
                    --secondary-color: #FF7D93;
                    --background-color: #0a192f;
                    --code-background: #112240;
                    --text-color: #8892b0;
                    --heading-color: #ccd6f6;
                    --card-background: #112240;
                    --hover-color: #233554;
                    --accent-color: #FF7D93;
                }
                /* Update all instances of var(--gfg-green) to var(--accent-color) */
                h1 {
                    border-bottom: 2px solid var(--accent-color);
                }
                .parameter {
                    border-left: 4px solid var(--accent-color);
                }
                .note {
                    border-left: 4px solid var(--accent-color);
                }
                .error-section h2 {
                    border-bottom: 2px solid var(--accent-color);
                }
                .endpoint-method {
                    background: var(--accent-color);
                }
                .try-button {
                    background-color: var(--accent-color);
                }
                .try-button:hover {
                    background-color: #ff4444;
                }
                .swagger-link {
                    border: 1px solid var(--accent-color);
                }
                .swagger-link:hover {
                    background-color: var(--accent-color);
                }
                footer a {
                    color: var(--accent-color) !important;
                }
                body {
                    font-family: 'SF Mono', 'Fira Code', 'Monaco', monospace;
                    line-height: 1.6;
                    color: var(--text-color);
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 4rem 2rem;
                    background: var(--background-color);
                    transition: all 0.25s ease-in-out;
                }
                h1, h2, h3 {
                    color: var(--heading-color);
                    padding-bottom: 0.75rem;
                    margin-top: 2rem;
                    font-weight: 600;
                    letter-spacing: -0.5px;
                }
                h1 {
                    font-size: clamp(1.8rem, 4vw, 2.5rem);
                    margin-bottom: 2rem;
                }
                .endpoint {
                    background: var(--card-background);
                    border-radius: 12px;
                    padding: 0;
                    margin: 1.5rem 0;
                    box-shadow: 0 10px 30px -15px rgba(2,12,27,0.7);
                    border: 1px solid var(--hover-color);
                    transition: all 0.2s ease-in-out;
                    overflow: hidden;
                }
                .endpoint-header {
                    padding: 1.5rem;
                    cursor: pointer;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    transition: background-color 0.2s ease;
                }
                .endpoint-header:hover {
                    background-color: var(--hover-color);
                }
                .endpoint-header h2 {
                    margin: 0;
                    padding: 0;
                    border: none;
                }
                .endpoint-content {
                    max-height: 0;
                    overflow: hidden;
                    transition: max-height 0.3s ease;
                    padding: 0 1.5rem;
                }
                .endpoint.active .endpoint-content {
                    max-height: 5000px; /* Large enough to show all content */
                    padding: 0 1.5rem 1.5rem;
                }
                .endpoint-toggle {
                    font-size: 1.5rem;
                    font-weight: bold;
                    color: var(--secondary-color);
                    transition: transform 0.3s ease;
                }
                .endpoint.active .endpoint-toggle {
                    transform: rotate(45deg);
                }
                code {
                    background: var(--code-background);
                    color: var(--secondary-color);
                    padding: 0.3rem 0.6rem;
                    border-radius: 6px;
                    font-family: 'SF Mono', 'Fira Code', monospace;
                    font-size: 0.85em;
                    word-break: break-word;
                    white-space: pre-wrap;
                }
                pre {
                    background: var(--code-background);
                    padding: 1.5rem;
                    border-radius: 12px;
                    overflow-x: auto;
                    margin: 1.5rem 0;
                    border: 1px solid var(--hover-color);
                    position: relative;
                }
                pre code {
                    padding: 0;
                    background: none;
                    color: var(--primary-color);
                    font-size: 0.9em;
                }
                .parameter {
                    margin: 1.5rem 0;
                    padding: 1.25rem;
                    border-left: 4px solid var(--accent-color);
                    background: var(--hover-color);
                    border-radius: 0 8px 8px 0;
                    box-shadow: 0 4px 12px -6px rgba(2,12,27,0.4);
                    transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
                }
                .parameter:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 6px 16px -6px rgba(2,12,27,0.5);
                }
                .parameter code {
                    font-size: 0.95em;
                    font-weight: 500;
                    margin-right: 0.5rem;
                }
                .error-response {
                    border-left: 4px solid #ff79c6;
                    padding: 1.25rem;
                    margin: 1.25rem 0;
                    background: var(--hover-color);
                    border-radius: 0 8px 8px 0;
                    overflow-x: auto;
                }
                .note {
                    background: var(--hover-color);
                    border-left: 4px solid var(--accent-color);
                    padding: 1.25rem;
                    margin: 1.25rem 0;
                    border-radius: 0 8px 8px 0;
                }
                        padding: 1rem 0.5rem;
                    }
                    .endpoint-header {
                        padding: 1rem;
                    }
                    h1 {
                        font-size: 1.8rem;
                    }
                    pre {
                        padding: 0.75rem;
                        font-size: 0.85em;
                    }
                    .parameter, .error-response, .note {
                        padding: 1rem;
                        margin: 1rem 0;
                    }
                }
                .method {
                    color: #ff79c6;
                    font-weight: bold;
                }
                .path {
                    color: var(--secondary-color);
                }
                .parameter {
                    margin: 1rem 0 1rem 1.5rem;
                    padding: 1rem;
                    border-left: 3px solid var(--gfg-green);
                    background: var(--hover-color);
                    border-radius: 0 8px 8px 0;
                }
                .error-section {
                    margin: 2rem 0;
                }
                .error-section h2 {
                    border-bottom: 2px solid var(--gfg-green);
                    padding-bottom: 0.75rem;
                }
                .error-toggle {
                    cursor: pointer;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 1rem;
                    background: var(--card-background);
                    border-radius: 8px;
                    margin-bottom: 1rem;
                    border: 1px solid var(--hover-color);
                }
                .error-toggle:hover {
                    background: var(--hover-color);
                }
                .error-toggle h3 {
                    margin: 0;
                    padding: 0;
                    border: none;
                }
                .error-content {
                    max-height: 0;
                    overflow: hidden;
                    transition: max-height 0.3s ease;
                }
                .error-item.active .error-content {
                    max-height: 1000px;
                }
                .error-toggle-icon {
                    font-size: 1.5rem;
                    font-weight: bold;
                    color: var(--secondary-color);
                    transition: transform 0.3s ease;
                }
                .error-item.active .error-toggle-icon {
                    transform: rotate(45deg);
                }
                ::selection {
                    background: var(--secondary-color);
                    color: var(--background-color);
                }
                .endpoint-method {
                    display: inline-block;
                    padding: 0.3rem 0.5rem;
                    color: white;
                    border-radius: 4px;
                    font-weight: bold;
                    margin-right: 0.5rem;
                }
                .try-button {
                    display: inline-block;
                    margin-top: 1rem;
                    padding: 0.75rem 1.5rem;
                    color: white;
                    border-radius: 4px;
                    font-weight: bold;
                    text-decoration: none;
                    transition: all 0.2s ease;
                    border: none;
                    cursor: pointer;
                }
                .try-button:hover {
                    background-color: #8e7cc3;
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                }
                .swagger-link {
                    position: fixed;
                    top: 1rem;
                    right: 1rem;
                    padding: 0.5rem 1rem;
                    background-color: var(--hover-color);
                    color: var(--heading-color);
                    border-radius: 4px;
                    text-decoration: none;
                    font-weight: bold;
                    transition: all 0.2s ease;
                    border: none;
                }
                .swagger-link:hover {
                    color: white;
                }
                footer {
                    margin-top: 4rem;
                    padding-top: 2rem;
                    text-align: center;
                    position: relative;
                }

                footer:before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 50%;
                    transform: translateX(-50%);
                    width: 80%;
                    height: 1px;
                    background: linear-gradient(
                        to right,
                        transparent,
                        var(--accent-color),
                        transparent
                    );
                }

                footer p {
                    margin: 0.5rem 0;
                    font-size: 0.9rem;
                    color: var(--text-color);
                }

                footer a {
                    color: var(--accent-color) !important;
                    text-decoration: none;
                    position: relative;
                    transition: all 0.2s ease;
                }

                footer a:hover {
                    color: var(--heading-color) !important;
                }

                footer a:after {
                    content: '';
                    position: absolute;
                    width: 100%;
                    height: 1px;
                    bottom: -2px;
                    left: 0;
                    background-color: var(--accent-color);
                    transform: scaleX(0);
                    transform-origin: right;
                    transition: transform 0.3s ease;
                }

                footer a:hover:after {
                    transform: scaleX(1);
                    transform-origin: left;
                }
            </style>
        </head>
        <body>
            <a href="/docs" class="swagger-link">Swagger UI</a>
            <h1>CodeForces Stats API Documentation</h1>
            
            <p>This API provides access to CodeForces user statistics and contest data. Explore the endpoints below.</p>

            <div class="endpoint">
                <div class="endpoint-header">
                    <h2><span class="endpoint-method">GET</span> User All Stats</h2>
                    <span class="endpoint-toggle">+</span>
                </div>
                <div class="endpoint-content">
                    <p><code class="path">/<span>{userid}</span></code></p>
                    
                    <h3>Parameters</h3>
                    <div class="parameter">
                        <code>userid</code> (path parameter): CodeForces handle
                    </div>

                    <h3>Response Format</h3>
                    <pre>
<code>
{
    "handle": "example_user",
    "rating": 1500,
    "maxRating": 1700,
    "rank": "specialist",
    "maxRank": "expert",
    "contests_count": 25,
    "solved_problems_count": 150,
    "rating_history": [
        {
            "contestId": 1234,
            "contestName": "Codeforces Round #123",
            "handle": "example_user",
            "rank": 100,
            "ratingUpdateTimeSeconds": 1632145200,
            "oldRating": 1400,
            "newRating": 1500
        }
    ]
}
</code>
                    </pre>

                    <h3>Example</h3>
                    <pre><code>GET /tourist</code></pre>
                    
                    <a href="/docs#/default/user_all_stats__userid__get" class="try-button" target="_blank">Try it in Swagger UI</a>
                </div>
            </div>

            <div class="endpoint">
                <div class="endpoint-header">
                    <h2><span class="endpoint-method">GET</span> User Basic Info</h2>
                    <span class="endpoint-toggle">+</span>
                </div>
                <div class="endpoint-content">
                    <p><code class="path">/<span>{userid}</span>/basic</code></p>
                    
                    <h3>Parameters</h3>
                    <div class="parameter">
                        <code>userid</code> (path parameter): CodeForces handle
                    </div>

                    <h3>Response Format</h3>
                    <pre>
<code>
{
    "handle": "example_user",
    "rating": 1500,
    "maxRating": 1700,
    "rank": "specialist",
    "maxRank": "expert",
    "country": "Russia",
    "organization": "ITMO University"
}
</code>
                    </pre>

                    <h3>Example</h3>
                    <pre><code>GET /tourist/basic</code></pre>
                    
                    <a href="/docs#/default/user_basic_info__userid__basic_get" class="try-button" target="_blank">Try it in Swagger UI</a>
                </div>
            </div>

            <div class="endpoint">
                <div class="endpoint-header">
                    <h2><span class="endpoint-method">GET</span> Multi-User Info</h2>
                    <span class="endpoint-toggle">+</span>
                </div>
                <div class="endpoint-content">
                    <p><code class="path">/multi/<span>{userids}</span></code></p>
                    
                    <h3>Parameters</h3>
                    <div class="parameter">
                        <code>userids</code> (path parameter): Semicolon-separated list of CodeForces handles
                    </div>

                    <h3>Response Format</h3>
                    <pre>
<code>
[
    {
        "handle": "tourist",
        "rating": 3800,
        "rank": "legendary grandmaster"
    },
    {
        "handle": "SecondBest",
        "rating": 3500,
        "rank": "international grandmaster"
    }
]
</code>
                    </pre>

                    <h3>Example</h3>
                    <pre><code>GET /multi/tourist;SecondBest</code></pre>
                    
                    <a href="/docs#/default/users_info_multi__userids__get" class="try-button" target="_blank">Try it in Swagger UI</a>
                </div>
            </div>

            <div class="endpoint">
                <div class="endpoint-header">
                    <h2><span class="endpoint-method">GET</span> Upcoming Contests</h2>
                    <span class="endpoint-toggle">+</span>
                </div>
                <div class="endpoint-content">
                    <p><code class="path">/contests/upcoming</code></p>
                    
                    <h3>Parameters</h3>
                    <div class="parameter">
                        <code>gym</code> (query parameter, optional): Boolean to include gym contests
                    </div>

                    <h3>Response Format</h3>
                    <pre>
<code>
[
    {
        "id": 1234,
        "name": "Codeforces Round #123",
        "type": "CF",
        "phase": "BEFORE",
        "frozen": false,
        "durationSeconds": 7200,
        "startTimeSeconds": 1632145200
    }
]
</code>
                    </pre>

                    <h3>Example</h3>
                    <pre><code>GET /contests/upcoming?gym=false</code></pre>
                    
                    <a href="/docs#/default/upcoming_contests_contests_upcoming_get" class="try-button" target="_blank">Try it in Swagger UI</a>
                </div>
            </div>

            <div class="endpoint">
                <div class="endpoint-header">
                    <h2><span class="endpoint-method">GET</span> User Rating History</h2>
                    <span class="endpoint-toggle">+</span>
                </div>
                <div class="endpoint-content">
                    <p><code class="path">/<span>{userid}</span>/rating</code></p>
                    
                    <h3>Parameters</h3>
                    <div class="parameter">
                        <code>userid</code> (path parameter): CodeForces handle
                    </div>

                    <h3>Response Format</h3>
                    <pre>
<code>
[
    {
        "contestId": 1234,
        "contestName": "Codeforces Round #123",
        "handle": "tourist",
        "rank": 1,
        "ratingUpdateTimeSeconds": 1632145200,
        "oldRating": 3795,
        "newRating": 3800
    }
]
</code>
                    </pre>

                    <h3>Example</h3>
                    <pre><code>GET /tourist/rating</code></pre>
                    
                    <a href="/docs#/default/user_rating__userid__rating_get" class="try-button" target="_blank">Try it in Swagger UI</a>
                </div>
            </div>

            <div class="endpoint">
                <div class="endpoint-header">
                    <h2><span class="endpoint-method">GET</span> Solved Problems Count</h2>
                    <span class="endpoint-toggle">+</span>
                </div>
                <div class="endpoint-content">
                    <p><code class="path">/<span>{userid}</span>/solved</code></p>
                    
                    <h3>Parameters</h3>
                    <div class="parameter">
                        <code>userid</code> (path parameter): CodeForces handle
                    </div>

                    <h3>Response Format</h3>
                    <pre>
<code>
{
    "handle": "tourist",
    "count": 1500
}
</code>
                    </pre>

                    <h3>Example</h3>
                    <pre><code>GET /tourist/solved</code></pre>
                    
                    <a href="/docs#/default/solved_problems__userid__solved_get" class="try-button" target="_blank">Try it in Swagger UI</a>
                </div>
            </div>

            <div class="endpoint">
                <div class="endpoint-header">
                    <h2><span class="endpoint-method">GET</span> User Contests</h2>
                    <span class="endpoint-toggle">+</span>
                </div>
                <div class="endpoint-content">
                    <p><code class="path">/<span>{userid}</span>/contests</code></p>
                    
                    <h3>Parameters</h3>
                    <div class="parameter">
                        <code>userid</code> (path parameter): CodeForces handle
                    </div>

                    <h3>Response Format</h3>
                    <pre>
<code>
{
    "handle": "tourist",
    "contests": [1234, 1235, 1236]
}
</code>
                    </pre>

                    <h3>Example</h3>
                    <pre><code>GET /tourist/contests</code></pre>
                    
                    <a href="/docs#/default/contests_participated__userid__contests_get" class="try-button" target="_blank">Try it in Swagger UI</a>
                </div>
            </div>

            <div class="endpoint">
                <div class="endpoint-header">
                    <h2><span class="endpoint-method">GET</span> Common Contests</h2>
                    <span class="endpoint-toggle">+</span>
                </div>
                <div class="endpoint-content">
                    <p><code class="path">/users/common-contests/<span>{userids}</span></code></p>
                    
                    <h3>Parameters</h3>
                    <div class="parameter">
                        <code>userids</code> (path parameter): Semicolon-separated list of CodeForces handles
                    </div>

                    <h3>Response Format</h3>
                    <pre>
<code>
{
    "handles": ["tourist", "SecondBest"],
    "common_contests": [1234, 1235, 1236]
}
</code>
                    </pre>

                    <h3>Example</h3>
                    <pre><code>GET /users/common-contests/tourist;SecondBest</code></pre>
                    
                    <a href="/docs#/default/common_contests_users_common_contests__userids__get" class="try-button" target="_blank">Try it in Swagger UI</a>
                </div>
            </div>

            <div class="error-section">
                <h2>Error Responses</h2>
                
                <div class="error-item">
                    <div class="error-toggle">
                        <h3>User not found</h3>
                        <span class="error-toggle-icon">+</span>
                    </div>
                    <div class="error-content">
                        <pre>
<code>{
    "detail": "User information not found for {handle}"
}</code>
                        </pre>
                    </div>
                </div>

                <div class="error-item">
                    <div class="error-toggle">
                        <h3>Invalid request</h3>
                        <span class="error-toggle-icon">+</span>
                    </div>
                    <div class="error-content">
                        <pre>
<code>{
    "detail": "No valid handles provided"
}</code>
                        </pre>
                    </div>
                </div>
            </div>

            <div class="note">
                <h2>Usage Notes</h2>
                <p>Please use this API responsibly and consider CodeForces' rate limits when making requests.</p>
                <p>The API respects CodeForces' rate limiting of 1 request per 2 seconds.</p>
            </div>

            <footer>
                <p>This API is open source and available on <a href="https://github.com/tashifkhan/GFG-Stats-API" style="  text-decoration: none;">GitHub</a>.</p>
                <p>Try it live at <a href="https://codeforces-stats.tashif.codes" style="text-decoration: none;">codeforces-stats.tashif.codes</a></p>
            </footer>

            <script>
                document.addEventListener('DOMContentLoaded', function() {
                    // Handle endpoint toggles
                    const endpoints = document.querySelectorAll('.endpoint');
                    endpoints.forEach(endpoint => {
                        const header = endpoint.querySelector('.endpoint-header');
                        header.addEventListener('click', () => {
                            endpoint.classList.toggle('active');
                        });
                    });
                    
                    // Handle error toggles
                    const errorItems = document.querySelectorAll('.error-item');
                    errorItems.forEach(item => {
                        const toggle = item.querySelector('.error-toggle');
                        toggle.addEventListener('click', () => {
                            item.classList.toggle('active');
                        });
                    });
                    
                    // Make the first endpoint active by default for better UX
                    if (endpoints.length > 0) {
                        endpoints[0].classList.add('active');
                    }
                });
            </script>
        </body>
        </html>
    """
    return HTMLResponse(content=html)

@app.get("/{userid}", response_model=UserAllStats, responses={404: {"model": ErrorResponse}})
async def user_all_stats(userid: str = Path(..., description="Codeforces handle")):
    """
    Get comprehensive statistics for a Codeforces user.
    
    This includes profile info, contests participated, problems solved, and rating history.
    """
    stats = get_user_all_stats(userid)
    if stats is None:
        raise HTTPException(status_code=404, detail=f"Stats not found for {userid}")
    return stats

@app.get("/{userid}/basic", response_model=UserInfo, responses={404: {"model": ErrorResponse}})
async def user_basic_info(userid: str = Path(..., description="Codeforces handle")):
    """Get basic information about a Codeforces user."""
    user_info = get_user_info([userid])
    if not user_info:
        raise HTTPException(status_code=404, detail=f"User information not found for {userid}")
    return user_info[0]

@app.get("/multi/{userids}", response_model=List[UserInfo], responses={404: {"model": ErrorResponse}})
async def users_info(userids: str = Path(..., description="Semicolon-separated list of Codeforces handles")):
    """Get information about multiple Codeforces users."""
    handles_list = []
    if ';' in userids:
        handles_list = userids.split(';')
    elif ',' in userids:
        handles_list = userids.split(',')
    else:
        handles_list = [userids]
    
    # Clean up handles list to remove any empty strings
    handles_list = [h.strip() for h in handles_list if h.strip()]
    
    if not handles_list:
        raise HTTPException(status_code=400, detail="No valid handles provided")
    
    # Call get_user_info directly with the list of handles
    user_info = get_user_info(handles_list)
    
    if not user_info:
        raise HTTPException(status_code=404, detail=f"User information not found")
    
    return user_info

@app.get("/{userid}/rating", response_model=List[RatingHistory], responses={404: {"model": ErrorResponse}})
async def user_rating(userid: str = Path(..., description="Codeforces handle")):
    """Get rating history of a Codeforces user."""
    rating_history = get_user_rating(userid)
    if rating_history is None:
        raise HTTPException(status_code=404, detail=f"Rating history not found for {userid}")
    return rating_history

@app.get("/{userid}/solved", response_model=SolvedProblemsCount, responses={404: {"model": ErrorResponse}})
async def solved_problems(userid: str = Path(..., description="Codeforces handle")):
    """Get the number of solved problems for a Codeforces user."""
    solved_count = get_solved_problem_count(userid)
    if solved_count is None:
        raise HTTPException(status_code=404, detail=f"Solved problem count not found for {userid}")
    return {"handle": userid, "count": solved_count}

@app.get("/contests/upcoming", response_model=List[Contest], responses={404: {"model": ErrorResponse}})
async def upcoming_contests(gym: bool = False):
    """Get upcoming contests from Codeforces."""
    contests = get_upcoming_contests(gym)
    if contests is None:
        raise HTTPException(status_code=404, detail=f"Upcoming contests data not found")
    return contests

@app.get("/{userid}/contests", response_model=Dict[str, Any], responses={404: {"model": ErrorResponse}})
async def contests_participated(userid: str = Path(..., description="Codeforces handle")):
    """Get contests participated by a Codeforces user."""
    contests = get_contests_participated_by_user(userid)
    if not contests:
        raise HTTPException(status_code=404, detail=f"Contest participation data not found for {userid}")
    return {"handle": userid, "contests": list(contests)}

@app.get("/users/common-contests/{userids}", response_model=Dict[str, Any], responses={404: {"model": ErrorResponse}})
async def common_contests(userids: str = Path(..., description="Semicolon-separated list of Codeforces handles")):
    """Get common contests participated by multiple Codeforces users."""
    # Support both semicolon and comma as separators
    handles_list = []
    if ';' in userids:
        handles_list = userids.split(';')
    elif ',' in userids:
        handles_list = userids.split(',')
    else:
        handles_list = [userids]  # Single handle

    # Remove any empty strings from the list
    handles_list = [h.strip() for h in handles_list if h.strip()]
    
    if not handles_list:
        raise HTTPException(status_code=400, detail="No valid handles provided")

    common = get_common_contests(handles_list)
    if common is None:
        raise HTTPException(status_code=404, detail=f"Common contest data not found for {handles}")
    return {"handles": handles_list, "common_contests": list(common)}

def get_user_info(handles):
    """
    Fetches information about Codeforces users.

    Args:
        handles: A list of Codeforces user handles.

    Returns:
        A list of user objects, or None if there was an error.
    """
    url = f"https://codeforces.com/api/user.info?handles={';'.join(handles)}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        if data["status"] == "OK":
            return data["result"]
        else:
            print(f"Error fetching user info: {data['comment']}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None

def get_user_rating(handle):
    """
    Fetches the rating history of a Codeforces user.

    Args:
        handle: The Codeforces user handle.

    Returns:
        A list of rating change objects, or None if there was an error.
    """
    url = f"https://codeforces.com/api/user.rating?handle={handle}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data["status"] == "OK":
            return data["result"]
        else:
            print(f"Error fetching user rating: {data['comment']}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None
    
def get_solved_problem_count(handle):
    """
    Calculates the number of solved problems for a Codeforces user.

    Args:
        handle: The Codeforces user handle.

    Returns:
        The number of solved problems, or None if there was an error.
    """
    url = f"https://codeforces.com/api/user.status?handle={handle}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data["status"] == "OK":
            solved_problems = set()
            for submission in data["result"]:
                if submission["verdict"] == "OK":
                    problem_id = (submission["problem"]["contestId"], submission["problem"]["index"])
                    solved_problems.add(problem_id)
            return len(solved_problems)
        else:
            print(f"Error fetching user status: {data['comment']}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None
    
def get_upcoming_contests(gym=False):
    """
    Fetches a list of upcoming contests from the Codeforces API.

    Args:
        gym: If True, only gym contests are returned. Otherwise, only regular contests.

    Returns:
        A list of upcoming contest objects, or None if there was an error.
    """
    url = f"https://codeforces.com/api/contest.list?gym={str(gym).lower()}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data["status"] == "OK":
            upcoming_contests = []
            current_time = time.time()  # Current time in seconds since epoch
            for contest in data["result"]:
                if contest["phase"] == "BEFORE" and contest["startTimeSeconds"] > current_time:
                    upcoming_contests.append(contest)
            return upcoming_contests
        else:
            print(f"Error fetching contest list: {data['comment']}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None
    

def get_contests_participated_by_user(handle):
    """
    Gets a list of contests that the given Codeforces user has participated in.

    Args:
        handle: A Codeforces user handle.

    Returns:
        A set of contest IDs representing the contests participated in by the user.
    """
    contests = set()
    time.sleep(2)  # Respect rate limit (1 request per 2 seconds)
    url = f"https://codeforces.com/api/user.status?handle={handle}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data["status"] == "OK":
            for submission in data["result"]:
                if 'contestId' in submission:
                    contests.add(submission["contestId"])
        else:
            print(f"Error fetching submissions for {handle}: {data['comment']}")
    except requests.exceptions.RequestException as e:
        print(f"Request error for {handle}: {e}")
    return contests


def get_common_contests(handles):
    """
    Gets the common contests that a list of Codeforces users have participated in.

    Args:
        handles: A list of Codeforces user handles.

    Returns:
        A set of contest IDs representing the contests participated in by all users,
        or None if there was a critical error fetching data.
    """
    if not handles:
        return set()  # No users, no contests

    all_users_contests = []
    
    for handle in handles:
        user_contests = get_contests_participated_by_user(handle)
        if user_contests is None:
            print(f"Could not retrieve contest data for {handle}. Skipping.")
            continue
        
        if not user_contests:  # If user has no contests
            print(f"User {handle} has no contest participation")
            # If any user has no contests, the intersection will be empty
            return set()
        
        all_users_contests.append(user_contests)
    
    if not all_users_contests:
        # If we couldn't retrieve contest data for any user
        return set()
    
    # Start with the first user's contests
    common_contests = all_users_contests[0]
    
    # Take intersection with each subsequent user's contests
    for user_contests in all_users_contests[1:]:
        common_contests = common_contests.intersection(user_contests)
    
    return common_contests

def get_user_all_stats(handle):
    """
    Gets comprehensive statistics for a Codeforces user including profile info,
    number of contests participated in, and number of problems solved.

    Args:
        handle: A Codeforces user handle.

    Returns:
        A UserAllStats object with all user statistics, or None if there was an error.
    """
    # Make sure handle is a string, not a list
    if isinstance(handle, list):
        # This function only works with a single handle
        # If a list is passed, we'll just use the first one
        if not handle:  # Empty list
            return None
        handle = handle[0]
        
    user_info = get_user_info([handle])
    if not user_info:
        return None
    
    # Get contest participation
    contests = get_contests_participated_by_user(handle)
    contests_count = len(contests) if contests else 0
    
    # Get solved problems count
    solved_count = get_solved_problem_count(handle)
    if solved_count is None:
        solved_count = 0
    
    # Get rating history
    rating_history = get_user_rating(handle)
    
    # Create UserAllStats object
    all_stats = UserAllStats(**user_info[0])
    all_stats.contests_count = contests_count
    all_stats.solved_problems_count = solved_count
    all_stats.rating_history = rating_history
    
    return all_stats


if __name__ == '__main__':
    uvicorn.run("app:app", host="0.0.0.0", port=58353, reload=True)