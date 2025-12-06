# Filmosphere Backend - Project Structure

Complete guide to the project structure, explaining what each file and directory is for.

## 📁 Project Overview

This is a **Django REST Framework** backend API for a Letterboxd-like film social platform. The project follows Django's app-based architecture with a clear separation of concerns.

```
backend/
├── films/              # Main app for film-related features
├── users/              # User authentication and profiles
├── core/               # Shared services and utilities
├── api/                # API routing layer
├── filmosphere/        # Django project settings
├── docs/               # API documentation
├── staticfiles/        # Static files (admin, DRF)
└── [config files]      # Docker, requirements, etc.
```

---

## 🎬 Core Applications

### `/backend/films/` - Film Application

The main application handling all film-related features.

#### **`models.py`**
- **Purpose**: Database models (Django ORM)
- **Contains**:
  - `Film`: Cached film data from external APIs
  - `Rating`: Multi-aspect rating system (FR10)
  - `Mood`: Mood tracking before/after watching (FR09)
  - `List`: Custom film lists (FR03)
  - `ListItem`: Films in lists
  - `Review`: User reviews/comments with spoiler protection (FR06) and moderation
  - `ReviewLike`: Review likes
  - `CommentFlag`: User flags for comments requiring moderation
  - `Badge`: Badge definitions (FR05)
  - `UserBadge`: Badges earned by users

#### **`views.py`**
- **Purpose**: API endpoints (request handlers)
- **Contains**: All view classes handling HTTP requests
  - Film search, details, ratings, reviews
  - Lists management
  - Mood tracking
  - Recommendations
  - Following system
  - Badge system
  - Extended IMDb/KinoCheck APIs
- **Size**: ~1400 lines (main API logic)

#### **`serializers.py`**
- **Purpose**: Data validation and transformation
- **Contains**: DRF serializers for all models
  - Input validation
  - Response formatting
  - Read-only fields
  - Nested serializers
- **Key Serializers**:
  - `RatingSerializer`, `ReviewSerializer`
  - `ListSerializer`, `BadgeSerializer`
  - `FollowSerializer`, `UserBadgeSerializer`

#### **`urls.py`**
- **Purpose**: URL routing for film endpoints
- **Contains**: All URL patterns for film-related endpoints
  - Film details, ratings, reviews
  - Lists, recommendations
  - Extended API endpoints

#### **`admin.py`**
- **Purpose**: Django admin interface configuration
- **Contains**: Admin classes for all models
  - Custom list displays, filters, search
  - Makes models manageable via `/admin/`

#### **`services/`** - Business Logic Layer
- **`film_aggregator.py`**: Aggregates data from multiple APIs (IMDb, KinoCheck, Watchmode)
- **`film_cache.py`**: Manages film data caching
- **`badge_service.py`**: Badge checking and awarding logic (FR05)

#### **`migrations/`**
- **Purpose**: Database schema changes
- **Contains**: Migration files for model changes
  - `0001_initial.py`: Initial Film model
  - `0002_rating.py`: Rating model
  - `0003_mood.py`: Mood model
  - `0004_*`: Lists, Reviews, ReviewLikes
  - `0005_*`: Spoiler fields

#### **`tests/`**
- **Purpose**: Unit and integration tests
- **Contains**: Test files for services and views

---

### `/backend/users/` - User Application

Handles user authentication, profiles, and following.

#### **`models.py`**
- **Purpose**: User-related models
- **Contains**:
  - `UserProfile`: Extended user profile (bio, favorites, etc.)
  - `Follow`: Following relationships between users

#### **`views.py`**
- **Purpose**: User authentication and profile views
- **Contains**:
  - `RegisterView`: User registration
  - `login_view`: User login (JWT)
  - `UserProfileView`: Get/update user profile
  - `current_user_view`: Get current authenticated user

#### **`serializers.py`**
- **Purpose**: User data serialization
- **Contains**: Serializers for user registration and profiles

#### **`urls.py`**
- **Purpose**: User-related URL routing
- **Contains**: Authentication and profile endpoints
  - `/api/auth/register/`, `/api/auth/login/`
  - `/api/users/me/`, `/api/users/{username}/`

#### **`admin.py`**
- **Purpose**: Admin interface for user models
- **Contains**: Admin configurations for UserProfile and Follow

#### **`migrations/`**
- **Purpose**: User model migrations
- **Contains**: Migration files for UserProfile and Follow models

---

### `/backend/core/` - Shared Core

Reusable services and utilities used across the application.

#### **`services/`** - External API Services

##### **`http_client.py`**
- **Purpose**: HTTP client wrapper with retry logic
- **Features**:
  - Retry on failures
  - Timeout handling
  - GET and POST methods
