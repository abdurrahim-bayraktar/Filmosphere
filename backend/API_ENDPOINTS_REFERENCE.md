# API Endpoints Quick Reference

Complete list of all API endpoints for frontend developers.

## 🔐 Authentication

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | `/api/auth/register/` | No | Register new user |
| POST | `/api/auth/login/` | No | Login user |
| POST | `/api/auth/token/refresh/` | No | Refresh access token |
| GET | `/api/users/me/` | Yes | Get current user |

## 👤 User Profiles

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/api/users/{username}/` | No | Get user profile |
| GET | `/api/users/{username}/ratings/` | No | Get user's ratings |
| GET | `/api/users/{username}/reviews/` | No | Get user's reviews |
| GET | `/api/users/{username}/lists/` | No | Get user's lists |
| GET | `/api/users/{username}/badges` | No | Get user's badges |

## 🔍 Film Search & Details

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/api/search?q={query}` | No | Search films |
| POST | `/api/search/graphql` | No | GraphQL search |
| GET | `/api/films/{imdb_id}` | Optional | Get film details |

## ⭐ Ratings (FR10)

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | `/api/films/{imdb_id}/rate` | Yes | Create/update rating |
| GET | `/api/films/{imdb_id}/rate` | Yes | Get your rating |
| DELETE | `/api/films/{imdb_id}/rate` | Yes | Delete your rating |
| GET | `/api/films/{imdb_id}/ratings` | No | Get all ratings for film |

## 😊 Mood Tracking (FR09)

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | `/api/films/{imdb_id}/mood` | Yes | Log mood before/after |
| GET | `/api/films/{imdb_id}/mood` | Yes | Get your mood log |

## 📺 Watched Films

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | `/api/films/{imdb_id}/watched` | Yes | Mark film as watched |
| DELETE | `/api/films/{imdb_id}/unwatched` | Yes | Mark film as unwatched |
| GET | `/api/films/{imdb_id}/watched-status` | Yes | Check if film is watched |
| GET | `/api/users/{username}/watched` | No | Get user's watched films |

## 💬 Reviews/Comments (FR06)

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | `/api/films/{imdb_id}/reviews/create` | Yes | Create review (auto-moderated) |
| GET | `/api/films/{imdb_id}/reviews` | No | Get all reviews (spoilers hidden, rejected filtered) |
| GET | `/api/films/{imdb_id}/reviews?show_spoiler=true` | No | Get reviews with spoilers |
| GET | `/api/reviews/{review_id}` | Yes | Get review details |
| PUT | `/api/reviews/{review_id}` | Yes | Update your review |
| DELETE | `/api/reviews/{review_id}` | Yes | Delete your review |
| POST | `/api/reviews/{review_id}/like` | Yes | Like/unlike review |
| POST | `/api/reviews/{review_id}/flag` | Yes | Flag comment for review |
| DELETE | `/api/reviews/{review_id}/unflag` | Yes | Remove flag from comment |

## 🛡️ Comment Moderation (Admin)

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/api/admin/reviews/flagged?status={status}` | Yes (Staff) | Get flagged comments |
| POST | `/api/admin/reviews/{review_id}/moderate` | Yes (Staff) | Approve/reject comment |

## 📋 Lists (FR03)

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/api/lists/` | Yes | Get all lists (yours + public) |
| POST | `/api/lists/create/` | Yes | Create new list |
| GET | `/api/lists/{list_id}` | Yes | Get list details |
| PUT | `/api/lists/{list_id}` | Yes | Update your list |
| DELETE | `/api/lists/{list_id}` | Yes | Delete your list |
| POST | `/api/lists/{list_id}/films` | Yes | Add film to list |
| DELETE | `/api/lists/{list_id}/films/{imdb_id}` | Yes | Remove film from list |

## 👥 Following System

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | `/api/users/{username}/follow` | Yes | Follow user |
| DELETE | `/api/users/{username}/follow` | Yes | Unfollow user |
| GET | `/api/users/{username}/followers` | No | Get user's followers |
| GET | `/api/users/{username}/following` | No | Get users being followed |
| GET | `/api/users/{username}/follow-status` | Yes | Check follow status |

## 🏆 Badge System (FR05)

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/api/badges/` | No | Get all badges |
| GET | `/api/badges/?is_custom=true` | No | Get custom badges only |
| GET | `/api/badges/progress` | Yes | Get your badge progress |
| GET | `/api/users/{username}/badges` | No | Get user's earned badges |
| POST | `/api/badges/create` | Yes | Create custom badge |
| POST | `/api/badges/award` | Yes | Manually check badges |

## 🎬 Recommendations (FR11)

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/api/recommendations/` | Yes | Get personalized recommendations |

## 🎥 Film Media

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/api/films/{imdb_id}/trailer` | No | Get trailer |
| GET | `/api/films/{imdb_id}/streaming` | No | Get streaming sources |

## 📊 IMDb Extended API

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/api/films/{imdb_id}/credits` | No | Get cast & crew |
| GET | `/api/films/{imdb_id}/release-dates` | No | Get release dates |
| GET | `/api/films/{imdb_id}/akas` | No | Get alternate titles |
| GET | `/api/films/{imdb_id}/seasons` | No | Get season count (TV) |
| GET | `/api/films/{imdb_id}/episodes` | No | Get episodes (TV) |
| GET | `/api/films/{imdb_id}/images` | No | Get images |
| GET | `/api/films/{imdb_id}/videos` | No | Get videos |
| GET | `/api/films/{imdb_id}/award-nominations` | No | Get award nominations |
| GET | `/api/films/{imdb_id}/parents-guide` | No | Get parents guide |
| GET | `/api/films/{imdb_id}/certificates` | No | Get certificates |
| GET | `/api/films/{imdb_id}/company-credits` | No | Get company credits |
| GET | `/api/films/{imdb_id}/box-office` | No | Get box office data |

