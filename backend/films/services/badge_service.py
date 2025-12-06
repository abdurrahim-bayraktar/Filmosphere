from __future__ import annotations

import logging
from typing import Any, Dict

from django.contrib.auth.models import User

from films.models import Badge, List, Rating, Review, UserBadge, WatchedFilm
from users.models import Follow

logger = logging.getLogger(__name__)


class BadgeService:
    """Service for checking and awarding badges (FR05.1, FR05.2)."""

    def __init__(self):
        self._initialize_default_badges()

    def _initialize_default_badges(self):
        """Initialize default badges if they don't exist."""
        default_badges = [
            {
                "name": "Film Enthusiast",
                "description": "Watched 10 films",
                "criteria_type": "films_watched",
                "criteria_value": 10,
            },
            {
                "name": "Critic",
                "description": "Written 50 reviews",
                "criteria_type": "reviews_written",
                "criteria_value": 50,
            },
            {
                "name": "Curator",
                "description": "Created 5 lists",
                "criteria_type": "lists_created",
                "criteria_value": 5,
            },
            {
                "name": "Rater",
                "description": "Given 25 ratings",
                "criteria_type": "ratings_given",
                "criteria_value": 25,
            },
            {
                "name": "Influencer",
                "description": "Gained 10 followers",
                "criteria_type": "followers_count",
                "criteria_value": 10,
            },
        ]

        for badge_data in default_badges:
            Badge.objects.get_or_create(
                name=badge_data["name"],
                is_custom=False,
                defaults=badge_data,
            )

    def check_and_award_badges(self, user: User) -> list[UserBadge]:
        """
        Check if user meets criteria for any badges and award them (FR05.2).
        
        Args:
            user: User to check badges for
            
        Returns:
            List of newly awarded badges
        """
        newly_awarded = []

        # Get user statistics
        stats = self._get_user_stats(user)

        # Check all badges (default and custom)
        badges = Badge.objects.all()

        for badge in badges:
            # Skip if user already has this badge
            if UserBadge.objects.filter(user=user, badge=badge).exists():
                continue

            # Check if user meets criteria
            if self._meets_criteria(user, badge, stats):
                user_badge = UserBadge.objects.create(
                    user=user,
                    badge=badge,
                    progress=stats.get(badge.criteria_type, 0),
                )
                newly_awarded.append(user_badge)
                logger.info(f"User {user.username} earned badge: {badge.name}")

        return newly_awarded

    def _get_user_stats(self, user: User) -> Dict[str, int]:
        """Get user statistics for badge checking."""
        return {
            "films_watched": WatchedFilm.objects.filter(user=user).count(),
            "reviews_written": Review.objects.filter(user=user).count(),
            "lists_created": List.objects.filter(user=user).count(),
            "ratings_given": Rating.objects.filter(user=user).count(),
            "followers_count": Follow.objects.filter(following=user).count(),
        }

    def _meets_criteria(self, user: User, badge: Badge, stats: Dict[str, int]) -> bool:
        """Check if user meets badge criteria."""
        user_value = stats.get(badge.criteria_type, 0)
        return user_value >= badge.criteria_value

    def get_user_progress(self, user: User, badge: Badge) -> Dict[str, Any]:
        """Get user's progress towards a specific badge."""
        stats = self._get_user_stats(user)
        current_value = stats.get(badge.criteria_type, 0)
        progress_percentage = min(100, int((current_value / badge.criteria_value) * 100)) if badge.criteria_value > 0 else 0

        return {
            "badge": badge.id,
            "badge_name": badge.name,
            "current_value": current_value,
            "required_value": badge.criteria_value,
            "progress_percentage": progress_percentage,
            "earned": UserBadge.objects.filter(user=user, badge=badge).exists(),
        }