- **Used by**: All external API services

##### **`imdb_service.py`**
- **Purpose**: IMDb API integration
- **Methods**:
  - `search()`: Search films
  - `get_metadata()`: Get film details
  - `get_credits()`, `get_images()`, `get_videos()`, etc.
  - `search_movies_graphql()`: GraphQL search

##### **`kinocheck_service.py`**
- **Purpose**: KinoCheck API integration (trailers)
- **Methods**:
  - `get_trailer()`: Get trailer for film
  - `get_latest_trailers()`: Latest trailers
  - `get_trending_trailers()`: Trending trailers
  - `get_trailers_by_genre()`: Trailers by genre
  - `get_movie_by_id()`: Movie by KinoCheck ID

##### **`watchmode_service.py`**
- **Purpose**: Watchmode API integration (streaming)
- **Methods**:
  - `lookup_title_id()`: Find Watchmode ID
  - `get_streaming_sources()`: Get streaming platforms

##### **`deepseek_service.py`**
- **Purpose**: DeepSeek LLM API integration
- **Methods**:
  - `get_recommendations()`: Generate film recommendations (FR11)
  - `check_spoiler()`: Detect spoilers in comments (FR06)

#### **`utils/`** - Utility Functions
- **`decorators.py`**: Custom decorators
- **`logging.py`**: Logging configuration

---

### `/backend/api/` - API Routing Layer

#### **`urls.py`**
- **Purpose**: Main API URL routing
- **Contains**: Routes requests to appropriate apps
  - `/api/search` → SearchView
  - `/api/` → films.urls
  - `/api/auth/` → users.urls

---

### `/backend/filmosphere/` - Django Project Configuration

Main Django project settings and configuration.

#### **`settings.py`**
- **Purpose**: Django project settings
- **Contains**:
  - Installed apps
  - Database configuration
  - REST Framework settings
  - JWT authentication
  - CORS settings
  - API keys (IMDb, KinoCheck, DeepSeek, Watchmode)
  - Timeout and retry settings

#### **`urls.py`**
- **Purpose**: Root URL configuration
- **Contains**: Main URL routing
  - `/admin/` → Django admin
  - `/api/schema/` → OpenAPI schema
  - `/api/docs/` → Swagger UI
  - `/api/` → api.urls

#### **`wsgi.py`**
- **Purpose**: WSGI application entry point
- **Used for**: Production deployment (Gunicorn, uWSGI)

#### **`asgi.py`**
- **Purpose**: ASGI application entry point
- **Used for**: Async deployment (Daphne)

---

## 📄 Configuration Files

### **`manage.py`**
- **Purpose**: Django management script
- **Usage**: Run Django commands
  - `python manage.py runserver`
  - `python manage.py migrate`
  - `python manage.py createsuperuser`

### **`requirements.txt`**
- **Purpose**: Python dependencies
- **Contains**: All required packages
  - Django, DRF, JWT, CORS, httpx, etc.

### **`pytest.ini`**
- **Purpose**: Pytest configuration
- **Used for**: Running tests

### **`Dockerfile`**
- **Purpose**: Docker image definition
- **Contains**: Instructions to build backend container
  - Python 3.11 base
  - Dependencies installation
  - Application setup

### **`docker-compose.yml`**
- **Purpose**: Docker Compose configuration
- **Contains**: Service definitions
  - `postgres`: PostgreSQL database
  - `web`: Django application
  - Volumes, networks, health checks

### **`docker-entrypoint.sh`**
- **Purpose**: Container startup script
- **Contains**: Initialization logic
  - Wait for database
  - Run migrations
  - Collect static files
  - Start server

### **`.dockerignore`**
- **Purpose**: Files to exclude from Docker build
- **Contains**: Patterns for files not needed in container

---

## 📚 Documentation Files

### **`FRONTEND_DEVELOPER_GUIDE.md`**
- **Purpose**: Complete guide for frontend developers
- **Contains**: 
  - Setup instructions
  - Feature-by-feature guide
  - Code examples
  - Best practices

### **`API_ENDPOINTS_REFERENCE.md`**
- **Purpose**: Quick reference of all endpoints
- **Contains**: 
  - Endpoint tables
  - Request/response examples
  - Status codes

### **`SETUP_FOR_FRONTEND_TEAM.md`**
- **Purpose**: Quick setup guide
- **Contains**: 5-minute setup instructions

### **`BACKEND_VERIFICATION.md`**
- **Purpose**: Backend verification checklist
- **Contains**: Component verification status

### **`NEW_FEATURES_SUMMARY.md`**
- **Purpose**: Summary of new features
- **Contains**: Following, Spoiler Protection, Badge System details

