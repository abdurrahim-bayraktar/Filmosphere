from __future__ import annotations

import logging
import re
from typing import Any, Dict

from django.contrib.auth.models import User
from django.db import models
from django.http import Http404
from rest_framework import status
from django.utils import timezone

logger = logging.getLogger(__name__)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.services import IMDbService, KinoCheckService
from films.models import Badge, CommentFlag, Film, List, ListItem, Mood, ModerationLog, Rating, RecommendationLog, Review, ReviewLike, UserBadge, WatchedFilm
from films.serializers import (
    BadgeSerializer,
    FollowSerializer,
    ListCreateUpdateSerializer,
    ListItemCreateSerializer,
    ListItemSerializer,
    ListSerializer,
    MoodCreateUpdateSerializer,
    MoodSerializer,
    RatingCreateUpdateSerializer,
    RatingSerializer,
    RecommendationSerializer,
    ReviewCreateUpdateSerializer,
    ReviewSerializer,
    SearchResultSerializer,
    UserBadgeSerializer,
    WatchedFilmSerializer,
)
from films.services import BadgeService, FilmAggregatorService
from users.models import Follow

IMDB_ID_PATTERN = re.compile(r"^tt\d+$")


class SearchView(APIView):
    """
    Search films via IMDbService and return normalized results.
    Frontend endpoint: GET /api/search/imdb/?q=<query>
    """

    def __init__(self, imdb_service: IMDbService | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.imdb_service = imdb_service or IMDbService()

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        query = request.query_params.get("q", "").strip()
        
        if not query:
            return Response(
                {"detail": "Query parameter 'q' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        results_raw = self.imdb_service.search(query)
        
        serializer = SearchResultSerializer(results_raw, many=True)
        return Response({
            "query": query, 
            "results": serializer.data
        })


class FilmDetailView(APIView):
    """Return full aggregated film payload for a given IMDb id."""

    def __init__(
        self,
        aggregator: FilmAggregatorService | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.aggregator = aggregator or FilmAggregatorService()

    def get(self, request: Request, imdb_id: str, *args: Any, **kwargs: Any) -> Response:
        """Handle GET /api/films/{imdb_id}."""
        if not IMDB_ID_PATTERN.match(imdb_id):
            raise Http404("Invalid IMDb id")
        payload: Dict[str, Any] = self.aggregator.fetch_and_cache(imdb_id)
        
        # Add rating statistics if film exists in database
        try:
            film = Film.objects.get(imdb_id=imdb_id)
            avg_ratings = film.get_average_ratings()
            payload["rating_statistics"] = avg_ratings
            
            # Add user's personal rating if authenticated
            if request.user.is_authenticated:
                try:
                    user_rating = Rating.objects.get(user=request.user, film=film)
                    rating_serializer = RatingSerializer(user_rating)
                    payload["user_rating"] = rating_serializer.data
                except Rating.DoesNotExist:
                    payload["user_rating"] = None
        except Film.DoesNotExist:
            payload["rating_statistics"] = None
            payload["user_rating"] = None
        
        return Response(payload)


class FilmTrailerView(APIView):
    """Return only trailer information for a film, using the aggregator output."""

    def __init__(
        self,
        aggregator: FilmAggregatorService | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.aggregator = aggregator or FilmAggregatorService()

    def get(self, request: Request, imdb_id: str, *args: Any, **kwargs: Any) -> Response:
        """Handle GET /api/films/{imdb_id}/trailer."""
        if not IMDB_ID_PATTERN.match(imdb_id):
            raise Http404("Invalid IMDb id")
        payload = self.aggregator.fetch_and_cache(imdb_id)
        return Response({"imdb_id": imdb_id, "trailer": payload.get("trailer")})


class FilmStreamingView(APIView):
    """Return only streaming information for a film, using the aggregator output."""

    def __init__(
        self,
        aggregator: FilmAggregatorService | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.aggregator = aggregator or FilmAggregatorService()

    def get(self, request: Request, imdb_id: str, *args: Any, **kwargs: Any) -> Response:
        """Handle GET /api/films/{imdb_id}/streaming."""
        if not IMDB_ID_PATTERN.match(imdb_id):
            raise Http404("Invalid IMDb id")
        payload = self.aggregator.fetch_and_cache(imdb_id)
        return Response({"imdb_id": imdb_id, "streaming": payload.get("streaming", [])})


class FilmRatingView(APIView):
    """Create, update, or delete a rating for a film."""

    permission_classes = [IsAuthenticated]

    def get_film(self, imdb_id: str) -> Film:
        """Get or create film from IMDb ID."""
        if not IMDB_ID_PATTERN.match(imdb_id):
            raise Http404("Invalid IMDb id")
        
        # Fetch film data to ensure it exists in cache
        aggregator = FilmAggregatorService()
        aggregator.fetch_and_cache(imdb_id)
        
        try:
            return Film.objects.get(imdb_id=imdb_id)
        except Film.DoesNotExist:
            raise Http404("Film not found")

    def post(self, request: Request, imdb_id: str, *args: Any, **kwargs: Any) -> Response:
        """Create or update a rating for a film."""
        film = self.get_film(imdb_id)
        
        # Check if user has watched the film
        from films.models import WatchedFilm
        if not WatchedFilm.objects.filter(user=request.user, film=film).exists():
            return Response(
                {"detail": "You must mark this film as watched before rating it."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Validate the data first
        serializer = RatingCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data.copy()
        
        # Check if aspect ratings are provided but no overall_rating
        aspects = [
            validated_data.get("plot_rating"),
            validated_data.get("acting_rating"),
            validated_data.get("cinematography_rating"),
            validated_data.get("soundtrack_rating"),
            validated_data.get("originality_rating"),
            validated_data.get("direction_rating"),
        ]
        has_aspects = any(a is not None for a in aspects)
        has_overall = validated_data.get("overall_rating") is not None
        
        # If only aspects provided (no overall), calculate overall from aspects
        if has_aspects and not has_overall:
            provided_aspects = [a for a in aspects if a is not None]
            if provided_aspects:
                temp_overall = round(sum(provided_aspects) / len(provided_aspects))
                validated_data["overall_rating"] = temp_overall
        
        # Get or create rating
        try:
            rating = Rating.objects.get(user=request.user, film=film)
            created = False
            # Update with new data
            for key, value in validated_data.items():
                setattr(rating, key, value)
            rating.save()  # This triggers model's save() which recalculates overall if needed
        except Rating.DoesNotExist:
            # Create new rating - need to ensure overall_rating is set
            if not validated_data.get("overall_rating"):
                # If still no overall, calculate from aspects or use default
                if has_aspects:
                    provided_aspects = [a for a in aspects if a is not None]
                    if provided_aspects:
                        validated_data["overall_rating"] = round(sum(provided_aspects) / len(provided_aspects))
                    else:
                        validated_data["overall_rating"] = 1
                else:
                    validated_data["overall_rating"] = 1
            
            rating = Rating.objects.create(
                user=request.user,
                film=film,
                **validated_data,
            )
            created = True
        
        # Refresh to get any calculated values
        rating.refresh_from_db()
        
        # Check and award badges (FR05.2)
        if created:  # Only check on new ratings
            try:
                badge_service = BadgeService()
                badge_service.check_and_award_badges(request.user)
            except Exception as e:
                logger.error(f"Error checking badges: {e}")
        
        response_serializer = RatingSerializer(rating)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(response_serializer.data, status=status_code)

    def delete(self, request: Request, imdb_id: str, *args: Any, **kwargs: Any) -> Response:
        """Delete a user's rating for a film."""
        film = self.get_film(imdb_id)
        
        try:
            rating = Rating.objects.get(user=request.user, film=film)
            rating.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Rating.DoesNotExist:
            return Response(
                {"detail": "Rating not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def get(self, request: Request, imdb_id: str, *args: Any, **kwargs: Any) -> Response:
        """Get the current user's rating for a film."""
        film = self.get_film(imdb_id)
        
        try:
            rating = Rating.objects.get(user=request.user, film=film)
            serializer = RatingSerializer(rating)
            return Response(serializer.data)
        except Rating.DoesNotExist:
            return Response(
                {"detail": "Rating not found."},
                status=status.HTTP_404_NOT_FOUND,
            )


class FilmRatingsListView(APIView):
    """Get all ratings for a film with statistics."""

    def get_film(self, imdb_id: str) -> Film:
        """Get film from IMDb ID."""
        if not IMDB_ID_PATTERN.match(imdb_id):
            raise Http404("Invalid IMDb id")
        
        try:
            return Film.objects.get(imdb_id=imdb_id)
        except Film.DoesNotExist:
            raise Http404("Film not found")

    def get(self, request: Request, imdb_id: str, *args: Any, **kwargs: Any) -> Response:
        """Get all ratings for a film."""
        film = self.get_film(imdb_id)
        
        ratings = Rating.objects.filter(film=film).select_related("user")
        serializer = RatingSerializer(ratings, many=True)
        
        # Get average ratings
        avg_ratings = film.get_average_ratings()
        
        return Response({
            "film": {
                "imdb_id": film.imdb_id,
                "title": film.title,
            },
            "average_ratings": avg_ratings,
            "ratings": serializer.data,
        })


class UserRatingsListView(ListAPIView):
    """Get all ratings by a specific user."""

    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        username = self.kwargs.get("username")
        try:
            user = User.objects.get(username=username)
            return Rating.objects.filter(user=user).select_related("film", "user")
        except User.DoesNotExist:
            return Rating.objects.none()


class FilmMoodView(APIView):
    """Create, update, or get mood log for a film (FR09.1, FR09.2)."""

    permission_classes = [IsAuthenticated]

    def get_film(self, imdb_id: str) -> Film:
        """Get or create film from IMDb ID."""
        if not IMDB_ID_PATTERN.match(imdb_id):
            raise Http404("Invalid IMDb id")
        
        aggregator = FilmAggregatorService()
        aggregator.fetch_and_cache(imdb_id)
        
        try:
            return Film.objects.get(imdb_id=imdb_id)
        except Film.DoesNotExist:
            raise Http404("Film not found")

    def post(self, request: Request, imdb_id: str, *args: Any, **kwargs: Any) -> Response:
        """Create or update mood log for a film."""
        film = self.get_film(imdb_id)
        
        # Check if user has watched the film
        from films.models import WatchedFilm
        if not WatchedFilm.objects.filter(user=request.user, film=film).exists():
            return Response(
                {"detail": "You must mark this film as watched before logging your mood."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Validate the data first
        serializer = MoodCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        
        # Use update_or_create to handle both create and update cases
        mood, created = Mood.objects.update_or_create(
            user=request.user,
            film=film,
            defaults=validated_data,
        )
        
        response_serializer = MoodSerializer(mood)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(response_serializer.data, status=status_code)

    def get(self, request: Request, imdb_id: str, *args: Any, **kwargs: Any) -> Response:
        """Get the current user's mood log for a film."""
        film = self.get_film(imdb_id)
        
        try:
            mood = Mood.objects.get(user=request.user, film=film)
            serializer = MoodSerializer(mood)
            return Response(serializer.data)
        except Mood.DoesNotExist:
            return Response(
                {"detail": "Mood log not found."},
                status=status.HTTP_404_NOT_FOUND,
            )


class RecommendationsView(APIView):
    """Get personalized film recommendations (FR11)."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Generate recommendations based on user's ratings, moods, and viewing history."""
        from core.services.deepseek_service import DeepSeekService
        from core.services import IMDbService, KinoCheckService
        from django.conf import settings
        
        user = request.user
        
        # FR11.1: Get user's rating history
        ratings = Rating.objects.filter(user=user).select_related("film")[:50]
        rating_data = [
            {
                "film_title": r.film.title,
                "overall_rating": r.overall_rating,
                "plot_rating": r.plot_rating,
                "acting_rating": r.acting_rating,
                "cinematography_rating": r.cinematography_rating,
                "soundtrack_rating": r.soundtrack_rating,
                "originality_rating": r.originality_rating,
                "direction_rating": r.direction_rating,
            }
            for r in ratings
        ]
        
        # FR11.1: Get user's mood logs
        moods = Mood.objects.filter(user=user).select_related("film")[:30]
        mood_data = [
            {
                "film_title": m.film.title,
                "mood_before": m.mood_before,
                "mood_after": m.mood_after,
            }
            for m in moods
        ]
        
        # FR11.1: Get viewing history (films user has watched)
        watched_films = WatchedFilm.objects.filter(user=request.user).select_related("film")
        viewing_history = [
            {
                "film_title": wf.film.title,
                "imdb_id": wf.film.imdb_id,
            }
            for wf in watched_films
        ]
        
        # Check if user has enough data
        if not rating_data and not mood_data:
            return Response({
                "recommendations": [],
                "total": 0,
                "message": "Not enough data for recommendations. Please rate some films or log moods to get personalized recommendations.",
                "based_on": {
                    "ratings_count": 0,
                    "moods_count": 0,
                    "viewing_history_count": 0,
                },
            }, status=status.HTTP_200_OK)
        
        # FR11.2: Generate recommendations using DeepSeek
        deepseek_service = DeepSeekService()
        recommended_titles = []
        
        # Check if DeepSeek API key is configured
        deepseek_api_key = getattr(settings, "DEEPSEEK_API_KEY", "")
        if not deepseek_api_key:
            # Fallback: Return popular films if no API key
            return Response({
                "recommendations": [],
                "total": 0,
                "message": "DeepSeek API key not configured. Please set DEEPSEEK_API_KEY in your .env file.",
                "based_on": {
                    "ratings_count": len(rating_data),
                    "moods_count": len(mood_data),
                    "viewing_history_count": len(viewing_history),
                },
            }, status=status.HTTP_200_OK)
        
        try:
            recommended_titles = deepseek_service.get_recommendations(
                user_ratings=rating_data,
                user_moods=mood_data,
                viewing_history=viewing_history,
            )
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return Response({
                "recommendations": [],
                "total": 0,
                "message": f"Error generating recommendations: {str(e)}",
                "based_on": {
                    "ratings_count": len(rating_data),
                    "moods_count": len(mood_data),
                    "viewing_history_count": len(viewing_history),
                },
            }, status=status.HTTP_200_OK)
        
        # FR11.3: Format recommendations with search URLs
        recommendations = []
        imdb_service = IMDbService()
        
        if not recommended_titles:
            return Response({
                "recommendations": [],
                "total": 0,
                "message": "No recommendations generated. Try rating more films or logging moods.",
                "based_on": {
                    "ratings_count": len(rating_data),
                    "moods_count": len(mood_data),
                    "viewing_history_count": len(viewing_history),
                },
            }, status=status.HTTP_200_OK)
        
        for title in recommended_titles:
            # Search for the film to get IMDb ID
            try:
                search_results = imdb_service.search(title)
                imdb_id = None
                if search_results:
                    # Try to find exact match
                    for result in search_results:
                        if result.get("title", "").lower() == title.lower():
                            imdb_id = result.get("imdb_id")
                            break
                    # If no exact match, use first result
                    if not imdb_id and search_results:
                        imdb_id = search_results[0].get("imdb_id")
            except Exception as e:
                logger.warning(f"Error searching for film {title}: {e}")
                imdb_id = None
            
            recommendations.append({
                "film_title": title,
                "imdb_id": imdb_id,
                "search_url": f"/api/search?q={title.replace(' ', '+')}" if title else None,
                "film_detail_url": f"/api/films/{imdb_id}" if imdb_id else None,
            })
        
        serializer = RecommendationSerializer(recommendations, many=True)
        return Response({
            "recommendations": serializer.data,
            "total": len(recommendations),
            "message": f"Generated {len(recommendations)} recommendations based on your preferences.",
            "based_on": {
                "ratings_count": len(rating_data),
                "moods_count": len(mood_data),
                "viewing_history_count": len(viewing_history),
            },
        })


class ListListView(ListAPIView):
    """Get all lists (user's own or public lists) (FR03)."""

    serializer_class = ListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # All lists are public, get user's own lists and all other lists
        return List.objects.filter(
            models.Q(user=user) | models.Q(is_public=True)
        ).select_related("user").prefetch_related("items__film").distinct()


class ListCreateView(CreateAPIView):
    """Create a new film list (FR03.1)."""

    serializer_class = ListCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # All lists are public by default
        list_obj = serializer.save(user=self.request.user, is_public=True)
        
        # Check and award badges (FR05.2)
        try:
            badge_service = BadgeService()
            badge_service.check_and_award_badges(self.request.user)
        except Exception as e:
            logger.error(f"Error checking badges: {e}")
        
        return list_obj


class ListDetailView(RetrieveUpdateDestroyAPIView):
    """Get, update, or delete a list (FR03.4)."""

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ListCreateUpdateSerializer
        return ListSerializer

    def get_queryset(self):
        user = self.request.user
        # All lists are public, but users can only edit/delete their own lists
        return List.objects.filter(
            models.Q(user=user) | models.Q(is_public=True)
        ).select_related("user").prefetch_related("items__film")

    def get_object(self):
        """Override to allow viewing any public list."""
        list_id = self.kwargs.get('list_id')
        try:
            list_obj = List.objects.select_related("user").prefetch_related("items__film").get(id=list_id)
            # Allow viewing if list is public or user owns it
            if list_obj.is_public or list_obj.user == self.request.user:
                return list_obj
            raise Http404("List not found or you don't have permission.")
        except List.DoesNotExist:
            raise Http404("List not found.")

    def destroy(self, request, *args, **kwargs):
        """Only allow users to delete their own lists."""
        list_obj = self.get_object()
        if list_obj.user != request.user:
            return Response(
                {"detail": "You can only delete your own lists."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Only allow users to update their own lists."""
        list_obj = self.get_object()
        if list_obj.user != request.user:
            return Response(
                {"detail": "You can only update your own lists."},
                status=status.HTTP_403_FORBIDDEN,
            )
        # Ensure is_public is always True
        serializer = self.get_serializer(list_obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(is_public=True)
        return Response(serializer.data)


class ListAddFilmView(APIView):
    """Add a film to a list (FR03.2)."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, list_id: int, *args: Any, **kwargs: Any) -> Response:
        """Add a film to a list."""
        try:
            list_obj = List.objects.get(id=list_id, user=request.user)
        except List.DoesNotExist:
            return Response(
                {"detail": "List not found or you don't have permission."},
                status=status.HTTP_404_NOT_FOUND,
            )

        imdb_id = request.data.get("imdb_id")
        if not imdb_id:
            return Response(
                {"detail": "imdb_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not IMDB_ID_PATTERN.match(imdb_id):
            return Response(
                {"detail": "Invalid IMDb id format."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get or create film
        aggregator = FilmAggregatorService()
        aggregator.fetch_and_cache(imdb_id)

        try:
            film = Film.objects.get(imdb_id=imdb_id)
        except Film.DoesNotExist:
            return Response(
                {"detail": "Film not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Get max order for this list
        max_order = ListItem.objects.filter(list=list_obj).aggregate(
            max_order=models.Max("order")
        )["max_order"] or 0

        # Create list item
        list_item, created = ListItem.objects.get_or_create(
            list=list_obj,
            film=film,
            defaults={"order": max_order + 1},
        )

        if not created:
            return Response(
                {"detail": "Film is already in this list."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ListItemSerializer(list_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ListRemoveFilmView(DestroyAPIView):
    """Remove a film from a list (FR03.3)."""

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ListItem.objects.filter(list__user=self.request.user)

    def get_object(self):
        list_id = self.kwargs.get("list_id")
        imdb_id = self.kwargs.get("imdb_id")

        try:
            list_obj = List.objects.get(id=list_id, user=self.request.user)
        except List.DoesNotExist:
            raise Http404("List not found or you don't have permission.")

        try:
            film = Film.objects.get(imdb_id=imdb_id)
        except Film.DoesNotExist:
            raise Http404("Film not found.")

        try:
            return ListItem.objects.get(list=list_obj, film=film)
        except ListItem.DoesNotExist:
            raise Http404("Film not found in this list.")


class FilmReviewsListView(ListAPIView):
    """Get all reviews for a film."""

    serializer_class = ReviewSerializer
    permission_classes = []

    def get_queryset(self):
        imdb_id = self.kwargs.get("imdb_id")
        if not IMDB_ID_PATTERN.match(imdb_id):
            raise Http404("Invalid IMDb id")

        try:
            film = Film.objects.get(imdb_id=imdb_id)
        except Film.DoesNotExist:
            return Review.objects.none()

        # Only show approved reviews (pending/rejected are hidden from public)
        queryset = Review.objects.filter(
            film=film,
            moderation_status="approved"
        ).select_related("user", "film")
        
        # If admin, show all including pending/rejected for moderation
        if self.request.user.is_authenticated and self.request.user.is_staff:
            queryset = Review.objects.filter(film=film).select_related("user", "film")
        
        return queryset.order_by("-created_at")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class ReviewCreateView(CreateAPIView):
    """Create a review for a film."""

    serializer_class = ReviewCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, imdb_id: str, *args: Any, **kwargs: Any) -> Response:
        """Create a review for a film."""
        if not IMDB_ID_PATTERN.match(imdb_id):
            raise Http404("Invalid IMDb id")

        aggregator = FilmAggregatorService()
        aggregator.fetch_and_cache(imdb_id)

        try:
            film = Film.objects.get(imdb_id=imdb_id)
        except Film.DoesNotExist:
            raise Http404("Film not found")

        # Check if user has watched the film
        from films.models import WatchedFilm
        if not WatchedFilm.objects.filter(user=request.user, film=film).exists():
            return Response(
                {"detail": "You must mark this film as watched before writing a review."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review = serializer.save(user=request.user, film=film)

        # DeepSeek Analysis: Check for spoilers AND inappropriate content
        try:
            from core.services.deepseek_service import DeepSeekService
            from django.conf import settings
            
            deepseek_service = DeepSeekService()
            blacklist = getattr(settings, "COMMENT_BLACKLIST", [])
            
            # Check if DeepSeek API key is configured
            api_key = getattr(settings, "DEEPSEEK_API_KEY", None)
            if not api_key:
                logger.warning("DeepSeek API key not configured - skipping AI moderation, using basic blacklist only")
                # Only check blacklist if no API key
                comment_lower = review.content.lower()
                has_blacklisted = any(word.lower() in comment_lower for word in blacklist)
                if has_blacklisted:
                    review.moderation_status = "pending"
                    review.moderation_reason = "Contains blacklisted words"
                    review.save(update_fields=["moderation_status", "moderation_reason"])
                    
                    # Auto-create a system flag
                    try:
                        admin_user = User.objects.filter(is_superuser=True).first() or User.objects.filter(is_staff=True).first()
                        if admin_user:
                            CommentFlag.objects.get_or_create(
                                user=admin_user,
                                review=review,
                                defaults={
                                    "reason": "inappropriate",
                                    "description": "Flagged by basic blacklist check (DeepSeek API not configured)",
                                },
                            )
                    except Exception as flag_error:
                        logger.error(f"Failed to auto-flag review {review.id}: {flag_error}")
                else:
                    review.moderation_status = "approved"
                    review.save(update_fields=["moderation_status"])
                # Don't return here - continue to badge check and response
            else:
                # API key is configured, proceed with full AI moderation
                # 1. Check for spoilers (only if user didn't manually mark it)
                is_spoiler = False
                if not review.is_spoiler:
                    try:
                        logger.info(f"Checking spoiler for review content: '{review.content}' (film: {film.title})")
                        is_spoiler = deepseek_service.check_spoiler(film.title, review.content)
                        logger.info(f"Spoiler detection result: {is_spoiler}")
                        if is_spoiler:
                            review.is_auto_detected_spoiler = True
                            logger.info(f"Review {review.id} marked as auto-detected spoiler")
                    except Exception as e:
                        logger.error(f"Error detecting spoiler: {e}", exc_info=True)
                        # Continue without spoiler detection if it fails
                else:
                    logger.info(f"Skipping spoiler detection - user manually marked as spoiler: {review.is_spoiler}")
                
                # 2. Check for inappropriate content (profanity, racism, sexism, etc.)
                try:
                    moderation_result = deepseek_service.moderate_comment(review.content, blacklist)
                except Exception as e:
                    logger.error(f"Error calling DeepSeek moderation API: {e}")
                    # If API call fails, only check blacklist
                    comment_lower = review.content.lower()
                    has_blacklisted = any(word.lower() in comment_lower for word in blacklist)
                    if has_blacklisted:
                        review.moderation_status = "pending"
                        review.moderation_reason = "Contains blacklisted words"
                        review.save(update_fields=["moderation_status", "moderation_reason"])
                    else:
                        # No blacklisted words, approve it
                        review.moderation_status = "approved"
                        review.save(update_fields=["moderation_status"])
                    # Continue to badge check and response - don't return
                else:
                    content_type = moderation_result.get("content_type", "none")
                    needs_moderation = moderation_result.get("needs_moderation", False)
                    
                    logger.info(f"DeepSeek moderation result for review {review.id}: needs_moderation={needs_moderation}, content_type={content_type}, is_spoiler={is_spoiler}")
                    
                    # If inappropriate content detected (profanity, racism, sexism, etc.), flag for admin review
                    if needs_moderation and content_type not in ["none", ""]:
                        # Flag for admin review - contains profanity, racism, sexism, etc.
                        review.moderation_status = "pending"
                        review.moderation_reason = moderation_result.get("reason", f"Content flagged: {content_type}")
                        logger.info(f"Review {review.id} flagged for moderation: {review.moderation_reason}")
                        review.save(update_fields=["moderation_status", "moderation_reason", "is_auto_detected_spoiler"])

                        # Auto-create a system flag so it appears in moderation queues
                        try:
                            admin_user = User.objects.filter(is_superuser=True).first() or User.objects.filter(is_staff=True).first()
                            if admin_user:
                                CommentFlag.objects.get_or_create(
                                    user=admin_user,
                                    review=review,
                                    defaults={
                                        "reason": "inappropriate",
                                        "description": moderation_result.get("reason", "Flagged by AI moderation"),
                                    },
                                )
                        except Exception as flag_error:
                            logger.error(f"Failed to auto-flag review {review.id}: {flag_error}")
                    elif is_spoiler:
                        # Only spoiler detected - approve but mark as spoiler (will be blurred in frontend)
                        review.moderation_status = "approved"
                        review.is_auto_detected_spoiler = True
                        logger.info(f"Review {review.id} approved with spoiler tag")
                        review.save(update_fields=["moderation_status", "is_auto_detected_spoiler"])
                    else:
                        # No issues - auto-approve
                        review.moderation_status = "approved"
                        logger.info(f"Review {review.id} auto-approved")
                        review.save(update_fields=["moderation_status"])
                
        except Exception as e:
            logger.error(f"Unexpected error in DeepSeek analysis: {e}", exc_info=True)
            # If there's an unexpected error, check blacklist at least
            try:
                from django.conf import settings
                blacklist = getattr(settings, "COMMENT_BLACKLIST", [])
                comment_lower = review.content.lower()
                has_blacklisted = any(word.lower() in comment_lower for word in blacklist)
                if has_blacklisted:
                    review.moderation_status = "pending"
                    review.moderation_reason = "Contains blacklisted words"
                    review.save(update_fields=["moderation_status", "moderation_reason"])
                else:
                    # No blacklisted words, approve it (better than blocking everything)
                    review.moderation_status = "approved"
                    review.save(update_fields=["moderation_status"])
            except Exception as e2:
                logger.error(f"Error in fallback blacklist check: {e2}")
                # Last resort: approve it (better than blocking everything)
                review.moderation_status = "approved"
                review.save(update_fields=["moderation_status"])

        # Check and award badges (FR05.2)
        try:
            badge_service = BadgeService()
            badge_service.check_and_award_badges(request.user)
        except Exception as e:
            logger.error(f"Error checking badges: {e}")
            # Continue even if badge checking fails

        response_serializer = ReviewSerializer(review, context={"request": request})
        response_data = response_serializer.data
        
        # Add moderation info to response so frontend can inform user
        if review.moderation_status == "pending":
            response_data["moderation_message"] = (
                "Your review has been submitted for moderation. "
                f"Reason: {review.moderation_reason or 'Automatic content check'}. "
                "It will be visible once approved by a moderator."
            )
        
        return Response(response_data, status=status.HTTP_201_CREATED)


class ReviewDetailView(RetrieveUpdateDestroyAPIView):
    """Get, update, or delete a review."""

    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    lookup_url_kwarg = 'review_id'

    def get_queryset(self):
        return Review.objects.select_related("user", "film").all()

    def get_serializer_class(self):
        """Use ReviewCreateUpdateSerializer for updates, ReviewSerializer for retrieval."""
        if self.request.method in ['PUT', 'PATCH']:
            return ReviewCreateUpdateSerializer
        return ReviewSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def update(self, request, *args, **kwargs):
        """Only allow users to update their own reviews."""
        instance = self.get_object()
        
        if instance.user != request.user:
            return Response(
                {"detail": "You can only update your own reviews."},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        # Use ReviewCreateUpdateSerializer for update
        partial = kwargs.pop('partial', False)
        serializer = ReviewCreateUpdateSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Refresh instance and return with full serializer
        instance.refresh_from_db()
        response_serializer = ReviewSerializer(instance, context={"request": request})
        return Response(response_serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Only allow users to delete their own reviews."""
        try:
            review = self.get_object()
            if review.user != request.user:
                return Response(
                    {"detail": "You can only delete your own reviews."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            review.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Error deleting review: {e}", exc_info=True)
            return Response(
                {"detail": f"Error deleting review: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ReviewLikeView(APIView):
    """Like or unlike a review."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, review_id: int, *args: Any, **kwargs: Any) -> Response:
        """Like or unlike a review."""
        try:
            review = Review.objects.get(id=review_id)
        except Review.DoesNotExist:
            return Response(
                {"detail": "Review not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        like, created = ReviewLike.objects.get_or_create(
            user=request.user,
            review=review,
        )

        if not created:
            # Unlike - delete the like
            like.delete()
            action = "unliked"
        else:
            action = "liked"

        review.refresh_from_db()
        serializer = ReviewSerializer(review, context={"request": request})
        return Response(
            {
                "action": action,
                "review": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class UserListsView(ListAPIView):
    """Get all lists by a specific user."""

    serializer_class = ListSerializer
    permission_classes = []

    def get_queryset(self):
        username = self.kwargs.get("username")
        try:
            user = User.objects.get(username=username)
            # Show user's own lists and public lists
            requesting_user = self.request.user if self.request.user.is_authenticated else None
            if requesting_user and requesting_user == user:
                # User viewing their own profile - show all their lists
                return List.objects.filter(user=user).select_related("user").prefetch_related("items__film")
            else:
                # Other users - only show public lists
                return List.objects.filter(user=user, is_public=True).select_related("user").prefetch_related("items__film")
        except User.DoesNotExist:
            return List.objects.none()


class UserReviewsView(ListAPIView):
    """Get all reviews by a specific user."""

    serializer_class = ReviewSerializer
    permission_classes = []

    def get_queryset(self):
        username = self.kwargs.get("username")
        try:
            user = User.objects.get(username=username)
            # Only show approved reviews unless the user is viewing their own profile or is an admin
            queryset = Review.objects.filter(user=user).select_related("user", "film")
            
            # Filter to only approved reviews for public view
            if not self.request.user.is_authenticated or \
               (self.request.user.username != username and not self.request.user.is_staff):
                queryset = queryset.filter(moderation_status="approved")
            
            return queryset.order_by("-created_at")
        except User.DoesNotExist:
            return Review.objects.none()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context



# IMDb Extended API Views
class FilmCreditsView(APIView):
    """Get full cast and credits for a film."""

    def get(self, request: Request, imdb_id: str, *args: Any, **kwargs: Any) -> Response:
        """Handle GET /api/films/{imdb_id}/credits."""
        if not IMDB_ID_PATTERN.match(imdb_id):
            return Response(
                {"detail": "Invalid IMDb id"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        service = IMDbService()
        try:
            data = service.get_credits(imdb_id)
            return Response(data)
        except Exception as e:
            logger.error(f"Error fetching credits for {imdb_id}: {e}")
            return Response(
                {"detail": "Failed to fetch credits"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class FilmReleaseDatesView(APIView):
    """Get release dates for a film."""

    def get(self, request: Request, imdb_id: str, *args: Any, **kwargs: Any) -> Response:
        """Handle GET /api/films/{imdb_id}/release-dates."""
        if not IMDB_ID_PATTERN.match(imdb_id):
            return Response(
                {"detail": "Invalid IMDb id"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        service = IMDbService()
        try:
            data = service.get_release_dates(imdb_id)
            return Response(data)
        except Exception as e:
            logger.error(f"Error fetching release dates for {imdb_id}: {e}")
            return Response(
                {"detail": "Failed to fetch release dates"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class FilmAKAsView(APIView):
    """Get alternate titles (AKAs) for a film."""

    def get(self, request: Request, imdb_id: str, *args: Any, **kwargs: Any) -> Response:
        """Handle GET /api/films/{imdb_id}/akas."""
        if not IMDB_ID_PATTERN.match(imdb_id):
            return Response(
                {"detail": "Invalid IMDb id"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        service = IMDbService()
        try:
            data = service.get_akas(imdb_id)
            return Response(data)
        except Exception as e:
            logger.error(f"Error fetching AKAs for {imdb_id}: {e}")
            return Response(
                {"detail": "Failed to fetch AKAs"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class FilmSeasonsView(APIView):
    """Get season count for a TV series."""

    def get(self, request: Request, imdb_id: str, *args: Any, **kwargs: Any) -> Response:
        """Handle GET /api/films/{imdb_id}/seasons."""
        if not IMDB_ID_PATTERN.match(imdb_id):
            return Response(
                {"detail": "Invalid IMDb id"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        service = IMDbService()
        try:
            data = service.get_seasons(imdb_id)
            return Response(data)
        except Exception as e:
            logger.error(f"Error fetching seasons for {imdb_id}: {e}")
            return Response(
                {"detail": "Failed to fetch seasons"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class FilmEpisodesView(APIView):
    """Get episodes for a TV series."""

    def get(self, request: Request, imdb_id: str, *args: Any, **kwargs: Any) -> Response:
        """Handle GET /api/films/{imdb_id}/episodes."""
        if not IMDB_ID_PATTERN.match(imdb_id):
            return Response(
                {"detail": "Invalid IMDb id"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        service = IMDbService()
        try:
            data = service.get_episodes(imdb_id)
            return Response(data)
        except Exception as e:
            logger.error(f"Error fetching episodes for {imdb_id}: {e}")
            return Response(
                {"detail": "Failed to fetch episodes"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class FilmImagesView(APIView):
    """Get images for a film."""

    def get(self, request: Request, imdb_id: str, *args: Any, **kwargs: Any) -> Response:
        """Handle GET /api/films/{imdb_id}/images."""
        if not IMDB_ID_PATTERN.match(imdb_id):
            return Response(
                {"detail": "Invalid IMDb id"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        service = IMDbService()
        try:
            data = service.get_images(imdb_id)
            return Response(data)
        except Exception as e:
            logger.error(f"Error fetching images for {imdb_id}: {e}")
            return Response(
                {"detail": "Failed to fetch images"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class FilmVideosView(APIView):
    """Get videos for a film."""

    def get(self, request: Request, imdb_id: str, *args: Any, **kwargs: Any) -> Response:
        """Handle GET /api/films/{imdb_id}/videos."""
        if not IMDB_ID_PATTERN.match(imdb_id):
            return Response(
                {"detail": "Invalid IMDb id"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        service = IMDbService()
        try:
            data = service.get_videos(imdb_id)
            return Response(data)
        except Exception as e:
            logger.error(f"Error fetching videos for {imdb_id}: {e}")
            return Response(
                {"detail": "Failed to fetch videos"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class FilmAwardNominationsView(APIView):
    """Get award nominations for a film."""

    def get(self, request: Request, imdb_id: str, *args: Any, **kwargs: Any) -> Response:
        """Handle GET /api/films/{imdb_id}/award-nominations."""
        if not IMDB_ID_PATTERN.match(imdb_id):
            return Response(
                {"detail": "Invalid IMDb id"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        service = IMDbService()
        try:
            data = service.get_award_nominations(imdb_id)
            return Response(data)
        except Exception as e:
            logger.error(f"Error fetching award nominations for {imdb_id}: {e}")
            return Response(
                {"detail": "Failed to fetch award nominations"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class FilmParentsGuideView(APIView):
    """Get parents guide for a film."""

    def get(self, request: Request, imdb_id: str, *args: Any, **kwargs: Any) -> Response:
        """Handle GET /api/films/{imdb_id}/parents-guide."""
        if not IMDB_ID_PATTERN.match(imdb_id):
            return Response(
                {"detail": "Invalid IMDb id"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        service = IMDbService()
        try:
            data = service.get_parents_guide(imdb_id)
            return Response(data)
        except Exception as e:
            logger.error(f"Error fetching parents guide for {imdb_id}: {e}")
            return Response(
                {"detail": "Failed to fetch parents guide"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class FilmCertificatesView(APIView):
    """Get certificates for a film."""

    def get(self, request: Request, imdb_id: str, *args: Any, **kwargs: Any) -> Response:
        """Handle GET /api/films/{imdb_id}/certificates."""
        if not IMDB_ID_PATTERN.match(imdb_id):
            return Response(
                {"detail": "Invalid IMDb id"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        service = IMDbService()
        try:
            data = service.get_certificates(imdb_id)
            return Response(data)
        except Exception as e:
            logger.error(f"Error fetching certificates for {imdb_id}: {e}")
            return Response(
                {"detail": "Failed to fetch certificates"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class FilmCompanyCreditsView(APIView):
    """Get company credits for a film."""

    def get(self, request: Request, imdb_id: str, *args: Any, **kwargs: Any) -> Response:
        """Handle GET /api/films/{imdb_id}/company-credits."""
        if not IMDB_ID_PATTERN.match(imdb_id):
            return Response(
                {"detail": "Invalid IMDb id"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        service = IMDbService()
        try:
            data = service.get_company_credits(imdb_id)
            return Response(data)
        except Exception as e:
            logger.error(f"Error fetching company credits for {imdb_id}: {e}")
            return Response(
                {"detail": "Failed to fetch company credits"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class FilmBoxOfficeView(APIView):
    """Get box office data for a film."""

    def get(self, request: Request, imdb_id: str, *args: Any, **kwargs: Any) -> Response:
        """Handle GET /api/films/{imdb_id}/box-office."""
        if not IMDB_ID_PATTERN.match(imdb_id):
            return Response(
                {"detail": "Invalid IMDb id"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        service = IMDbService()
        try:
            data = service.get_box_office(imdb_id)
            return Response(data)
        except Exception as e:
            logger.error(f"Error fetching box office data for {imdb_id}: {e}")
            return Response(
                {"detail": "Failed to fetch box office data"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class FilmSearchGraphQLView(APIView):
    """Search movies using GraphQL query."""

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Handle POST /api/search/graphql."""
        query = request.data.get("query")
        if not query:
            return Response(
                {"detail": "Query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        service = IMDbService()
        try:
            data = service.search_movies_graphql(query)
            return Response(data)
        except Exception as e:
            logger.error(f"Error in GraphQL search: {e}")
            return Response(
                {"detail": "Failed to perform search"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# KinoCheck Extended API Views
class KinoCheckLatestTrailersView(APIView):
    """Get latest trailers from KinoCheck."""

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Handle GET /api/kinocheck/trailers/latest."""
        service = KinoCheckService()
        try:
            data = service.get_latest_trailers()
            return Response(data)
        except Exception as e:
            logger.error(f"Error fetching latest trailers: {e}")
            return Response(
                {"detail": "Failed to fetch latest trailers"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class KinoCheckTrendingTrailersView(APIView):
    """
    Retrieves trending trailers from KinoCheck and enriches them with IMDb posters.
    Implements a fallback mechanism to preserve original thumbnails if enrichment fails.
    """

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        service = KinoCheckService()
        aggregator = FilmAggregatorService()

        # Retrieve the initial trailer list from the service layer
        raw_trailers = service.get_trending_trailers()

        if not isinstance(raw_trailers, list):
            return Response(
                {"detail": "Invalid trailer data format received from upstream service."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        enriched_trailers = []

        for item in raw_trailers:
            # OPTIMIZATION: Skip corrupted entries with no title to prevent empty UI boxes
            if not item.get("title"):
                continue

            # Preserve the original KinoCheck thumbnail as a fallback
            original_thumbnail = item.get("thumbnail", "")
            resource = item.get("resource") or {}
            imdb_id = resource.get("imdb_id")

            if imdb_id and IMDB_ID_PATTERN.match(imdb_id):
                try:
                    # Attempt to fetch high-resolution metadata from the aggregator
                    full_data = aggregator.fetch_and_cache(imdb_id)
                    metadata = full_data.get("metadata", {})
                    raw_image = metadata.get("primaryImage")

                    # Extract the URL from the metadata object if it exists
                    if isinstance(raw_image, dict):
                        poster_url = raw_image.get("url")
                        item["thumbnail"] = poster_url if poster_url else original_thumbnail
                    elif isinstance(raw_image, str) and raw_image:
                        item["thumbnail"] = raw_image
                    else:
                        # Fallback to original KinoCheck image if IMDb has no primary image
                        item["thumbnail"] = original_thumbnail

                except Exception as e:
                    # Log enrichment failure but preserve the original data for UI stability
                    logger.warning(f"Metadata enrichment failed for {imdb_id}: {e}")
                    item["thumbnail"] = original_thumbnail
            else:
                # If no valid IMDb ID is present, retain the original thumbnail
                item["thumbnail"] = original_thumbnail
            
            # Ensure the thumbnail key is never None for frontend compatibility
            if not item.get("thumbnail"):
                item["thumbnail"] = ""
                
            enriched_trailers.append(item)

        return Response(enriched_trailers, status=status.HTTP_200_OK)



class KinoCheckTrailersByGenreView(APIView):
    """
    Returns trailers filtered by genre from KinoCheck and enriches them with IMDb posters.
    Filters out corrupted entries and provides fallback thumbnails for stability.
    Endpoint: GET /api/kinocheck/trailers?genres=Action
    """

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        genre = request.query_params.get("genres")

        if not genre:
            return Response(
                {"detail": "Query parameter 'genres' is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = KinoCheckService()
        aggregator = FilmAggregatorService()

        # Fetch trailers for the specific genre
        raw_trailers = service.get_trailers_by_genre(genre)

        # Defensive check for list format
        if not isinstance(raw_trailers, list):
            return Response(
                {"detail": "Invalid trailer data format received from service."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        enriched_trailers = []

        for item in raw_trailers:
            # 1. PREVENT EMPTY BOXES: Skip corrupted entries with no title
            if not item.get("title"):
                continue

            # 2. FALLBACK MECHANISM: Store the original KinoCheck thumbnail
            original_thumbnail = item.get("thumbnail", "")
            resource = item.get("resource") or {}
            imdb_id = resource.get("imdb_id")

            if imdb_id and IMDB_ID_PATTERN.match(imdb_id):
                try:
                    # 3. METADATA ENRICHMENT: Attempt to fetch high-quality IMDb poster
                    full_data = aggregator.fetch_and_cache(imdb_id)
                    metadata = full_data.get("metadata", {})
                    raw_image = metadata.get("primaryImage")

                    if isinstance(raw_image, dict):
                        poster_url = raw_image.get("url")
                        item["thumbnail"] = poster_url if poster_url else original_thumbnail
                    elif isinstance(raw_image, str) and raw_image:
                        item["thumbnail"] = raw_image
                    else:
                        item["thumbnail"] = original_thumbnail

                except Exception as e:
                    # Log failure but retain original KinoCheck image to avoid empty UI
                    logger.warning(f"Genre metadata enrichment failed for {imdb_id}: {e}")
                    item["thumbnail"] = original_thumbnail
            else:
                item["thumbnail"] = original_thumbnail
            
            # Final safety check for the thumbnail field
            if not item.get("thumbnail"):
                item["thumbnail"] = ""
                
            enriched_trailers.append(item)

        return Response(enriched_trailers, status=status.HTTP_200_OK)



class KinoCheckMovieByIdView(APIView):
    """Get movie details by KinoCheck ID."""

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Handle GET /api/kinocheck/movies?id={movie_id}."""
        movie_id = request.query_params.get("id")
        if not movie_id:
            return Response(
                {"detail": "Movie ID parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        service = KinoCheckService()
        try:
            data = service.get_movie_by_id(movie_id)
            if data is None:
                return Response(
                    {"detail": "Movie not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            return Response(data)
        except Exception as e:
            logger.error(f"Error fetching movie by ID: {e}")
            return Response(
                {"detail": "Failed to fetch movie"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# Following System Views
class FollowUserView(APIView):
    """Follow or unfollow a user."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, username: str, *args: Any, **kwargs: Any) -> Response:
        """Follow a user."""
        try:
            user_to_follow = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if user_to_follow == request.user:
            return Response(
                {"detail": "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=user_to_follow,
        )

        if not created:
            return Response(
                {"detail": "You are already following this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check and award badges for both users (FR05.2)
        badge_service = BadgeService()
        badge_service.check_and_award_badges(request.user)  # Follower
        badge_service.check_and_award_badges(user_to_follow)  # User being followed (for followers_count badge)

        serializer = FollowSerializer(follow)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request: Request, username: str, *args: Any, **kwargs: Any) -> Response:
        """Unfollow a user."""
        try:
            user_to_unfollow = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            follow = Follow.objects.get(follower=request.user, following=user_to_unfollow)
            follow.delete()
            return Response(
                {"detail": "Successfully unfollowed user."},
                status=status.HTTP_200_OK,
            )
        except Follow.DoesNotExist:
            return Response(
                {"detail": "You are not following this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserFollowersView(ListAPIView):
    """Get all followers of a user."""

    serializer_class = FollowSerializer
    permission_classes = []

    def get_queryset(self):
        username = self.kwargs.get("username")
        try:
            user = User.objects.get(username=username)
            return Follow.objects.filter(following=user).select_related("follower", "follower__profile", "following", "following__profile")
        except User.DoesNotExist:
            return Follow.objects.none()


class UserFollowingView(ListAPIView):
    """Get all users that a user is following."""

    serializer_class = FollowSerializer
    permission_classes = []

    def get_queryset(self):
        username = self.kwargs.get("username")
        try:
            user = User.objects.get(username=username)
            return Follow.objects.filter(follower=user).select_related("follower", "follower__profile", "following", "following__profile")
        except User.DoesNotExist:
            return Follow.objects.none()


class CheckFollowStatusView(APIView):
    """Check if current user follows another user."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, username: str, *args: Any, **kwargs: Any) -> Response:
        """Check follow status."""
        try:
            user_to_check = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        is_following = Follow.objects.filter(
            follower=request.user,
            following=user_to_check,
        ).exists()

        followers_count = Follow.objects.filter(following=user_to_check).count()
        following_count = Follow.objects.filter(follower=user_to_check).count()

        return Response({
            "is_following": is_following,
            "followers_count": followers_count,
            "following_count": following_count,
        })


# Badge System Views (FR05)
class BadgeListView(ListAPIView):
    """Get all available badges."""

    serializer_class = BadgeSerializer
    permission_classes = []

    def get_queryset(self):
        is_custom = self.request.query_params.get("is_custom", "").lower()
        if is_custom == "true":
            return Badge.objects.filter(is_custom=True)
        elif is_custom == "false":
            return Badge.objects.filter(is_custom=False)
        return Badge.objects.all()


class UserBadgesView(ListAPIView):
    """Get all badges earned by a user (FR05.3)."""

    serializer_class = UserBadgeSerializer
    permission_classes = []

    def get_queryset(self):
        username = self.kwargs.get("username")
        try:
            user = User.objects.get(username=username)
            return UserBadge.objects.filter(user=user).select_related("user", "badge")
        except User.DoesNotExist:
            return UserBadge.objects.none()


class BadgeProgressView(APIView):
    """Get user's progress towards all badges."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Get progress for all badges."""
        badge_service = BadgeService()
        badges = Badge.objects.all()
        
        progress = []
        for badge in badges:
            progress.append(badge_service.get_user_progress(request.user, badge))

        return Response({"progress": progress})


class CreateCustomBadgeView(CreateAPIView):
    """Create a custom badge/challenge (FR05)."""

    serializer_class = BadgeSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        badge = serializer.save(
            is_custom=True,
            created_by=self.request.user,
        )
        
        # Check if user already meets criteria
        badge_service = BadgeService()
        badge_service.check_and_award_badges(self.request.user)
        
        return badge


class AwardBadgeView(APIView):
    """Manually trigger badge checking for current user."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Check and award badges."""
        badge_service = BadgeService()
        newly_awarded = badge_service.check_and_award_badges(request.user)
        
        serializer = UserBadgeSerializer(newly_awarded, many=True)
        return Response({
            "newly_awarded": serializer.data,
            "count": len(newly_awarded),
        })


# Watched Films Views
class MarkFilmWatchedView(APIView):
    """Mark a film as watched."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, imdb_id: str, *args: Any, **kwargs: Any) -> Response:
        """Mark a film as watched."""
        if not IMDB_ID_PATTERN.match(imdb_id):
            return Response(
                {"detail": "Invalid IMDb ID format."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get or create film
        aggregator = FilmAggregatorService()
        try:
            film = Film.objects.get(imdb_id=imdb_id)
        except Film.DoesNotExist:
            # Fetch film data to create it
            aggregator.fetch_and_cache(imdb_id)
            try:
                film = Film.objects.get(imdb_id=imdb_id)
            except Film.DoesNotExist:
                return Response(
                    {"detail": "Film not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        # Create or get watched film record
        watched_film, created = WatchedFilm.objects.get_or_create(
            user=request.user,
            film=film,
        )

        # Check and award badges
        badge_service = BadgeService()
        badge_service.check_and_award_badges(request.user)

        serializer = WatchedFilmSerializer(watched_film)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class MarkFilmUnwatchedView(APIView):
    """Mark a film as unwatched (remove from watched list)."""

    permission_classes = [IsAuthenticated]

    def delete(self, request: Request, imdb_id: str, *args: Any, **kwargs: Any) -> Response:
        """Remove film from watched list."""
        if not IMDB_ID_PATTERN.match(imdb_id):
            return Response(
                {"detail": "Invalid IMDb ID format."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            film = Film.objects.get(imdb_id=imdb_id)
        except Film.DoesNotExist:
            return Response(
                {"detail": "Film not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            watched_film = WatchedFilm.objects.get(user=request.user, film=film)
            watched_film.delete()
            return Response(
                {"detail": "Film removed from watched list."},
                status=status.HTTP_200_OK,
            )
        except WatchedFilm.DoesNotExist:
            return Response(
                {"detail": "Film is not in your watched list."},
                status=status.HTTP_404_NOT_FOUND,
            )


class UserWatchedFilmsView(ListAPIView):
    """Get all films watched by a user."""

    serializer_class = WatchedFilmSerializer
    permission_classes = []

    def get_queryset(self):
        username = self.kwargs.get("username")
        try:
            user = User.objects.get(username=username)
            # If viewing own profile or public, show all watched films
            if self.request.user.is_authenticated and self.request.user == user:
                return WatchedFilm.objects.filter(user=user).select_related("film", "user").order_by("-watched_at")
            # For other users, show watched films (no privacy restriction mentioned)
            return WatchedFilm.objects.filter(user=user).select_related("film", "user").order_by("-watched_at")
        except User.DoesNotExist:
            return WatchedFilm.objects.none()


class CheckFilmWatchedView(APIView):
    """Check if current user has watched a specific film."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, imdb_id: str, *args: Any, **kwargs: Any) -> Response:
        """Check if film is watched."""
        if not IMDB_ID_PATTERN.match(imdb_id):
            return Response(
                {"detail": "Invalid IMDb ID format."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            film = Film.objects.get(imdb_id=imdb_id)
        except Film.DoesNotExist:
            return Response(
                {"detail": "Film not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        is_watched = WatchedFilm.objects.filter(user=request.user, film=film).exists()
        
        watched_film = None
        if is_watched:
            watched_film = WatchedFilm.objects.get(user=request.user, film=film)
        
        return Response({
            "is_watched": is_watched,
            "watched_at": watched_film.watched_at.isoformat() if watched_film else None,
        })


# Comment Moderation Views
class FlagCommentView(APIView):
    """Flag a comment for review."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, review_id: int, *args: Any, **kwargs: Any) -> Response:
        """Flag a comment."""
        try:
            review = Review.objects.get(id=review_id)
        except Review.DoesNotExist:
            return Response(
                {"detail": "Review not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if user already flagged this comment
        if CommentFlag.objects.filter(user=request.user, review=review).exists():
            return Response(
                {"detail": "You have already flagged this comment."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get flag reason from request
        reason = request.data.get("reason", "other")
        description = request.data.get("description", "")

        flag = CommentFlag.objects.create(
            user=request.user,
            review=review,
            reason=reason,
            description=description,
        )

        # Update review flagged count (handled by CommentFlag.save())
        # Set status to pending if not already
        if review.moderation_status == "approved":
            review.moderation_status = "pending"
            review.save(update_fields=["moderation_status"])

        return Response(
            {"detail": "Comment flagged successfully.", "flag_id": flag.id},
            status=status.HTTP_201_CREATED,
        )


class UnflagCommentView(APIView):
    """Remove a flag from a comment."""

    permission_classes = [IsAuthenticated]

    def delete(self, request: Request, review_id: int, *args: Any, **kwargs: Any) -> Response:
        """Remove flag."""
        try:
            review = Review.objects.get(id=review_id)
        except Review.DoesNotExist:
            return Response(
                {"detail": "Review not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            flag = CommentFlag.objects.get(user=request.user, review=review)
            flag.delete()
            return Response(
                {"detail": "Flag removed successfully."},
                status=status.HTTP_200_OK,
            )
        except CommentFlag.DoesNotExist:
            return Response(
                {"detail": "You have not flagged this comment."},
                status=status.HTTP_404_NOT_FOUND,
            )


class AdminModerateCommentView(APIView):
    """Admin endpoint to approve or reject comments with DeepSeek analysis."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, review_id: int, *args: Any, **kwargs: Any) -> Response:
        """Get DeepSeek moderation analysis for a review (admin only)."""
        if not request.user.is_staff:
            return Response(
                {"detail": "Only staff members can access moderation analysis."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            review = Review.objects.get(id=review_id)
        except Review.DoesNotExist:
            return Response(
                {"detail": "Review not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Get DeepSeek moderation analysis
        from core.services.deepseek_service import DeepSeekService
        from django.conf import settings
        
        deepseek_service = DeepSeekService()
        blacklist = getattr(settings, "MODERATION_BLACKLIST", [])
        
        moderation_result = deepseek_service.moderate_comment(review.content, blacklist)
        
        return Response({
            "review_id": review.id,
            "deepseek_analysis": moderation_result,
            "suggested_action": "reject" if moderation_result.get("needs_moderation", False) else "approve",
            "current_status": review.moderation_status
        }, status=status.HTTP_200_OK)

    def post(self, request: Request, review_id: int, *args: Any, **kwargs: Any) -> Response:
        """Approve or reject a comment (admin only) with optional DeepSeek analysis."""
        if not request.user.is_staff:
            return Response(
                {"detail": "Only staff members can moderate comments."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            review = Review.objects.get(id=review_id)
        except Review.DoesNotExist:
            return Response(
                {"detail": "Review not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        action = request.data.get("action")  # "approve" or "reject"
        reason = request.data.get("reason", "")
        use_deepseek = request.data.get("use_deepseek", False)  # Optional: get DeepSeek analysis first

        # If use_deepseek is True, get analysis before moderating
        deepseek_analysis = None
        if use_deepseek:
            from core.services.deepseek_service import DeepSeekService
            from django.conf import settings
            
            deepseek_service = DeepSeekService()
            blacklist = getattr(settings, "MODERATION_BLACKLIST", [])
            deepseek_analysis = deepseek_service.moderate_comment(review.content, blacklist)
            
            # Auto-suggest action based on DeepSeek analysis if no action provided
            if not action and deepseek_analysis.get("needs_moderation", False):
                action = "reject"
                reason = reason or deepseek_analysis.get("reason", "Flagged by DeepSeek moderation")

        if action == "approve":
            review.moderation_status = "approved"
            review.moderation_reason = reason or "Approved by admin"
        elif action == "reject":
            review.moderation_status = "rejected"
            review.moderation_reason = reason or "Rejected by admin"
        else:
            return Response(
                {"detail": "Invalid action. Use 'approve' or 'reject'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        review.moderated_by = request.user
        review.moderated_at = timezone.now()
        review.save(update_fields=["moderation_status", "moderation_reason", "moderated_by", "moderated_at"])

        serializer = ReviewSerializer(review, context={"request": request})
        response_data = serializer.data
        if deepseek_analysis:
            response_data["deepseek_analysis"] = deepseek_analysis
        
        return Response(response_data, status=status.HTTP_200_OK)


class AdminFlaggedCommentsView(ListAPIView):
    """Get all flagged comments for admin review with optional DeepSeek analysis."""

    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_staff:
            return Review.objects.none()

        # Get comments that are pending or have been flagged
        status_filter = self.request.query_params.get("status", "pending")
        
        if status_filter == "all":
            queryset = Review.objects.filter(
                models.Q(moderation_status="pending") | models.Q(flagged_count__gt=0)
            )
        elif status_filter == "flagged":
            queryset = Review.objects.filter(flagged_count__gt=0)
        else:  # pending
            queryset = Review.objects.filter(moderation_status="pending")

        return queryset.select_related("user", "film", "moderated_by").order_by("-flagged_count", "-created_at")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def list(self, request, *args, **kwargs):
        """Override list to add DeepSeek analysis if requested."""
        include_deepseek = request.query_params.get("include_deepseek", "false").lower() == "true"
        
        response = super().list(request, *args, **kwargs)
        
        if include_deepseek:
            from core.services.deepseek_service import DeepSeekService
            from django.conf import settings
            
            deepseek_service = DeepSeekService()
            blacklist = getattr(settings, "MODERATION_BLACKLIST", [])
            
            # Add DeepSeek analysis to each review
            reviews_with_analysis = []
            for review_data in response.data.get("results", response.data if isinstance(response.data, list) else []):
                try:
                    review_id = review_data.get("id")
                    if review_id:
                        review = Review.objects.get(id=review_id)
                        analysis = deepseek_service.moderate_comment(review.content, blacklist)
                        review_data["deepseek_analysis"] = analysis
                        review_data["deepseek_suggested_action"] = "reject" if analysis.get("needs_moderation", False) else "approve"
                except Review.DoesNotExist:
                    pass
                except Exception as e:
                    logger.error(f"Error getting DeepSeek analysis for review {review_id}: {e}")
                
                reviews_with_analysis.append(review_data)
            
            if isinstance(response.data, list):
                response.data = reviews_with_analysis
            else:
                response.data["results"] = reviews_with_analysis
        
        return response


class TopLikedReviewsView(ListAPIView):
    """Get top most liked reviews across all films."""

    serializer_class = ReviewSerializer
    permission_classes = []

    def get_queryset(self):
        # Get top 5 most liked approved reviews, excluding spoilers
        limit = int(self.request.query_params.get("limit", 5))
        queryset = Review.objects.filter(
            moderation_status="approved",
            is_spoiler=False,
            is_auto_detected_spoiler=False
        ).select_related("user", "film").order_by("-likes_count", "-created_at")
        return queryset[:limit]

    def list(self, request, *args, **kwargs):
        """Return top liked reviews with proper formatting."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True, context={"request": request})
        
        # Format response for frontend
        reviews_data = []
        for review_data in serializer.data:
            reviews_data.append({
                "id": review_data.get("id"),
                "username": review_data.get("username", "Unknown"),
                "film_title": review_data.get("film_title", "Unknown Film"),
                "content": review_data.get("content", ""),
                "created_at": review_data.get("created_at"),
                "likes_count": review_data.get("likes_count", 0),
                "moderation_status": review_data.get("moderation_status", "approved"),
                "rating": review_data.get("rating"),
            })
        
        return Response(reviews_data, status=status.HTTP_200_OK)


class AdminRecentReviewsView(ListAPIView):
    """Get recent reviews for admin dashboard."""

    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_staff:
            return Review.objects.none()

        # Get recent reviews, ordered by creation date
        limit = int(self.request.query_params.get("limit", 30))
        queryset = Review.objects.all().select_related("user", "film").order_by("-created_at")
        return queryset[:limit]

    def list(self, request, *args, **kwargs):
        """Return recent reviews with proper formatting."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True, context={"request": request})
        
        # Format response for frontend
        reviews_data = []
        for review_data in serializer.data:
            reviews_data.append({
                "id": review_data.get("id"),
                "username": review_data.get("username", "Unknown"),
                "film_title": review_data.get("film_title", "Unknown Film"),
                "content": review_data.get("content", ""),
                "created_at": review_data.get("created_at"),
                "moderation_status": review_data.get("moderation_status", "pending"),
                "flagged_count": review_data.get("flagged_count", 0),
                "rating": review_data.get("rating"),
            })
        
        return Response(reviews_data, status=status.HTTP_200_OK)


# ==================== ADMIN ENDPOINTS ====================

class AdminStatsView(APIView):
    """Get admin dashboard statistics."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Get admin statistics."""
        if not request.user.is_staff:
            return Response(
                {"detail": "Only staff members can access admin statistics."},
                status=status.HTTP_403_FORBIDDEN,
            )

        stats = {
            "total_users": User.objects.count(),
            "total_films": Film.objects.count(),
            "total_reviews": Review.objects.count(),
            "total_ratings": Rating.objects.count(),
            "total_watched": WatchedFilm.objects.count(),
            "total_lists": List.objects.count(),
            "total_badges": Badge.objects.count(),
            "pending_reviews": Review.objects.filter(moderation_status="pending").count(),
            "flagged_reviews": Review.objects.filter(flagged_count__gt=0).count(),
        }

        return Response(stats, status=status.HTTP_200_OK)


class AdminUsersView(ListAPIView):
    """Get all users for admin management."""

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_staff:
            return User.objects.none()

        queryset = User.objects.all().order_by("-date_joined")
        
        # Search functionality
        search_term = self.request.query_params.get("search", "")
        if search_term:
            queryset = queryset.filter(
                models.Q(username__icontains=search_term) |
                models.Q(email__icontains=search_term) |
                models.Q(first_name__icontains=search_term) |
                models.Q(last_name__icontains=search_term)
            )
        
        return queryset

    def list(self, request, *args, **kwargs):
        """Return user list with additional info."""
        queryset = self.get_queryset()
        
        users_data = []
        for user in queryset:
            users_data.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_active": user.is_active,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
                "date_joined": user.date_joined.isoformat() if user.date_joined else None,
                "last_login": user.last_login.isoformat() if user.last_login else None,
            })
        
        return Response(users_data, status=status.HTTP_200_OK)


class AdminUserBanView(APIView):
    """Ban or unban a user."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, user_id: int, *args: Any, **kwargs: Any) -> Response:
        """Ban or unban a user."""
        if not request.user.is_staff:
            return Response(
                {"detail": "Only staff members can ban users."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Prevent banning yourself
        if user == request.user:
            return Response(
                {"detail": "You cannot ban yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Toggle ban status
        user.is_active = not user.is_active
        user.save(update_fields=["is_active"])

        return Response({
            "detail": f"User {'banned' if not user.is_active else 'unbanned'} successfully.",
            "user_id": user.id,
            "username": user.username,
            "is_active": user.is_active
        }, status=status.HTTP_200_OK)


class AdminUserDeleteView(APIView):
    """Delete a user."""

    permission_classes = [IsAuthenticated]

    def delete(self, request: Request, user_id: int, *args: Any, **kwargs: Any) -> Response:
        """Delete a user."""
        if not request.user.is_staff:
            return Response(
                {"detail": "Only staff members can delete users."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Prevent deleting yourself
        if user == request.user:
            return Response(
                {"detail": "You cannot delete yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        username = user.username
        user.delete()

        return Response({
            "detail": f"User {username} deleted successfully."
        }, status=status.HTTP_200_OK)


class AdminFilmsView(ListAPIView):
    """Get all films for admin management."""

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_staff:
            return Film.objects.none()

        queryset = Film.objects.all().order_by("-created_at")
        
        # Search functionality
        search_term = self.request.query_params.get("search", "")
        if search_term:
            queryset = queryset.filter(
                models.Q(title__icontains=search_term) |
                models.Q(imdb_id__icontains=search_term)
            )
        
        return queryset

    def list(self, request, *args, **kwargs):
        """Return film list."""
        queryset = self.get_queryset()
        
        films_data = []
        for film in queryset:
            films_data.append({
                "id": str(film.id),
                "title": film.title,
                "imdb_id": film.imdb_id,
                "year": film.year,
                "poster_url": film.poster_url,
                "created_at": film.created_at.isoformat() if film.created_at else None,
            })
        
        return Response(films_data, status=status.HTTP_200_OK)


class AdminFilmCreateView(APIView):
    """Create a new film by IMDb ID."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Create a film from IMDb ID."""
        if not request.user.is_staff:
            return Response(
                {"detail": "Only staff members can create films."},
                status=status.HTTP_403_FORBIDDEN,
            )

        imdb_id = request.data.get("imdb_id", "").strip()
        if not imdb_id:
            return Response(
                {"detail": "IMDb ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not IMDB_ID_PATTERN.match(imdb_id):
            return Response(
                {"detail": "Invalid IMDb ID format. Expected format: tt1234567"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if film already exists
        if Film.objects.filter(imdb_id=imdb_id).exists():
            film = Film.objects.get(imdb_id=imdb_id)
            return Response(
                {"detail": "Film already exists.", "film": {
                    "id": str(film.id),
                    "title": film.title,
                    "imdb_id": film.imdb_id,
                    "year": film.year
                }},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Use FilmAggregatorService to fetch and create film
        try:
            aggregator = FilmAggregatorService()
            film_data = aggregator.get_or_create_film(imdb_id)
            
            return Response({
                "detail": "Film created successfully.",
                "film": {
                    "id": str(film_data.id),
                    "title": film_data.title,
                    "imdb_id": film_data.imdb_id,
                    "year": film_data.year,
                    "poster_url": film_data.poster_url
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error creating film {imdb_id}: {e}")
            return Response(
                {"detail": f"Failed to create film: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AdminFilmUpdateView(APIView):
    """Update a film."""

    permission_classes = [IsAuthenticated]

    def put(self, request: Request, film_id: str, *args: Any, **kwargs: Any) -> Response:
        """Update a film."""
        if not request.user.is_staff:
            return Response(
                {"detail": "Only staff members can update films."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            film = Film.objects.get(id=film_id)
        except Film.DoesNotExist:
            return Response(
                {"detail": "Film not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Update fields
        if "title" in request.data:
            film.title = request.data["title"]
        if "year" in request.data:
            film.year = request.data["year"]
        
        film.save(update_fields=["title", "year", "updated_at"])

        return Response({
            "detail": "Film updated successfully.",
            "film": {
                "id": str(film.id),
                "title": film.title,
                "imdb_id": film.imdb_id,
                "year": film.year
            }
        }, status=status.HTTP_200_OK)


class AdminFilmDeleteView(APIView):
    """Delete a film."""

    permission_classes = [IsAuthenticated]

    def delete(self, request: Request, film_id: str, *args: Any, **kwargs: Any) -> Response:
        """Delete a film."""
        if not request.user.is_staff:
            return Response(
                {"detail": "Only staff members can delete films."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            film = Film.objects.get(id=film_id)
        except Film.DoesNotExist:
            return Response(
                {"detail": "Film not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        title = film.title
        film.delete()

        return Response({
            "detail": f"Film {title} deleted successfully."
        }, status=status.HTTP_200_OK)


class AdminBadgeStatsView(APIView):
    """Get badge statistics for admin."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Get badge statistics."""
        if not request.user.is_staff:
            return Response(
                {"detail": "Only staff members can access badge statistics."},
                status=status.HTTP_403_FORBIDDEN,
            )

        stats = {
            "total_badges": Badge.objects.count(),
            "active_badges": Badge.objects.filter(is_active=True).count() if hasattr(Badge, "is_active") else Badge.objects.count(),
            "custom_badges": Badge.objects.filter(is_custom=True).count(),
            "total_awards": UserBadge.objects.count(),
            "unique_users_with_badges": UserBadge.objects.values("user").distinct().count(),
        }

        return Response(stats, status=status.HTTP_200_OK)


class AdminMoodStatsView(APIView):
    """Get mood tracking statistics for admin."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Get mood statistics."""
        if not request.user.is_staff:
            return Response(
                {"detail": "Only staff members can access mood statistics."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Get all moods
        all_moods = Mood.objects.all()
        total_moods = all_moods.count()

        if total_moods == 0:
            return Response({
                "before": {"percentages": {}, "total": 0},
                "after": {"percentages": {}, "total": 0}
            }, status=status.HTTP_200_OK)

        # Calculate percentages for mood_before
        before_counts = {}
        for mood in all_moods:
            mood_before = mood.mood_before or "neutral"
            before_counts[mood_before] = before_counts.get(mood_before, 0) + 1

        before_percentages = {
            mood: round((count / total_moods) * 100, 2)
            for mood, count in before_counts.items()
        }

        # Calculate percentages for mood_after
        after_counts = {}
        for mood in all_moods:
            mood_after = mood.mood_after or "neutral"
            after_counts[mood_after] = after_counts.get(mood_after, 0) + 1

        after_percentages = {
            mood: round((count / total_moods) * 100, 2)
            for mood, count in after_counts.items()
        }

        return Response({
            "before": {
                "percentages": before_percentages,
                "total": total_moods
            },
            "after": {
                "percentages": after_percentages,
                "total": total_moods
            }
        }, status=status.HTTP_200_OK)


class AdminLogsView(ListAPIView):
    """Get system logs (ModerationLog and RecommendationLog) for admin."""

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_staff:
            return []

        log_type = self.request.query_params.get("type", "all")  # "moderation", "recommendation", or "all"
        limit = int(self.request.query_params.get("limit", 100))

        logs = []

        if log_type in ["moderation", "all"]:
            moderation_logs = ModerationLog.objects.all().order_by("-created_at")[:limit]
            for log in moderation_logs:
                logs.append({
                    "id": log.id,
                    "type": "moderation",
                    "level": "WARNING" if not log.allow else "INFO",
                    "message": f"Moderation {log.direction}: {log.reason or 'No reason provided'}",
                    "timestamp": log.created_at.isoformat() if log.created_at else None,
                    "user": log.user.username if log.user else "System",
                    "direction": log.direction,
                    "allow": log.allow,
                    "flags": log.flags or []
                })

        if log_type in ["recommendation", "all"]:
            recommendation_logs = RecommendationLog.objects.all().order_by("-created_at")[:limit]
            for log in recommendation_logs:
                level = "ERROR" if log.blocked else "INFO"
                logs.append({
                    "id": log.id,
                    "type": "recommendation",
                    "level": level,
                    "message": f"Recommendation request: {log.user_message[:100]}..." if len(log.user_message) > 100 else f"Recommendation request: {log.user_message}",
                    "timestamp": log.created_at.isoformat() if log.created_at else None,
                    "user": log.user.username if log.user else "Unknown",
                    "blocked": log.blocked,
                    "flags": log.flags or []
                })

        # Sort by timestamp descending
        logs.sort(key=lambda x: x["timestamp"] or "", reverse=True)
        return logs[:limit]

    def list(self, request, *args, **kwargs):
        """Return logs list."""
        logs = self.get_queryset()
        return Response(logs, status=status.HTTP_200_OK)


class AdminUserActivityView(APIView):
    """Get user activity logs for admin (reviews, ratings, watched films, lists, etc.)."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, user_id: int, *args: Any, **kwargs: Any) -> Response:
        """Get all activities for a specific user."""
        if not request.user.is_staff:
            return Response(
                {"detail": "Only staff members can access user activities."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Get all user activities
        activities = []

        # Recent reviews
        reviews = Review.objects.filter(user=user).select_related("film").order_by("-created_at")[:20]
        for review in reviews:
            activities.append({
                "type": "review",
                "action": "created_review",
                "timestamp": review.created_at.isoformat() if review.created_at else None,
                "details": {
                    "review_id": review.id,
                    "film_title": review.film.title if review.film else "Unknown",
                    "film_imdb_id": review.film.imdb_id if review.film else None,
                    "rating": review.rating,
                    "moderation_status": review.moderation_status,
                }
            })

        # Recent ratings
        ratings = Rating.objects.filter(user=user).select_related("film").order_by("-rated_at")[:20]
        for rating in ratings:
            activities.append({
                "type": "rating",
                "action": "rated_film",
                "timestamp": rating.rated_at.isoformat() if rating.rated_at else None,
                "details": {
                    "rating_id": rating.id,
                    "film_title": rating.film.title if rating.film else "Unknown",
                    "film_imdb_id": rating.film.imdb_id if rating.film else None,
                    "overall_rating": rating.overall_rating,
                }
            })

        # Recent watched films
        watched = WatchedFilm.objects.filter(user=user).select_related("film").order_by("-watched_at")[:20]
        for wf in watched:
            activities.append({
                "type": "watched",
                "action": "watched_film",
                "timestamp": wf.watched_at.isoformat() if wf.watched_at else None,
                "details": {
                    "film_title": wf.film.title if wf.film else "Unknown",
                    "film_imdb_id": wf.film.imdb_id if wf.film else None,
                }
            })

        # Recent lists created
        lists = List.objects.filter(user=user).order_by("-created_at")[:10]
        for list_obj in lists:
            activities.append({
                "type": "list",
                "action": "created_list",
                "timestamp": list_obj.created_at.isoformat() if list_obj.created_at else None,
                "details": {
                    "list_id": list_obj.id,
                    "list_title": list_obj.title,
                    "films_count": list_obj.films_count,
                }
            })

        # Recent moods
        moods = Mood.objects.filter(user=user).select_related("film").order_by("-logged_at")[:20]
        for mood in moods:
            activities.append({
                "type": "mood",
                "action": "logged_mood",
                "timestamp": mood.logged_at.isoformat() if mood.logged_at else None,
                "details": {
                    "mood_id": mood.id,
                    "film_title": mood.film.title if mood.film else "Unknown",
                    "film_imdb_id": mood.film.imdb_id if mood.film else None,
                    "mood_before": mood.mood_before,
                    "mood_after": mood.mood_after,
                }
            })

        # Sort all activities by timestamp descending
        activities.sort(key=lambda x: x["timestamp"] or "", reverse=True)

        return Response({
            "user_id": user.id,
            "username": user.username,
            "total_activities": len(activities),
            "activities": activities[:50]  # Limit to 50 most recent
        }, status=status.HTTP_200_OK)
