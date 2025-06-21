# CodeForces-Stats-API

A robust RESTful API to fetch and display CodeForces statistics for users, built with FastAPI.

Hosted at [codeforces-stats.tashif.codes](https://codeforces-stats.tashif.codes)

## Interactive Dashboard Implementation

- **Interactive Profile Explorer**: Added a live dashboard at the root endpoint (`/`) that allows users to explore CodeForces profiles in real-time
- **Real-time Data Fetching**: Users can enter any CodeForces handle and instantly view comprehensive statistics
- **Visual Profile Cards**: Beautiful card-based layout displaying key metrics:
  - Current Rating
  - Maximum Rating Achieved
  - Total Contests Participated
  - Problems Solved Count
- **Contest History Visualization**: Interactive display of recent contest performance with rating changes
- **Responsive Design**: Modern, mobile-friendly interface with smooth animations and hover effects

## Features

- Retrieve user's rating, rank, and maximum achieved rating
- Get detailed contest participation history
- View solved problems count
- Fetch multiple users' information simultaneously
- Track upcoming contests
- Find common contests between multiple users
- **Interactive Dashboard** for real-time profile exploration
- Easy integration with other applications
- Rate-limited endpoints to respect CodeForces API limits

## API Endpoints

### Get User All Stats

```
GET /{userid}
```

Retrieves complete statistics for a CodeForces user.

#### Parameters

- `userid` (path): CodeForces handle

#### Response

Returns user's complete CodeForces statistics including rating history.

#### Example Response

```json
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
```

### Get User Basic Info

```
GET /{userid}/basic
```

Retrieves basic information for a CodeForces user.

#### Parameters

- `userid` (path): CodeForces handle

#### Response

Returns user's basic profile information.

#### Example Response

```json
{
	"handle": "example_user",
	"rating": 1500,
	"maxRating": 1700,
	"rank": "specialist",
	"maxRank": "expert",
	"country": "Russia",
	"organization": "ITMO University"
}
```

### Get Multiple Users Info

```
GET /multi/{userids}
```

Retrieves basic information for multiple CodeForces users.

#### Parameters

- `userids` (path): Semicolon-separated list of CodeForces handles

#### Response

Returns basic information for all specified users.

#### Example Response

```json
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
```

### Get Upcoming Contests

```
GET /contests/upcoming
```

Retrieves information about upcoming CodeForces contests.

#### Parameters

- `gym` (query, optional): Boolean to include gym contests

#### Response

Returns a list of upcoming contests.

#### Example Response

```json
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
```

### Get User Rating History

```
GET /{userid}/rating
```

Retrieves the complete rating history for a CodeForces user.

#### Parameters

- `userid` (path): CodeForces handle

#### Response

Returns the user's complete contest and rating history.

#### Example Response

```json
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
```

### Get Solved Problems Count

```
GET /{userid}/solved
```

Retrieves the number of problems solved by a CodeForces user.

#### Parameters

- `userid` (path): CodeForces handle

#### Response

Returns the user's handle and total problems solved.

#### Example Response

```json
{
	"handle": "tourist",
	"count": 1500
}
```

### Get User's Contests

```
GET /{userid}/contests
```

Retrieves the IDs of contests in which a user has participated.

#### Parameters

- `userid` (path): CodeForces handle

#### Response

Returns the user's handle and a list of contest IDs.

#### Example Response

```json
{
	"handle": "tourist",
	"contests": [1234, 1235, 1236]
}
```

### Get Common Contests

```
GET /users/common-contests/{userids}
```

Finds contests in which all specified users have participated.

#### Parameters

- `userids` (path): Semicolon-separated list of CodeForces handles

#### Response

Returns the list of handles and their common contests.

#### Example Response

```json
{
	"handles": ["tourist", "SecondBest"],
	"common_contests": [1234, 1235, 1236]
}
```

## API Documentation

Detailed API documentation is available when the server is running:

```
GET /
```

This provides a custom documentation page with detailed information about all endpoints.

For Swagger UI documentation:

```
GET /docs
```

## Error Handling

The API returns appropriate HTTP status codes:

- `200 OK`: Request successful
- `404 Not Found`: User not found
- `400 Bad Request`: Invalid request (e.g., no valid handles provided)

Error responses follow this format:

```json
{
	"detail": "User information not found for {handle}"
}
```

## Usage Examples

### Python

```python
import requests

username = "tourist"
response = requests.get(f"https://codeforces-stats.tashif.codes/{username}")
data = response.json()

print(f"{username} has a rating of {data['rating']} and rank {data['rank']}")
```

### JavaScript

```javascript
fetch(`https://codeforces-stats.tashif.codes/${username}`)
	.then((response) => response.json())
	.then((data) =>
		console.log(
			`${data.handle} has solved ${data.solved_problems_count} problems!`
		)
	);
```

## Installation

### Setup

1. Clone the repository

   ```bash
   git clone https://github.com/tashifkhan/CodeForces-API.git
   cd CodeForces-API
   ```

2. Create a virtual environment

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

4. Start the server
   ```bash
   uvicorn main:app --reload
   ```

The API will be available at `http://localhost:8000`.

## Usage Notes

Please use this API responsibly and consider CodeForces' rate limits when making requests. The API respects CodeForces' rate limiting of 1 request per 2 seconds.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License. See [LICENSE](LICENSE) for more information.