### **`DATABASE_RELATIONSHIPS.md`**
- **Purpose**: Database schema documentation
- **Contains**: Model relationships and structure

### **`PROJECT_STRUCTURE.md`** (this file)
- **Purpose**: Project structure explanation

---

## 🧪 Testing & Collections

### **`Filmosphere_Complete_API.postman_collection.json`**
- **Purpose**: Complete Postman collection
- **Contains**: All API endpoints organized in folders
  - 14 folders covering all features
  - Pre-configured variables
  - Example requests

### **`IMDB FREE API.postman_collection.json`**
- **Purpose**: Reference collection for IMDb API
- **Note**: For reference only, not used directly

### **`KinoCheck API.postman_collection.json`**
- **Purpose**: Reference collection for KinoCheck API
- **Note**: For reference only, not used directly

---

## 📁 Directory Structure Details

### **`staticfiles/`**
- **Purpose**: Collected static files
- **Contains**: 
  - Django admin static files
  - DRF static files (for browsable API)
- **Generated by**: `python manage.py collectstatic`

### **`docs/`**
- **Purpose**: API documentation
- **Contains**:
  - `API.md`: Basic API documentation
  - `openapi.yaml`: OpenAPI schema (generated)

### **`migrations/`** (in each app)
- **Purpose**: Database migration files
- **Format**: `000N_description.py`
- **Never edit manually**: Generated by `makemigrations`

### **`__pycache__/`**
- **Purpose**: Python bytecode cache
- **Auto-generated**: Can be ignored/deleted
- **In `.gitignore`**: Should not be committed

---

## 🏗️ Architecture Overview

### Request Flow

```
Client Request
    ↓
filmosphere/urls.py (root routing)
    ↓
api/urls.py (API routing)
    ↓
films/urls.py or users/urls.py (app routing)
    ↓
views.py (request handler)
    ↓
serializers.py (validation)
    ↓
models.py (database operations)
    ↓
services/ (business logic, external APIs)
    ↓
Response
```

### Data Flow Example: Rating a Film

1. **Request**: `POST /api/films/tt1375666/rate`
2. **Routing**: `films/urls.py` → `FilmRatingView`
3. **Validation**: `RatingCreateUpdateSerializer`
4. **Business Logic**: `FilmRatingView.post()`
5. **Database**: `Rating.objects.update_or_create()`
6. **Badge Check**: `BadgeService.check_and_award_badges()`
7. **Response**: `RatingSerializer` → JSON response

---

## 🔑 Key Concepts

### **Models** (`models.py`)
- Define database structure
- Business logic in model methods
- Relationships between entities

### **Serializers** (`serializers.py`)
- Validate incoming data
- Transform data for API responses
- Handle nested relationships

### **Views** (`views.py`)
- Handle HTTP requests
- Call serializers for validation
- Interact with models
- Return HTTP responses

### **Services** (`services/`)
- Business logic separated from views
- External API integrations
- Reusable across views

### **URLs** (`urls.py`)
- Map URLs to views
- Define URL patterns
- Handle URL parameters

---

## 📊 Feature Organization

### Film Features (`films/`)
- Search, Details, Ratings, Reviews
- Lists, Mood Tracking
- Recommendations, Badges

### User Features (`users/`)
- Authentication, Profiles
- Following System

### External Integrations (`core/services/`)
- IMDb API
- KinoCheck API
- Watchmode API
- DeepSeek LLM API

---

## 🔄 Database Models Relationships

```
User
├── UserProfile (OneToOne)
├── Rating (OneToMany)
├── Review (OneToMany)
├── Mood (OneToMany)
├── List (OneToMany)
├── Follow (follower/following relationships)
└── UserBadge (ManyToMany through UserBadge)

Film
├── Rating (OneToMany)
├── Review (OneToMany)
├── Mood (OneToMany)
├── ListItem (OneToMany)
└── UserProfile (favorite films)

Badge
└── UserBadge (ManyToMany through UserBadge)

List
└── ListItem (OneToMany)

Review
├── ReviewLike (OneToMany)
└── User (ForeignKey)
```

---

## 🚀 Development Workflow

### Adding a New Feature

1. **Define Model** (`models.py`)
   - Create model class
   - Define fields and relationships

2. **Create Migration**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Create Serializer** (`serializers.py`)
   - Input validation
   - Response formatting

4. **Create View** (`views.py`)
   - Handle HTTP requests
   - Use serializer
   - Return responses

5. **Add URL** (`urls.py`)
   - Define URL pattern
   - Map to view

6. **Register Admin** (`admin.py`)
   - Make model manageable

