# Guide: Creating Dummy Users and Badges for Testing

This guide will help you create dummy data to test the admin page functionality.

## Creating Dummy Users

### Method 1: Using Django Admin Interface

1. Start the Django server:
   ```bash
   cd backend
   python manage.py runserver
   ```

2. Go to `http://localhost:8000/admin/`

3. Login with a superuser account (or create one with `python manage.py createsuperuser`)

4. Navigate to "Users" section

5. Click "Add User" and create users with:
   - Username
   - Email
   - Password
   - Check "Active" for active users, uncheck for banned users

### Method 2: Using Django Shell

```bash
cd backend
python manage.py shell
```

Then run:
```python
from django.contrib.auth.models import User
from users.models import UserProfile

# Create dummy users
users_data = [
    {"username": "john_doe", "email": "john@example.com", "password": "password123"},
    {"username": "jane_smith", "email": "jane@example.com", "password": "password123"},
    {"username": "film_lover", "email": "film@example.com", "password": "password123"},
    {"username": "reviewer", "email": "reviewer@example.com", "password": "password123"},
    {"username": "banned_user", "email": "banned@example.com", "password": "password123"},
]

for user_data in users_data:
    user = User.objects.create_user(
        username=user_data["username"],
        email=user_data["email"],
        password=user_data["password"]
    )
    
    # Create user profile (automatically created via signal, but you can customize)
    if not hasattr(user, 'profile'):
        UserProfile.objects.create(user=user)
    
    # Ban the banned user
    if user_data["username"] == "banned_user":
        user.is_active = False
        user.save()
    
    print(f"Created user: {user.username}")

# Verify
print(f"Total users: {User.objects.count()}")
```

### Method 3: Using Management Command (if you create one)

You could create a custom management command:
```bash
python manage.py create_dummy_users
```

## Creating Dummy Badges

### Method 1: Using Django Admin Interface

1. Go to `http://localhost:8000/admin/`

2. Navigate to "Badges" section

3. Click "Add Badge" and create badges with:
   - Name: e.g., "Film Enthusiast"
   - Description: e.g., "Watched 10 films"
   - Criteria Type: Choose from dropdown (films_watched, reviews_written, etc.)
   - Criteria Value: e.g., 10
   - Is Custom: Uncheck for system badges, check for custom badges
   - Icon URL: (optional) URL to badge icon

### Method 2: Using Django Shell

```bash
cd backend
python manage.py shell
```

Then run:
```python
from films.models import Badge

# System badges (these are usually created automatically by BadgeService)
system_badges = [
    {
        "name": "Film Enthusiast",
        "description": "Watched 10 films",
        "criteria_type": "films_watched",
        "criteria_value": 10,
        "is_custom": False
    },
    {
        "name": "Critic",
        "description": "Written 50 reviews",
        "criteria_type": "reviews_written",
        "criteria_value": 50,
        "is_custom": False
    },
    {
        "name": "Curator",
        "description": "Created 5 lists",
        "criteria_type": "lists_created",
        "criteria_value": 5,
        "is_custom": False
    },
    {
        "name": "Rater",
        "description": "Given 25 ratings",
        "criteria_type": "ratings_given",
        "criteria_value": 25,
        "is_custom": False
    },
    {
        "name": "Influencer",
        "description": "Gained 10 followers",
        "criteria_type": "followers_count",
        "criteria_value": 10,
        "is_custom": False
    },
]

for badge_data in system_badges:
    badge, created = Badge.objects.get_or_create(
        name=badge_data["name"],
        defaults=badge_data
    )
    if created:
        print(f"Created badge: {badge.name}")
    else:
        print(f"Badge already exists: {badge.name}")

# Create custom badges
custom_badges = [
    {
        "name": "Horror Master",
        "description": "Watched 20 horror films",
        "criteria_type": "custom",
        "criteria_value": 20,
        "is_custom": True
    },
    {
        "name": "Early Adopter",
        "description": "Joined in the first month",
        "criteria_type": "custom",
        "criteria_value": 1,
        "is_custom": True
    },
]

from django.contrib.auth.models import User
admin_user = User.objects.filter(is_superuser=True).first()

for badge_data in custom_badges:
    badge_data["created_by"] = admin_user
    badge, created = Badge.objects.get_or_create(
        name=badge_data["name"],
        defaults=badge_data
    )
    if created:
        print(f"Created custom badge: {badge.name}")
    else:
        print(f"Custom badge already exists: {badge.name}")

# Verify
print(f"Total badges: {Badge.objects.count()}")
print(f"System badges: {Badge.objects.filter(is_custom=False).count()}")
print(f"Custom badges: {Badge.objects.filter(is_custom=True).count()}")
```

### Method 3: Badges Are Auto-Created

Note: The `BadgeService` automatically creates default system badges when first initialized. These badges are created when:
- The service is first instantiated
- Or when you access badge-related endpoints

To trigger badge creation, simply access:
```bash
curl http://localhost:8000/api/badges/
```

## Understanding "Active Badges"

**Active Badges** refers to **system badges** (non-custom badges). These are the predefined badges that are automatically checked and awarded based on user activity:

- **Active Badges** = `Badge.objects.filter(is_custom=False).count()` - System/Predefined badges
- **Custom Badges** = `Badge.objects.filter(is_custom=True).count()` - User-created badges
- **Total Badges** = All badges (active + custom)

In the admin badge stats:
- **Total Badges**: All badges in the system
- **Active Badges**: System badges (the 5 default badges + any admin-created system badges)
- **Custom Badges**: User-created custom challenge badges

## Awarding Badges to Users

Badges are automatically awarded when users meet the criteria. To manually trigger badge checking:

```python
from films.services import BadgeService
from django.contrib.auth.models import User

badge_service = BadgeService()
user = User.objects.get(username="john_doe")
awarded = badge_service.check_and_award_badges(user)
print(f"Awarded {len(awarded)} badges to {user.username}")
```

Or via API:
```bash
curl -X POST http://localhost:8000/api/badges/award \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Creating Films for Testing

You can create films via the admin page by entering an IMDb ID (e.g., `tt1375666` for Inception). The system will automatically fetch all details from the IMDb API.

Or via Django shell:
```python
from films.services import FilmAggregatorService

aggregator = FilmAggregatorService()
# This will fetch and cache the film data
payload = aggregator.fetch_and_cache("tt1375666")
print(f"Film created: {payload.get('title')}")
```

## Quick Test Script

Create a file `create_test_data.py` in the backend directory:

```python
#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Filmosphere.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile
from films.models import Badge
from films.services import BadgeService, FilmAggregatorService

# Create users
users = [
    {"username": "testuser1", "email": "test1@test.com"},
    {"username": "testuser2", "email": "test2@test.com"},
    {"username": "testuser3", "email": "test3@test.com"},
]

for u in users:
    user, created = User.objects.get_or_create(
        username=u["username"],
        defaults={"email": u["email"]}
    )
    user.set_password("testpass123")
    user.save()
    if created:
        print(f"Created user: {user.username}")

# Initialize badges (will create default badges)
badge_service = BadgeService()
print("Badges initialized")

# Create a test film
try:
    aggregator = FilmAggregatorService()
    aggregator.fetch_and_cache("tt1375666")  # Inception
    print("Created test film: Inception")
except Exception as e:
    print(f"Could not create film: {e}")

print("\nTest data created successfully!")
print(f"Total users: {User.objects.count()}")
print(f"Total badges: {Badge.objects.count()}")
```

Run it with:
```bash
cd backend
python create_test_data.py
```

