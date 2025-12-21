# Frontend Developer Guide - Filmosphere API

This guide will help frontend developers integrate with the Filmosphere backend API.

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Authentication](#authentication)
3. [API Base URL](#api-base-url)
4. [Core Features Overview](#core-features-overview)
5. [Feature-by-Feature Guide](#feature-by-feature-guide)
6. [Postman Collection](#postman-collection)
7. [Common Patterns](#common-patterns)
8. [Error Handling](#error-handling)

---

## 🚀 Getting Started

### Prerequisites
- Backend running on `http://localhost:8000` (or configured base URL)
- Postman collection for testing (optional but recommended)

### Quick Start
1. **Start the Backend**:
   ```bash
   cd backend
   docker-compose up -d
   ```

2. **Verify Backend is Running**:
   ```bash
   curl http://localhost:8000/api/search?q=inception
   ```

3. **Import Postman Collection**:
   - Import `Filmosphere_Complete_API.postman_collection.json` into Postman
   - Set `base_url` variable to `http://localhost:8000`

---

## 🔐 Authentication

### Authentication Flow

The API uses **JWT (JSON Web Tokens)** for authentication.

#### 1. Register a New User
```http
POST /api/auth/register/
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepass123",
  "password_confirm": "securepass123",
  "display_name": "John Doe"
}
```

**Response** (201 Created):
```json
{
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com"
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

#### 2. Login
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "johndoe",
  "password": "securepass123"
}
```

**Response** (200 OK):
```json
{
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

#### 3. Using the Access Token

For all authenticated endpoints, include the token in the Authorization header:

```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

#### 4. Refresh Token (when access token expires)
```http
POST /api/auth/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response**:
```json
{
  "access": "new_access_token_here"
}
```

---

## 🌐 API Base URL

- **Development**: `http://localhost:8000`
- **Production**: Configure based on deployment

All endpoints are prefixed with `/api/`

### ⚠️ Important: Always Use Backend Endpoints

**Frontend developers should ALWAYS use the backend API endpoints, NOT call external APIs (IMDb, KinoCheck, etc.) directly.**

**Why?**
1. **Security**: API keys are stored securely on the backend, never exposed to frontend
2. **Consistency**: All data flows through the backend, ensuring consistent format
3. **Caching**: Backend implements caching to reduce external API calls
4. **Rate Limiting**: Backend protects against API rate limits
5. **Error Handling**: Centralized error handling and fallbacks
6. **Future Features**: Easy to add analytics, logging, or custom logic
7. **CORS**: No CORS issues when calling external APIs
8. **Maintainability**: Single point of change if external APIs change

**❌ DON'T do this:**
```javascript
// BAD - Never expose API keys in frontend!
const response = await fetch('https://api.imdbapi.dev/search/titles?query=inception&apiKey=YOUR_KEY');
```

**✅ DO this:**
```javascript
// GOOD - Use backend endpoint
const response = await fetch('http://localhost:8000/api/search?q=inception');
```

---

## 📚 Core Features Overview

### Available Features

1. **Authentication & User Profiles**
   - Register, Login, Profile management

2. **Film Search & Details**
   - Search films, Get film details, Trailers, Streaming info

3. **Ratings System (FR10)**
   - Multi-aspect ratings (Plot, Acting, Cinematography, etc.)
   - Overall rating (auto-calculated from aspects or manual)

4. **Mood Tracking (FR09)**
   - Log mood before/after watching films

5. **Reviews/Comments**
   - Write reviews, Like reviews
   - **Spoiler Protection (FR06)** - Auto-detected and manual spoiler marking

6. **Lists (FR03)**
   - Create custom film lists
   - Add/remove films from lists

7. **Following System**
   - Follow/unfollow users
   - Get followers and following lists

8. **Badge System (FR05)**
   - Earn badges based on activity
   - Create custom challenges

9. **Recommendations (FR11)**
   - Get personalized film recommendations

10. **Extended APIs**
    - IMDb Extended API (credits, images, videos, etc.)
    - KinoCheck Extended API (trailers, trending)

---

## 🎯 Feature-by-Feature Guide

### 1. Film Search

**Search for Films**:
```http
GET /api/search?q=inception
```

**Response**:
```json
{
  "results": [
    {
      "imdb_id": "tt1375666",
      "title": "Inception",
      "year": 2010,
      "image": "https://...",
      "type": "movie"
    }
  ]
}
```

**Usage in Frontend**:

#### Basic JavaScript/React Example

```javascript
// Simple fetch function
const searchFilms = async (query) => {
  try {
    const response = await fetch(
      `http://localhost:8000/api/search?q=${encodeURIComponent(query)}`
    );
    if (!response.ok) {
      throw new Error('Search failed');
    }
    const data = await response.json();
    return data.results; // Array of film objects
  } catch (error) {
    console.error('Search error:', error);
    return [];
  }
};
```

#### Complete React Component with Debouncing

```jsx
import React, { useState, useEffect, useCallback } from 'react';

const API_BASE_URL = 'http://localhost:8000';

const FilmSearch = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Debounced search function
  const debouncedSearch = useCallback(
    debounce(async (searchQuery) => {
      if (!searchQuery.trim()) {
        setResults([]);
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const response = await fetch(
          `${API_BASE_URL}/api/search?q=${encodeURIComponent(searchQuery)}`
        );

        if (!response.ok) {
          throw new Error(`Search failed: ${response.statusText}`);
        }

        const data = await response.json();
        setResults(data.results || []);
      } catch (err) {
        setError(err.message);
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 300), // 300ms debounce delay
    []
  );

  useEffect(() => {
    debouncedSearch(query);
  }, [query, debouncedSearch]);

  const handleFilmClick = (imdbId) => {
    // Navigate to film detail page
    window.location.href = `/films/${imdbId}`;
  };

  return (
    <div className="film-search">
      <input
        type="text"
        placeholder="Search for films..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="search-input"
      />

      {loading && <div className="loading">Searching...</div>}
      {error && <div className="error">Error: {error}</div>}

      {!loading && !error && results.length === 0 && query && (
        <div className="no-results">No films found</div>
      )}

      <div className="results">
        {results.map((film) => (
          <div
            key={film.imdb_id}
            className="film-card"
            onClick={() => handleFilmClick(film.imdb_id)}
          >
            {film.image && (
              <img src={film.image} alt={film.title} className="film-poster" />
            )}
            <div className="film-info">
              <h3>{film.title}</h3>
              <p>{film.year} • {film.type}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Simple debounce helper function
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

export default FilmSearch;
```

#### Using Axios (Alternative)

```javascript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const searchFilms = async (query) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/search`, {
      params: { q: query }
    });
    return response.data.results;
  } catch (error) {
    console.error('Search error:', error);
    return [];
  }
};
```

#### TypeScript Types

```typescript
interface SearchResult {
  imdb_id: string;      // e.g., "tt1375666"
  title: string;        // e.g., "Inception"
  year: number | null;  // e.g., 2010
  image: string | null; // Poster URL
  type: string;         // "movie" or "tvSeries"
}

interface SearchResponse {
  query: string;
  results: SearchResult[];
}
```

#### TypeScript React Component Example

```tsx
import React, { useState, useEffect, useCallback } from 'react';

const API_BASE_URL = 'http://localhost:8000';

interface SearchResult {
  imdb_id: string;
  title: string;
  year: number | null;
  image: string | null;
  type: string;
}

interface SearchResponse {
  query: string;
  results: SearchResult[];
}

const FilmSearch: React.FC = () => {
  const [query, setQuery] = useState<string>('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const searchFilms = useCallback(async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      setResults([]);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/search?q=${encodeURIComponent(searchQuery)}`
      );

      if (!response.ok) {
        throw new Error(`Search failed: ${response.statusText}`);
      }

      const data: SearchResponse = await response.json();
      setResults(data.results || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, []);

  // Debounce effect
  useEffect(() => {
    const timer = setTimeout(() => {
      searchFilms(query);
    }, 300);

    return () => clearTimeout(timer);
  }, [query, searchFilms]);

  return (
    <div>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search films..."
      />
      {loading && <p>Loading...</p>}
      {error && <p>Error: {error}</p>}
      <ul>
        {results.map((film) => (
          <li key={film.imdb_id}>
            {film.title} ({film.year})
          </li>
        ))}
      </ul>
    </div>
  );
};

export default FilmSearch;
```

#### Best Practices

1. **Debounce Search Input**: Wait 300-500ms after user stops typing before searching
2. **Handle Empty Queries**: Don't search if query is empty or too short (< 2 characters)
3. **Loading States**: Show loading indicator while searching
4. **Error Handling**: Display user-friendly error messages
5. **Image Fallbacks**: Handle cases where `image` is `null`
6. **Navigate to Details**: Use `imdb_id` to navigate to film detail page (`/api/films/{imdb_id}`)

---

### 2. Film Details

**Get Film Details**:
```http
GET /api/films/tt1375666
Authorization: Bearer {token}  // Optional - adds user's rating if authenticated
```

**Response**:
```json
{
  "imdb_id": "tt1375666",
  "title": "Inception",
  "year": 2010,
  "metadata": {...},
  "rating_statistics": {
    "overall": 4.5,
    "plot": 4.7,
    "acting": 4.6,
    "total_ratings": 150
  },
  "user_rating": {
    "overall_rating": 5,
    "plot_rating": 5,
    ...
  }  // Only if authenticated
}
```

---

### 3. Rating a Film (FR10)

**Rate with Overall Rating Only**:
```http
POST /api/films/tt1375666/rate
Authorization: Bearer {token}
Content-Type: application/json

{
  "overall_rating": 5
}
```

**Rate with Aspect Ratings Only** (overall calculated automatically):
```http
POST /api/films/tt1375666/rate
Authorization: Bearer {token}
Content-Type: application/json

{
  "plot_rating": 5,
  "acting_rating": 4,
  "cinematography_rating": 5,
  "soundtrack_rating": 5,
  "originality_rating": 5,
  "direction_rating": 5
}
```

**Rate with Both**:
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

**Note**: If aspect ratings are provided, overall is calculated as average. If only overall is provided, it's used as-is.

**Get User's Rating**:
```http
GET /api/films/tt1375666/rate
Authorization: Bearer {token}
```

**Delete Rating**:
```http
DELETE /api/films/tt1375666/rate
Authorization: Bearer {token}
```

---

### 4. Watched Films

**Mark Film as Watched**:
```http
POST /api/films/tt1375666/watched
Authorization: Bearer {token}
```

**Response** (201 Created or 200 OK):
```json
{
  "id": 1,
  "user": 1,
  "username": "johndoe",
  "film": "uuid-here",
  "film_title": "Inception",
  "film_imdb_id": "tt1375666",
  "film_year": 2010,
  "film_poster_url": "https://...",
  "watched_at": "2025-12-06T12:00:00Z",
  "updated_at": "2025-12-06T12:00:00Z"
}
```

**Mark Film as Unwatched**:
```http
DELETE /api/films/tt1375666/unwatched
Authorization: Bearer {token}
```

**Check if Film is Watched**:
```http
GET /api/films/tt1375666/watched-status
Authorization: Bearer {token}
```

**Response**:
```json
{
  "is_watched": true,
  "watched_at": "2025-12-06T12:00:00Z"
}
```

**Get User's Watched Films**:
```http
GET /api/users/johndoe/watched
```

**Response**:
```json
{
  "count": 25,
  "results": [
    {
      "id": 1,
      "film_title": "Inception",
      "film_imdb_id": "tt1375666",
      "film_year": 2010,
      "film_poster_url": "https://...",
      "watched_at": "2025-12-06T12:00:00Z"
    }
  ]
}
```

**Note**: Marking a film as watched automatically checks and awards badges (e.g., "Film Enthusiast" for watching 10 films).

---

### 5. Mood Tracking (FR09)

**Log Mood Before Watching**:
```http
POST /api/films/tt1375666/mood
Authorization: Bearer {token}
Content-Type: application/json

{
  "mood_before": "excited"
}
```

**Log Mood After Watching**:
```http
POST /api/films/tt1375666/mood
Authorization: Bearer {token}
Content-Type: application/json

{
  "mood_before": "excited",
  "mood_after": "happy"
}
```

**Available Moods**: `happy`, `sad`, `excited`, `calm`, `anxious`, `bored`, `energetic`, `relaxed`, `stressed`, `neutral`

**Get User's Mood for Film**:
```http
GET /api/films/tt1375666/mood
Authorization: Bearer {token}
```

---

### 6. Reviews/Comments with Spoiler Protection (FR06)

**Create Review (Auto-Detects Spoilers & Auto-Moderates)**:
```http
POST /api/films/tt1375666/reviews/create
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Amazing film!",
  "content": "The ending was shocking!",
  "rating": 5
}
```

**Note**: Comments are automatically:
- Checked for spoilers (LLM-based)
- Moderated for blacklisted words and inappropriate content (LLM-based)
- Set to "pending" if flagged, "approved" if clean

**Create Review (Manually Mark as Spoiler)**:
```http
POST /api/films/tt1375666/reviews/create
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Spoiler Alert!",
  "content": "I can't believe the main character dies!",
  "rating": 4,
  "is_spoiler": true
}
```

**Get Reviews (Spoilers Hidden by Default, Rejected Comments Hidden)**:
```http
GET /api/films/tt1375666/reviews
```

**Response**:
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "username": "johndoe",
      "title": "Great film!",
      "content": "[SPOILER - Click to reveal]",  // Hidden if contains_spoiler is true
      "contains_spoiler": true,
      "is_spoiler": false,
      "is_auto_detected_spoiler": true,
      "moderation_status": "approved",
      "flagged_count": 0,
      "rating": 5,
      "likes_count": 3,
      "is_liked": false
    }
  ]
}
```

**Get Reviews (Show Spoilers)**:
```http
GET /api/films/tt1375666/reviews?show_spoiler=true
```

**Flag a Comment**:
```http
POST /api/reviews/1/flag
Authorization: Bearer {token}
Content-Type: application/json

{
  "reason": "inappropriate",
  "description": "This comment contains offensive content"
}
```

**Available Flag Reasons**: `spam`, `inappropriate`, `harassment`, `hate_speech`, `other`

**Unflag a Comment**:
```http
DELETE /api/reviews/1/unflag
Authorization: Bearer {token}
```

**Like a Review**:
```http
POST /api/reviews/1/like
Authorization: Bearer {token}
```

**Get All Reviews for a Film**:
```http
GET /api/films/tt1375666/reviews
```

**Note**: Rejected comments are automatically hidden from public view. Only approved or pending comments are shown.

---

### 7. Lists (FR03)

**Create a List**:
```http
POST /api/lists/create/
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "My Top 10 Horror Films",
  "description": "A curated list of my favorite horror movies",
  "is_public": true
}
```

**Get All Lists** (your lists + public lists):
```http
GET /api/lists/
Authorization: Bearer {token}
```

**Get List Details**:
```http
GET /api/lists/1
Authorization: Bearer {token}
```

**Update List**:
```http
PUT /api/lists/1
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Updated Title",
  "description": "Updated description",
  "is_public": false
}
```

**Delete List**:
```http
DELETE /api/lists/1
Authorization: Bearer {token}
```

**Add Film to List**:
```http
POST /api/lists/1/films
Authorization: Bearer {token}
Content-Type: application/json

{
  "imdb_id": "tt1375666"
}
```

**Remove Film from List**:
```http
DELETE /api/lists/1/films/tt1375666
Authorization: Bearer {token}
```

**Get User's Lists**:
```http
GET /api/users/johndoe/lists/
```

---

### 8. Following System

**Follow a User**:
```http
POST /api/users/johndoe/follow
Authorization: Bearer {token}
```

**Unfollow a User**:
```http
DELETE /api/users/johndoe/follow
Authorization: Bearer {token}
```

**Get User's Followers**:
```http
GET /api/users/johndoe/followers
```

**Get Users User is Following**:
```http
GET /api/users/johndoe/following
```

**Check Follow Status**:
```http
GET /api/users/johndoe/follow-status
Authorization: Bearer {token}
```

**Response**:
```json
{
  "is_following": true,
  "followers_count": 25,
  "following_count": 10
}
```

---

### 9. Badge System (FR05)

**Get All Badges**:
```http
GET /api/badges/
```

**Filter Badges**:
```http
GET /api/badges/?is_custom=false  // Only default badges
GET /api/badges/?is_custom=true   // Only custom badges
```

**Get User's Badges**:
```http
GET /api/users/johndoe/badges
```

**Get Your Badge Progress**:
```http
GET /api/badges/progress
Authorization: Bearer {token}
```

**Response**:
```json
{
  "progress": [
    {
      "badge": 1,
      "badge_name": "Film Enthusiast",
      "current_value": 8,
      "required_value": 10,
      "progress_percentage": 80,
      "earned": false
    },
    {
      "badge": 2,
      "badge_name": "Critic",
      "current_value": 50,
      "required_value": 50,
      "progress_percentage": 100,
      "earned": true
    }
  ]
}
```

**Create Custom Badge/Challenge**:
```http
POST /api/badges/create
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Watch 100 Horror Films",
  "description": "Watch 100 horror films this year",
  "criteria_type": "films_watched",
  "criteria_value": 100,
  "icon_url": "https://example.com/icon.png"
}
```

**Manually Check Badges** (usually automatic):
```http
POST /api/badges/award
Authorization: Bearer {token}
```

---

### 10. Recommendations (FR11)

**Get Personalized Recommendations**:
```http
GET /api/recommendations/
Authorization: Bearer {token}
```

**Response**:
```json
{
  "recommendations": [
    {
      "film_title": "The Shawshank Redemption",
      "imdb_id": "tt0111161",
      "search_url": "/api/search?q=The+Shawshank+Redemption",
      "film_detail_url": "/api/films/tt0111161"
    }
  ],
  "total": 10,
  "message": "Generated 10 recommendations based on your preferences.",
  "based_on": {
    "ratings_count": 25,
    "moods_count": 10,
    "viewing_history_count": 30
  }
}
```

---

### 11. User Profile

**Get Current User**:
```http
GET /api/users/me/
Authorization: Bearer {token}
```

**Get User Profile**:
```http
GET /api/users/johndoe/
```

**Get User's Ratings**:
```http
GET /api/users/johndoe/ratings/
```

**Get User's Reviews**:
```http
GET /api/users/johndoe/reviews/
```

---

### 12. Comment Moderation (Admin)

**Get Flagged Comments**:
```http
GET /api/admin/reviews/flagged?status=pending
Authorization: Bearer {admin_token}
```

**Query Parameters**:
- `status=pending` - Only pending reviews
- `status=flagged` - Only flagged reviews (flagged_count > 0)
- `status=all` - All pending or flagged reviews

**Approve a Comment**:
```http
POST /api/admin/reviews/1/moderate
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "action": "approve",
  "reason": "Content is appropriate"
}
```

**Reject a Comment**:
```http
POST /api/admin/reviews/1/moderate
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "action": "reject",
  "reason": "Contains inappropriate content"
}
```

**Note**: Admin endpoints require staff permissions (`is_staff=True`). Rejected comments are hidden from public view.

---

## 📦 Postman Collection

### Using the Postman Collection

1. **Import Collection**:
   - Open Postman
   - Click "Import"
   - Select `Filmosphere_Complete_API.postman_collection.json`

2. **Set Variables**:
   - `base_url`: `http://localhost:8000`
   - `access_token`: (auto-saved after login/register)
   - `username`: Test username
   - `imdb_id`: Test IMDb ID (e.g., `tt0111161`)

3. **Test Authentication**:
   - Run "Register User" or "Login"
   - Token is automatically saved to `access_token` variable

4. **Test Features**:
   - All endpoints are organized in folders
   - Each request includes example data
   - Variables are used for consistency

---

## 🔄 Common Patterns

### 1. Making Authenticated Requests

```javascript
const makeAuthenticatedRequest = async (url, options = {}) => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(`http://localhost:8000/api${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...options.headers,
    },
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Request failed');
  }
  
  return response.json();
};

// Usage
const rateFilm = async (imdbId, rating) => {
  return makeAuthenticatedRequest(`/films/${imdbId}/rate`, {
    method: 'POST',
    body: JSON.stringify(rating),
  });
};
```

### 2. Handling Pagination

Most list endpoints return paginated results:

```javascript
const getFilmReviews = async (imdbId, page = 1) => {
  const response = await fetch(
    `http://localhost:8000/api/films/${imdbId}/reviews?page=${page}`
  );
  const data = await response.json();
  
  return {
    results: data.results,
    next: data.next,
    previous: data.previous,
    count: data.count,
  };
};
```

### 3. Handling Spoiler Toggle

```javascript
const getFilmReviews = async (imdbId, showSpoilers = false) => {
  const url = showSpoilers 
    ? `/api/films/${imdbId}/reviews?show_spoiler=true`
    : `/api/films/${imdbId}/reviews`;
  
  const response = await fetch(`http://localhost:8000${url}`);
  return response.json();
};

// In your component
const [showSpoilers, setShowSpoilers] = useState(false);
const reviews = await getFilmReviews(imdbId, showSpoilers);

// Toggle button
<button onClick={() => setShowSpoilers(!showSpoilers)}>
  {showSpoilers ? 'Hide Spoilers' : 'Show Spoilers'}
</button>
```

### 4. Real-time Badge Updates

Badges are automatically checked when users perform actions. To show progress:

```javascript
const checkBadgeProgress = async () => {
  const progress = await makeAuthenticatedRequest('/badges/progress');
  
  // Display progress bars
  progress.progress.forEach(badge => {
    console.log(`${badge.badge_name}: ${badge.progress_percentage}%`);
  });
};
```

---

## ⚠️ Error Handling

### Common HTTP Status Codes

- **200 OK**: Success
- **201 Created**: Resource created
- **400 Bad Request**: Invalid input
- **401 Unauthorized**: Missing or invalid token
- **403 Forbidden**: Not allowed (e.g., editing someone else's list)
- **404 Not Found**: Resource doesn't exist
- **500 Internal Server Error**: Server error

### Error Response Format

```json
{
  "detail": "Error message here"
}
```

Or for validation errors:

```json
{
  "field_name": ["Error message 1", "Error message 2"]
}
```

### Example Error Handling

```javascript
const handleApiError = async (response) => {
  if (!response.ok) {
    const error = await response.json();
    
    if (response.status === 401) {
      // Token expired, refresh or redirect to login
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    
    throw new Error(error.detail || 'An error occurred');
  }
  
  return response.json();
};
```

---

## 🎨 Frontend Integration Examples

### React Example: Film Rating Component

```jsx
import { useState } from 'react';

const FilmRating = ({ imdbId }) => {
  const [rating, setRating] = useState({
    overall_rating: null,
    plot_rating: null,
    acting_rating: null,
    // ... other aspects
  });

  const submitRating = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(
        `http://localhost:8000/api/films/${imdbId}/rate`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify(rating),
        }
      );
      
      if (response.ok) {
        const data = await response.json();
        console.log('Rating saved:', data);
        // Show success message
      }
    } catch (error) {
      console.error('Error rating film:', error);
    }
  };

  return (
    <form onSubmit={submitRating}>
      <label>Overall Rating:</label>
      <input
        type="number"
        min="1"
        max="5"
        value={rating.overall_rating || ''}
        onChange={(e) => setRating({
          ...rating,
          overall_rating: parseInt(e.target.value)
        })}
      />
      {/* Other rating fields */}
      <button type="submit">Submit Rating</button>
    </form>
  );
};
```

### React Example: Review with Spoiler Toggle

```jsx
const FilmReviews = ({ imdbId }) => {
  const [reviews, setReviews] = useState([]);
  const [showSpoilers, setShowSpoilers] = useState(false);

  useEffect(() => {
    const fetchReviews = async () => {
      const url = showSpoilers
        ? `http://localhost:8000/api/films/${imdbId}/reviews?show_spoiler=true`
        : `http://localhost:8000/api/films/${imdbId}/reviews`;
      
      const response = await fetch(url);
      const data = await response.json();
      setReviews(data.results);
    };

    fetchReviews();
  }, [imdbId, showSpoilers]);

  return (
    <div>
      <button onClick={() => setShowSpoilers(!showSpoilers)}>
        {showSpoilers ? 'Hide Spoilers' : 'Show Spoilers'}
      </button>
      
      {reviews.map(review => (
        <div key={review.id}>
          <h3>{review.title}</h3>
          <p>{review.content}</p>
          {review.contains_spoiler && (
            <span className="spoiler-badge">⚠️ Spoiler</span>
          )}
        </div>
      ))}
    </div>
  );
};
```

---

## 📝 Important Notes

### 1. Token Management
- Access tokens expire (default: 5 minutes)
- Use refresh tokens to get new access tokens
- Store tokens securely (localStorage, httpOnly cookies, etc.)

### 2. CORS
- Backend is configured to allow requests from:
  - `http://localhost:3000` (React default)
  - `http://localhost:5173` (Vite default)
- Update `CORS_ALLOWED_ORIGINS` in settings for production

### 3. Rate Limiting
- Anonymous users: 60 requests/minute
- Authenticated users: No limit (can be configured)

### 4. Badge Auto-Awarding
Badges are automatically checked when:
- User rates a film
- User creates a review
- User creates a list
- User follows someone

No need to manually trigger badge checking in most cases.

### 5. Spoiler Detection
- Automatic spoiler detection uses DeepSeek LLM API
- Requires `DEEPSEEK_API_KEY` to be configured
- Falls back gracefully if API is unavailable

---

## 🔗 Quick Reference

### Essential Endpoints

| Feature | Method | Endpoint |
|---------|--------|----------|
| Register | POST | `/api/auth/register/` |
| Login | POST | `/api/auth/login/` |
| Search Films | GET | `/api/search?q={query}` |
| Film Details | GET | `/api/films/{imdb_id}` |
| Rate Film | POST | `/api/films/{imdb_id}/rate` |
| Create Review | POST | `/api/films/{imdb_id}/reviews/create` |
| Get Reviews | GET | `/api/films/{imdb_id}/reviews` |
| Create List | POST | `/api/lists/create/` |
| Follow User | POST | `/api/users/{username}/follow` |
| Get Badges | GET | `/api/users/{username}/badges` |
| Get Recommendations | GET | `/api/recommendations/` |

---

## 🆘 Support

For questions or issues:
1. Check the Postman collection for examples
2. Review API responses for error details
3. Check backend logs: `docker-compose logs web`

---

## 📚 Additional Resources

- **Postman Collection**: `Filmosphere_Complete_API.postman_collection.json`
- **Backend Verification**: `BACKEND_VERIFICATION.md`
- **New Features Summary**: `NEW_FEATURES_SUMMARY.md`

Happy coding! 🎬

