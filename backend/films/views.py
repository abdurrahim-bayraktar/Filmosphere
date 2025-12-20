from __future__ import annotations

import logging
import re
from typing import Any, Dict

<<<<<<< HEAD
from django.contrib.auth.models import User
=======
from django.contrib.auth import get_user_model
User = get_user_model()
from django.utils import timezone


>>>>>>> feature/backend-api
from django.db import models
from django.http import Http404
from rest_framework import status

logger = logging.getLogger(__name__)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.services import IMDbService, KinoCheckService
from films.models import Badge, CommentFlag, Film, List, ListItem, Mood, Rating, Review, ReviewLike, UserBadge, WatchedFilm
from films.serializers import (
    BadgeSerializer,
    FollowSerializer,
    ListCreateUpdateSerializer,
<<<<<<< HEAD
    ListItemCreateSerializer,
=======
>>>>>>> feature/backend-api
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
<<<<<<< HEAD
from users.models import Follow
=======
from films.models import Follow

>>>>>>> feature/backend-api

IMDB_ID_PATTERN = re.compile(r"^tt\d+$")


class SearchView(APIView):
    """Search films via IMDbService and return normalized results."""

    def __init__(self, imdb_service: IMDbService | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.imdb_service = imdb_service or IMDbService()

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Handle GET /api/search?q=<query>."""
        query = request.query_params.get("q", "").strip()
        if not query:
            return Response(
                {"detail": "Query parameter 'q' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        results_raw = self.imdb_service.search(query)
        serializer = SearchResultSerializer(results_raw, many=True)
        return Response({"query": query, "results": serializer.data})


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
        # Get user's own lists and public lists from other users
        return List.objects.filter(
            models.Q(user=user) | models.Q(is_public=True)
        ).select_related("user").prefetch_related("items__film").distinct()


class ListCreateView(CreateAPIView):
    """Create a new film list (FR03.1)."""

    serializer_class = ListCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        list_obj = serializer.save(user=self.request.user)
        
        # Check and award badges (FR05.2)
        try:
            badge_service = BadgeService()
            badge_service.check_and_award_badges(self.request.user)
        except Exception as e:
            logger.error(f"Error checking badges: {e}")
        
        return list_obj


class ListDetailView(RetrieveUpdateDestroyAPIView):
    """Get, update, or delete a list (FR03.4)."""

    serializer_class = ListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Users can only edit/delete their own lists, but can view public lists
        return List.objects.filter(
            models.Q(user=user) | models.Q(is_public=True)
        ).select_related("user").prefetch_related("items__film")

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
        return super().update(request, *args, **kwargs)


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

        # Filter out rejected comments, only show approved or pending
        queryset = Review.objects.filter(
            film=film,
            moderation_status__in=["approved", "pending"]
        ).select_related("user", "film")
        
        # If admin, show all including rejected
        if self.request.user.is_authenticated and self.request.user.is_staff:
            queryset = Review.objects.filter(film=film).select_related("user", "film")
        
        return queryset

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

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review = serializer.save(user=request.user, film=film)

        # FR06.2: Auto-detect spoilers using LLM
        if not review.is_spoiler:  # Only check if user didn't manually mark it
            try:
                from core.services.deepseek_service import DeepSeekService
                deepseek_service = DeepSeekService()
                is_spoiler = deepseek_service.check_spoiler(film.title, review.content)
                if is_spoiler:
                    review.is_auto_detected_spoiler = True
                    review.save(update_fields=["is_auto_detected_spoiler"])
            except Exception as e:
                logger.error(f"Error detecting spoiler: {e}")
                # Continue even if spoiler detection fails

        # Comment moderation with LLM and blacklist
        try:
            from core.services.deepseek_service import DeepSeekService
            deepseek_service = DeepSeekService()
            blacklist = getattr(settings, "COMMENT_BLACKLIST", [])
            moderation_result = deepseek_service.moderate_comment(review.content, blacklist)
            
            if moderation_result["needs_moderation"]:
                review.moderation_status = "pending"
                review.moderation_reason = moderation_result.get("reason", "Content flagged for review")
                review.save(update_fields=["moderation_status", "moderation_reason"])
            else:
                # Auto-approve if no issues detected
                review.moderation_status = "approved"
                review.save(update_fields=["moderation_status"])
        except Exception as e:
            logger.error(f"Error moderating comment: {e}")
            # Default to pending if moderation fails
            review.moderation_status = "pending"
            review.save(update_fields=["moderation_status"])

        # Check and award badges (FR05.2)
        try:
            badge_service = BadgeService()
            badge_service.check_and_award_badges(request.user)
        except Exception as e:
            logger.error(f"Error checking badges: {e}")
            # Continue even if badge checking fails

        response_serializer = ReviewSerializer(review, context={"request": request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class ReviewDetailView(RetrieveUpdateDestroyAPIView):
    """Get, update, or delete a review."""

    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Review.objects.select_related("user", "film").all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def update(self, request, *args, **kwargs):
        """Only allow users to update their own reviews."""
        review = self.get_object()
        if review.user != request.user:
            return Response(
                {"detail": "You can only update your own reviews."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Only allow users to delete their own reviews."""
        review = self.get_object()
        if review.user != request.user:
            return Response(
                {"detail": "You can only delete your own reviews."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)


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
            return Review.objects.filter(user=user).select_related("user", "film")
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
    """Get trending trailers from KinoCheck."""

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Handle GET /api/kinocheck/trailers/trending."""
        service = KinoCheckService()
        try:
            data = service.get_trending_trailers()
            return Response(data)
        except Exception as e:
            logger.error(f"Error fetching trending trailers: {e}")
            return Response(
                {"detail": "Failed to fetch trending trailers"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class KinoCheckTrailersByGenreView(APIView):
    """Get trailers by genre from KinoCheck."""

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Handle GET /api/kinocheck/trailers?genres={genre}."""
        genre = request.query_params.get("genres", "Action")
        service = KinoCheckService()
        try:
            data = service.get_trailers_by_genre(genre)
            return Response(data)
        except Exception as e:
            logger.error(f"Error fetching trailers by genre: {e}")
            return Response(
                {"detail": "Failed to fetch trailers"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


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
            return Follow.objects.filter(following=user).select_related("follower", "following")
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
            return Follow.objects.filter(follower=user).select_related("follower", "following")
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
    """Admin endpoint to approve or reject comments."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, review_id: int, *args: Any, **kwargs: Any) -> Response:
        """Approve or reject a comment (admin only)."""
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
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminFlaggedCommentsView(ListAPIView):
    """Get all flagged comments for admin review."""

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
