# Database Relationships - User Connections

## ✅ Yes, We Used Django's Default User Class

We're using Django's built-in `User` model from `django.contrib.auth.models.User`.

## How Relationships Work

### Rating → User
```python
class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ratings")
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name="ratings")
    # ...
```

**Database:** `films_rating` table has a `user_id` column (Foreign Key)
- Stores the User's ID (integer)
- Django ORM handles this automatically
- You can access: `rating.user` (gets User object)
- You can access: `user.ratings.all()` (gets all ratings by user)

### Mood → User
```python
class Mood(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="moods")
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name="moods")
    # ...
```

**Database:** `films_mood` table has a `user_id` column (Foreign Key)

### UserProfile → User
```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    # ...
```

**Database:** `users_userprofile` table has a `user_id` column (OneToOne - unique)

## Database Schema

When Django creates the tables, it looks like this:

```
auth_user (Django's default User table)
├── id (PK)
├── username
├── email
└── ...

films_rating
├── id (PK)
├── user_id (FK → auth_user.id)  ← User's ID stored here
├── film_id (FK → films_film.id)
├── overall_rating
└── ...

films_mood
├── id (PK)
├── user_id (FK → auth_user.id)  ← User's ID stored here
├── film_id (FK → films_film.id)
├── mood_before
└── ...

users_userprofile
├── id (PK)
├── user_id (FK → auth_user.id, UNIQUE)  ← User's ID stored here
└── ...
```

## How Django ORM Works

### When you create a Rating:
```python
rating = Rating.objects.create(
    user=request.user,  # Pass User object
    film=film,
    overall_rating=5
)
```

**Django automatically:**
- Takes `request.user.id` (the user's ID)
- Stores it in `user_id` column in database
- Creates the foreign key relationship

### When you query:
```python
# Get user's ratings
user.ratings.all()  # Django automatically uses user_id to find ratings

# Get rating's user
rating.user  # Django automatically joins using user_id to get User object
```

## Summary

✅ **Django's default User class** - `django.contrib.auth.models.User`  
✅ **ForeignKey stores user_id** - Django ORM handles this automatically  
✅ **Same approach as Gemini suggested** - User ID stored in Rating/Mood/List tables  
✅ **Django ORM manages relationships** - No need to manually handle IDs  

This is the standard Django way! 🎯