## 🎞️ KinoCheck Extended API

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/api/kinocheck/trailers/latest` | No | Get latest trailers |
| GET | `/api/kinocheck/trailers/trending` | No | Get trending trailers |
| GET | `/api/kinocheck/trailers?genres={genre}` | No | Get trailers by genre |
| GET | `/api/kinocheck/movies?id={movie_id}` | No | Get movie by KinoCheck ID |

---

## 📝 Request/Response Examples

### Rating a Film
**Request**:
```http
POST /api/films/tt1375666/rate
Authorization: Bearer {token}
Content-Type: application/json

{
  "overall_rating": 5,
  "plot_rating": 5,
  "acting_rating": 4
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "user": 1,
  "username": "johndoe",
  "film": "uuid-here",
  "film_title": "Inception",
  "film_imdb_id": "tt1375666",
  "overall_rating": 5,
  "plot_rating": 5,
  "acting_rating": 4,
  "cinematography_rating": null,
  "soundtrack_rating": null,
  "originality_rating": null,
  "direction_rating": null,
  "rated_at": "2025-12-06T12:00:00Z"
}
```

### Creating a Review with Spoiler
**Request**:
```http
POST /api/films/tt1375666/reviews/create
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Mind-blowing!",
  "content": "The ending twist was incredible!",
  "rating": 5,
  "is_spoiler": false
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "username": "johndoe",
  "film_title": "Inception",
  "film_imdb_id": "tt1375666",
  "title": "Mind-blowing!",
  "content": "[SPOILER - Click to reveal]",  // Hidden if auto-detected
  "rating": 5,
  "likes_count": 0,
  "is_liked": false,
  "is_spoiler": false,
  "is_auto_detected_spoiler": true,
  "contains_spoiler": true,
  "moderation_status": "approved",
  "flagged_count": 0,
  "created_at": "2025-12-06T12:00:00Z"
}
```

**Note**: Comments are automatically moderated. If blacklisted words are detected or LLM flags content, `moderation_status` will be set to "pending" for admin review.

### Flagging a Comment
**Request**:
```http
POST /api/reviews/1/flag
Authorization: Bearer {token}
Content-Type: application/json

{
  "reason": "inappropriate",
  "description": "This comment contains offensive content"
}
```

**Response** (201 Created):
```json
{
  "detail": "Comment flagged successfully.",
  "flag_id": 1
}
```

### Admin Moderating a Comment
**Request**:
```http
POST /api/admin/reviews/1/moderate
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "action": "approve",
  "reason": "Content is appropriate"
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "moderation_status": "approved",
  "moderation_reason": "Content is appropriate",
  "moderated_at": "2025-12-06T12:00:00Z",
  "moderated_by": 1,
  ...
}
```

### Following a User
**Request**:
```http
POST /api/users/janedoe/follow
Authorization: Bearer {token}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "follower": 1,
  "follower_username": "johndoe",
  "following": 2,
  "following_username": "janedoe",
  "created_at": "2025-12-06T12:00:00Z"
}
```

---

## 🔑 Authentication Header Format

All authenticated requests require:
```
Authorization: Bearer {access_token}
```

Example:
```javascript
fetch('http://localhost:8000/api/films/tt1375666/rate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  },
  body: JSON.stringify({ overall_rating: 5 })
});
```

---

## 📊 Response Status Codes

- **200 OK**: Success
- **201 Created**: Resource created
- **204 No Content**: Success (delete operations)
- **400 Bad Request**: Invalid input
- **401 Unauthorized**: Missing/invalid token
- **403 Forbidden**: Not allowed
- **404 Not Found**: Resource doesn't exist
- **500 Internal Server Error**: Server error

---

## 🎯 Common Use Cases

### 1. User Dashboard
- Get current user: `GET /api/users/me/`
- Get user's ratings: `GET /api/users/{username}/ratings/`
- Get user's watched films: `GET /api/users/{username}/watched`
- Get user's badges: `GET /api/users/{username}/badges`
- Get user's lists: `GET /api/users/{username}/lists/`

### 2. Film Page
- Get film details: `GET /api/films/{imdb_id}`
- Get ratings: `GET /api/films/{imdb_id}/ratings`
- Get reviews: `GET /api/films/{imdb_id}/reviews`
- Check if watched: `GET /api/films/{imdb_id}/watched-status`
- Mark as watched: `POST /api/films/{imdb_id}/watched`
- Get trailer: `GET /api/films/{imdb_id}/trailer`
- Get streaming: `GET /api/films/{imdb_id}/streaming`

### 3. User Profile Page
- Get profile: `GET /api/users/{username}/`
- Get followers: `GET /api/users/{username}/followers`
- Get following: `GET /api/users/{username}/following`
- Get badges: `GET /api/users/{username}/badges`
- Check follow status: `GET /api/users/{username}/follow-status`

---

## 💡 Tips for Frontend Developers

1. **Store Token Securely**: Use localStorage, sessionStorage, or httpOnly cookies
2. **Handle Token Expiry**: Implement token refresh logic
3. **Show Loading States**: API calls may take time, especially spoiler detection
4. **Handle Errors Gracefully**: Show user-friendly error messages
5. **Use Query Parameters**: For filtering (e.g., `?show_spoiler=true`, `?is_custom=false`)
6. **Cache Responses**: Film details don't change often, cache them
7. **Optimistic Updates**: Update UI immediately, sync with backend

---

For detailed examples, see `FRONTEND_DEVELOPER_GUIDE.md`

