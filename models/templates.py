html_template = """
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