7. **Test** (Postman or tests)
   - Test endpoints
   - Verify functionality

---

## 📝 File Naming Conventions

- **Models**: `models.py` (always)
- **Views**: `views.py` (always)
- **Serializers**: `serializers.py` (always)
- **URLs**: `urls.py` (always)
- **Admin**: `admin.py` (always)
- **Services**: `services/{name}_service.py`
- **Migrations**: `migrations/000N_description.py`

---

## 🎯 Important Files to Know

### For Frontend Developers
- `FRONTEND_DEVELOPER_GUIDE.md` - Start here!
- `API_ENDPOINTS_REFERENCE.md` - Quick lookup
- `Filmosphere_Complete_API.postman_collection.json` - Test endpoints

### For Backend Developers
- `films/models.py` - Database structure
- `films/views.py` - API logic
- `core/services/` - External API integrations
- `filmosphere/settings.py` - Configuration

### For DevOps
- `docker-compose.yml` - Service orchestration
- `Dockerfile` - Container definition
- `requirements.txt` - Dependencies
- `.dockerignore` - Build exclusions

---

## 🔍 Finding Things

### Where to find...

- **Film endpoints**: `films/urls.py`
- **User endpoints**: `users/urls.py`
- **Film models**: `films/models.py`
- **User models**: `users/models.py`
- **External API calls**: `core/services/`
- **Badge logic**: `films/services/badge_service.py`
- **Spoiler detection**: `core/services/deepseek_service.py`
- **Film aggregation**: `films/services/film_aggregator.py`
- **Settings**: `filmosphere/settings.py`
- **Main routing**: `filmosphere/urls.py` → `api/urls.py`

---

## 📦 Dependencies Overview

### Core Framework
- **Django**: Web framework
- **Django REST Framework**: API framework
- **djangorestframework-simplejwt**: JWT authentication

### External APIs
- **httpx**: HTTP client
- **tenacity**: Retry logic

### Database
- **psycopg2-binary**: PostgreSQL adapter

### Utilities
- **django-environ**: Environment variables
- **django-cors-headers**: CORS handling
- **drf-spectacular**: OpenAPI schema generation

---

## 🎬 Feature Implementation Locations

| Feature | Models | Views | Serializers | Services |
|---------|--------|-------|-------------|----------|
| Ratings (FR10) | `films/models.py` | `films/views.py` | `films/serializers.py` | - |
| Mood Tracking (FR09) | `films/models.py` | `films/views.py` | `films/serializers.py` | - |
| Lists (FR03) | `films/models.py` | `films/views.py` | `films/serializers.py` | - |
| Reviews | `films/models.py` | `films/views.py` | `films/serializers.py` | - |
| Spoiler Protection (FR06) | `films/models.py` | `films/views.py` | `films/serializers.py` | `core/services/deepseek_service.py` |
| Comment Moderation | `films/models.py` | `films/views.py` | `films/serializers.py` | `core/services/deepseek_service.py` |
| Badge System (FR05) | `films/models.py` | `films/views.py` | `films/serializers.py` | `films/services/badge_service.py` |
| Following | `users/models.py` | `films/views.py` | `films/serializers.py` | - |
| Recommendations (FR11) | - | `films/views.py` | `films/serializers.py` | `core/services/deepseek_service.py` |
| Film Search | - | `films/views.py` | `films/serializers.py` | `core/services/imdb_service.py` |
| Film Aggregation | `films/models.py` | `films/views.py` | - | `films/services/film_aggregator.py` |

---

## 🛠️ Common Tasks

### Run Migrations
```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

### Create Superuser
```bash
docker-compose exec web python manage.py createsuperuser
```

### View Logs
```bash
docker-compose logs -f web
```

### Access Django Shell
```bash
docker-compose exec web python manage.py shell
```

### Run Tests
```bash
docker-compose exec web pytest
```

---

## 📋 Summary

This project follows **Django's app-based architecture**:

- **`films/`**: All film-related features (ratings, reviews, lists, badges)
- **`users/`**: User authentication and profiles
- **`core/`**: Shared services (external APIs, utilities)
- **`api/`**: API routing layer
- **`filmosphere/`**: Project configuration

Each app follows Django's standard structure:
- `models.py` - Database
- `views.py` - API endpoints
- `serializers.py` - Data validation
- `urls.py` - URL routing
- `admin.py` - Admin interface

Services are separated for reusability and testability.

---

For more details on specific features, see:
- `FRONTEND_DEVELOPER_GUIDE.md` - How to use the API
- `NEW_FEATURES_SUMMARY.md` - Feature implementations
- `API_ENDPOINTS_REFERENCE.md` - All endpoints

