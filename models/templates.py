html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="logo.png" type="image/png">
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
    <a href="/docs" class="swagger-link" style="right: 8.5rem;">Swagger UI</a>
    <a href="/redoc" class="swagger-link">ReDoc</a>
    <h1>CodeForces Stats Profile Dashboard</h1>
    
    <!-- Interactive Dashboard Section -->
    <div class="dashboard-section" style="background: var(--card-background); border-radius: 12px; padding: 2rem; margin-bottom: 2.5rem; border: 1px solid var(--hover-color); text-align: center;">
        <h2 style="color: var(--heading-color); margin-bottom: 1.5rem;">Explore a Codeforces Profile</h2>
        <div class="input-group" style="display: flex; justify-content: center; gap: 1rem; max-width: 500px; margin: 0 auto;">
            <input type="text" id="cf-handle" placeholder="Enter Codeforces handle (e.g., tourist)" style="flex: 1; padding: 0.75rem 1rem; border: 2px solid var(--hover-color); border-radius: 8px; background: var(--code-background); color: var(--text-color); font-family: inherit; font-size: 1rem; transition: border-color 0.2s ease;" />
            <button onclick="exploreCFUser()" class="try-button" style="background: var(--accent-color); color: var(--background-color); font-size: 1rem; display: flex; align-items: center; gap: 0.5rem;">
                <svg class="icon" viewBox="0 0 24 24" fill="currentColor" style="width: 1.2rem; height: 1.2rem;"><path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
                Analyze
            </button>
        </div>
        <div id="cf-dashboard-loading" class="loading" style="display: none; margin-top: 1.5rem;">
            <div class="spinner"></div>
            <p>Fetching Codeforces data...</p>
        </div>
        <div id="cf-dashboard-results" class="profile-results" style="display: none; margin-top: 2rem;">
            <!-- Profile Overview Cards -->
            <div class="profile-cards" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
                <div class="profile-card" style="background: var(--hover-color); border-radius: 12px; padding: 1.5rem; text-align: center;">
                    <div class="card-icon">
                        <svg class="icon" viewBox="0 0 24 24" fill="currentColor"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>
                    </div>
                    <div class="card-content">
                        <h4 style="color: var(--text-color); margin-bottom: 0.5rem; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.5px;">Handle</h4>
                        <div id="cf-handle-value" class="card-value" style="color: var(--secondary-color); font-size: 1.5rem; font-weight: 700;">-</div>
                    </div>
                </div>
                <div class="profile-card" style="background: var(--hover-color); border-radius: 12px; padding: 1.5rem; text-align: center;">
                    <div class="card-icon">
                        <svg class="icon" viewBox="0 0 24 24" fill="currentColor"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/></svg>
                    </div>
                    <div class="card-content">
                        <h4 style="color: var(--text-color); margin-bottom: 0.5rem; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.5px;">Rating</h4>
                        <div id="cf-rating" class="card-value" style="color: var(--secondary-color); font-size: 1.5rem; font-weight: 700;">-</div>
                    </div>
                </div>
                <div class="profile-card" style="background: var(--hover-color); border-radius: 12px; padding: 1.5rem; text-align: center;">
                    <div class="card-icon">
                        <svg class="icon" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
                    </div>
                    <div class="card-content">
                        <h4 style="color: var(--text-color); margin-bottom: 0.5rem; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.5px;">Max Rating</h4>
                        <div id="cf-max-rating" class="card-value" style="color: var(--secondary-color); font-size: 1.5rem; font-weight: 700;">-</div>
                    </div>
                </div>
                <div class="profile-card" style="background: var(--hover-color); border-radius: 12px; padding: 1.5rem; text-align: center;">
                    <div class="card-icon">
                        <svg class="icon" viewBox="0 0 24 24" fill="currentColor"><path d="M13 2.05v3.03c3.39.49 6 3.39 6 6.92 0 .9-.18 1.75-.5 2.54l2.6 1.53c.56-1.24.9-2.62.9-4.07 0-5.18-3.95-9.45-9-9.95zM12 19c-3.87 0-7-3.13-7-7 0-3.53 2.61-6.43 6-6.92V2.05c-5.05.5-9 4.76-9 9.95 0 5.52 4.47 10 9.99 10 3.31 0 6.24-1.61 8.06-4.09l-2.6-1.53C16.17 17.98 14.21 19 12 19z"/></svg>
                    </div>
                    <div class="card-content">
                        <h4 style="color: var(--text-color); margin-bottom: 0.5rem; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.5px;">Contests</h4>
                        <div id="cf-contests" class="card-value" style="color: var(--secondary-color); font-size: 1.5rem; font-weight: 700;">-</div>
                    </div>
                </div>
                <div class="profile-card" style="background: var(--hover-color); border-radius: 12px; padding: 1.5rem; text-align: center;">
                    <div class="card-icon">
                        <svg class="icon" viewBox="0 0 24 24" fill="currentColor"><path d="M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z"/></svg>
                    </div>
                    <div class="card-content">
                        <h4 style="color: var(--text-color); margin-bottom: 0.5rem; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.5px;">Solved</h4>
                        <div id="cf-solved" class="card-value" style="color: var(--secondary-color); font-size: 1.5rem; font-weight: 700;">-</div>
                    </div>
                </div>
            </div>
            <!-- Language Bar (Placeholder) -->
            <div id="cf-languages" class="languages-chart" style="margin-bottom: 2rem;"></div>
            <!-- Contest History (Placeholder) -->
            <div id="cf-contest-history" style="margin-bottom: 2rem;"></div>
            <!-- Recent Contests (Placeholder) -->
            <div id="cf-recent-contests"></div>
        </div>
    </div>

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

            // Add Enter key support for the Codeforces handle input
            const cfHandleInput = document.getElementById('cf-handle');
            if (cfHandleInput) {
                cfHandleInput.addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        exploreCFUser();
                    }
                });
            }
        });

        // Codeforces Dashboard Functionality
        async function exploreCFUser() {
            const handleInput = document.getElementById('cf-handle');
            const loading = document.getElementById('cf-dashboard-loading');
            const results = document.getElementById('cf-dashboard-results');
            
            if (!handleInput || !loading || !results) {
                console.error('Required DOM elements not found');
                return;
            }
            
            const handle = handleInput.value.trim();
            if (!handle) {
                alert('Please enter a Codeforces handle');
                return;
            }
            
            // Show loading
            loading.style.display = 'block';
            results.style.display = 'none';
            
            try {
                // Fetch user data from the API
                const response = await fetch(`/${handle}`);
                const data = await response.json();
                
                if (response.ok) {
                    displayCFResults(handle, data);
                } else {
                    showCFError(data.detail || 'Failed to fetch user data');
                }
            } catch (error) {
                console.error('Error fetching data:', error);
                showCFError('Failed to fetch Codeforces data. Please check the handle and try again.');
            } finally {
                loading.style.display = 'none';
            }
        }
        
        function displayCFResults(handle, data) {
            const results = document.getElementById('cf-dashboard-results');
            
            // Update profile cards
            const elements = {
                'cf-handle-value': document.getElementById('cf-handle-value'),
                'cf-rating': document.getElementById('cf-rating'),
                'cf-max-rating': document.getElementById('cf-max-rating'),
                'cf-contests': document.getElementById('cf-contests'),
                'cf-solved': document.getElementById('cf-solved')
            };
            
            if (elements['cf-handle-value']) elements['cf-handle-value'].textContent = handle;
            if (elements['cf-rating']) elements['cf-rating'].textContent = data.rating || 'N/A';
            if (elements['cf-max-rating']) elements['cf-max-rating'].textContent = data.maxRating || 'N/A';
            if (elements['cf-contests']) elements['cf-contests'].textContent = data.contests_count || 'N/A';
            if (elements['cf-solved']) elements['cf-solved'].textContent = data.solved_problems_count || 'N/A';
            
            // Display rating history if available
            displayRatingHistory(data.rating_history || []);
            
            // Display recent contests if available
            displayRecentContests(data.rating_history || []);
            
            results.style.display = 'block';
        }
        
        function displayRatingHistory(ratingHistory) {
            const container = document.getElementById('cf-contest-history');
            if (!container) return;
            
            if (ratingHistory.length === 0) {
                container.innerHTML = '<div style="text-align: center; color: var(--text-color); padding: 2rem;">No contest history available</div>';
                return;
            }
            
            // Show last 10 contests
            const recentContests = ratingHistory.slice(-10).reverse();
            
            let html = '<h3 style="color: var(--heading-color); margin-bottom: 1rem;">Recent Contest History</h3>';
            html += '<div style="display: flex; flex-direction: column; gap: 1rem;">';
            
            recentContests.forEach(contest => {
                const ratingChange = contest.newRating - contest.oldRating;
                const changeColor = ratingChange >= 0 ? '#4caf50' : '#f44336';
                const changeSymbol = ratingChange >= 0 ? '+' : '';
                
                html += `
                    <div style="background: var(--hover-color); border-radius: 8px; padding: 1rem; border-left: 4px solid var(--accent-color);">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <span style="color: var(--secondary-color); font-weight: 600;">${contest.contestName}</span>
                            <span style="color: ${changeColor}; font-weight: 600;">${changeSymbol}${ratingChange}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.9rem;">
                            <span style="color: var(--text-color);">Rank: ${contest.rank}</span>
                            <span style="color: var(--text-color);">${contest.oldRating} → ${contest.newRating}</span>
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
            container.innerHTML = html;
        }
        
        function displayRecentContests(ratingHistory) {
            const container = document.getElementById('cf-recent-contests');
            if (!container) return;
            
            if (ratingHistory.length === 0) {
                container.innerHTML = '<div style="text-align: center; color: var(--text-color); padding: 2rem;">No recent contests available</div>';
                return;
            }
            
            // Show upcoming contests (this would need a separate API call)
            container.innerHTML = `
                <h3 style="color: var(--heading-color); margin-bottom: 1rem;">Upcoming Contests</h3>
                <div style="text-align: center; color: var(--text-color); padding: 2rem;">
                    <p>Check <a href="/contests/upcoming" style="color: var(--accent-color);">upcoming contests</a> for the latest competition schedule.</p>
                </div>
            `;
        }
        
        function showCFError(message) {
            const results = document.getElementById('cf-dashboard-results');
            if (!results) {
                console.error('Results container not found');
                return;
            }
            results.innerHTML = `<div style="background: #ff6b6b; color: white; padding: 1rem; border-radius: 8px; text-align: center; margin: 1rem 0;">${message}</div>`;
            results.style.display = 'block';
        }
    </script>
</body>
</html>
"""
