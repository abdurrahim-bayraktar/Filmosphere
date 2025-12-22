from django.urls import path

from .views import (
    # --- Friend's Import ---
    SearchView,
    
    # --- Your Admin Imports ---
    AdminBadgeStatsView,
    AdminBanUserView,
    AdminDeleteUserView,
    AdminFilmCreateView,
    AdminFilmDeleteView,
    AdminFilmsListView,
    AdminFilmUpdateView,
    AdminFlaggedCommentsView,
    AdminModerateCommentView,
    AdminMoodStatsView,
    AdminRecentReviewsView,
    AdminStatsView,
    AdminSystemLogsView,
    AdminUsersListView,
    
    # --- Shared Imports ---
    AwardBadgeView,
    BadgeListView,
    BadgeProgressView,
    CheckFilmWatchedView,
    CheckFollowStatusView,
    CreateCustomBadgeView,
    FilmAKAsView,
    FilmAwardNominationsView,
    FilmBoxOfficeView,
    FilmCertificatesView,
    FilmCompanyCreditsView,
    FilmCreditsView,
    FilmDetailView,
    FilmEpisodesView,
    FilmImagesView,
    FilmMoodView,
    FilmParentsGuideView,
    FilmRatingView,
    FilmRatingsListView,
    FilmReleaseDatesView,
    FilmReviewsListView,
    FilmSearchGraphQLView,
    FilmSeasonsView,
    FilmStreamingView,
    FilmTrailerView,
    FilmVideosView,
    FlagCommentView,
    FollowUserView,
    KinoCheckLatestTrailersView,
    KinoCheckMovieByIdView,
    KinoCheckTrendingTrailersView,
    KinoCheckTrailersByGenreView,
    ListAddFilmView,
    ListCreateView,
    ListDetailView,
    ListListView,
    ListRemoveFilmView,
    MarkFilmUnwatchedView,
    MarkFilmWatchedView,
    RecommendationsView,
    ReviewCreateView,
    ReviewDetailView,
    ReviewLikeView,
    UnflagCommentView,
    UserBadgesView,
    UserFollowersView,
    UserFollowingView,
    UserListsView,
    UserRatingsListView,
    UserReviewsView,
    UserWatchedFilmsView,
)

urlpatterns = [
    # --- Friend's Search Endpoint ---
    path("search/imdb/", SearchView.as_view(), name="search-imdb"),

    # --- Standard Endpoints ---
    path("films/<str:imdb_id>", FilmDetailView.as_view(), name="film-detail"),
    path("films/<str:imdb_id>/trailer", FilmTrailerView.as_view(), name="film-trailer"),
    path("films/<str:imdb_id>/streaming", FilmStreamingView.as_view(), name="film-streaming"),
    path("films/<str:imdb_id>/rate", FilmRatingView.as_view(), name="film-rate"),
    path("films/<str:imdb_id>/ratings", FilmRatingsListView.as_view(), name="film-ratings-list"),
    path("films/<str:imdb_id>/mood", FilmMoodView.as_view(), name="film-mood"),
    path("films/<str:imdb_id>/watched", MarkFilmWatchedView.as_view(), name="film-mark-watched"),
    path("films/<str:imdb_id>/unwatched", MarkFilmUnwatchedView.as_view(), name="film-mark-unwatched"),
    path("films/<str:imdb_id>/watched-status", CheckFilmWatchedView.as_view(), name="film-watched-status"),
    path("films/<str:imdb_id>/reviews", FilmReviewsListView.as_view(), name="film-reviews-list"),
    path("films/<str:imdb_id>/reviews/create", ReviewCreateView.as_view(), name="film-review-create"),
    path("recommendations/", RecommendationsView.as_view(), name="recommendations"),
    path("lists/", ListListView.as_view(), name="list-list"),
    path("lists/create/", ListCreateView.as_view(), name="list-create"),
    path("lists/<int:list_id>", ListDetailView.as_view(), name="list-detail"),
    path("lists/<int:list_id>/films", ListAddFilmView.as_view(), name="list-add-film"),
    path("lists/<int:list_id>/films/<str:imdb_id>", ListRemoveFilmView.as_view(), name="list-remove-film"),
    path("reviews/<int:review_id>", ReviewDetailView.as_view(), name="review-detail"),
    path("reviews/<int:review_id>/like", ReviewLikeView.as_view(), name="review-like"),
    
    # IMDb Extended API endpoints
    path("films/<str:imdb_id>/credits", FilmCreditsView.as_view(), name="film-credits"),
    path("films/<str:imdb_id>/release-dates", FilmReleaseDatesView.as_view(), name="film-release-dates"),
    path("films/<str:imdb_id>/akas", FilmAKAsView.as_view(), name="film-akas"),
    path("films/<str:imdb_id>/seasons", FilmSeasonsView.as_view(), name="film-seasons"),
    path("films/<str:imdb_id>/episodes", FilmEpisodesView.as_view(), name="film-episodes"),
    path("films/<str:imdb_id>/images", FilmImagesView.as_view(), name="film-images"),
    path("films/<str:imdb_id>/videos", FilmVideosView.as_view(), name="film-videos"),
    path("films/<str:imdb_id>/award-nominations", FilmAwardNominationsView.as_view(), name="film-award-nominations"),
    path("films/<str:imdb_id>/parents-guide", FilmParentsGuideView.as_view(), name="film-parents-guide"),
    path("films/<str:imdb_id>/certificates", FilmCertificatesView.as_view(), name="film-certificates"),
    path("films/<str:imdb_id>/company-credits", FilmCompanyCreditsView.as_view(), name="film-company-credits"),
    path("films/<str:imdb_id>/box-office", FilmBoxOfficeView.as_view(), name="film-box-office"),
    path("search/graphql", FilmSearchGraphQLView.as_view(), name="search-graphql"),
    
    # KinoCheck Extended API endpoints
    path("kinocheck/trailers/latest", KinoCheckLatestTrailersView.as_view(), name="kinocheck-latest-trailers"),
    path("kinocheck/trailers/trending", KinoCheckTrendingTrailersView.as_view(), name="kinocheck-trending-trailers"),
    path("kinocheck/trailers", KinoCheckTrailersByGenreView.as_view(), name="kinocheck-trailers-by-genre"),
    path("kinocheck/movies", KinoCheckMovieByIdView.as_view(), name="kinocheck-movie-by-id"),
    
    # Following System endpoints
    path("users/<str:username>/follow", FollowUserView.as_view(), name="follow-user"),
    path("users/<str:username>/followers", UserFollowersView.as_view(), name="user-followers"),
    path("users/<str:username>/following", UserFollowingView.as_view(), name="user-following"),
    path("users/<str:username>/follow-status", CheckFollowStatusView.as_view(), name="check-follow-status"),
    
    # Badge System endpoints
    path("badges/", BadgeListView.as_view(), name="badge-list"),
    path("badges/progress", BadgeProgressView.as_view(), name="badge-progress"),
    path("badges/create", CreateCustomBadgeView.as_view(), name="create-custom-badge"),
    path("badges/award", AwardBadgeView.as_view(), name="award-badge"),
    path("users/<str:username>/badges", UserBadgesView.as_view(), name="user-badges"),
    
    # Watched Films endpoints
    path("users/<str:username>/watched", UserWatchedFilmsView.as_view(), name="user-watched-films"),
    
    # Comment Moderation endpoints
    path("reviews/<int:review_id>/flag", FlagCommentView.as_view(), name="flag-comment"),
    path("reviews/<int:review_id>/unflag", UnflagCommentView.as_view(), name="unflag-comment"),
    
    # --- Your New Admin Endpoints ---
    path("admin/reviews/<int:review_id>/moderate", AdminModerateCommentView.as_view(), name="admin-moderate-comment"),
    path("admin/reviews/flagged", AdminFlaggedCommentsView.as_view(), name="admin-flagged-comments"),
    path("admin/stats/", AdminStatsView.as_view(), name="admin-stats"),
    
    # Admin User Management
    path("admin/users/", AdminUsersListView.as_view(), name="admin-users-list"),
    path("admin/users/<int:user_id>/ban", AdminBanUserView.as_view(), name="admin-ban-user"),
    path("admin/users/<int:user_id>/delete", AdminDeleteUserView.as_view(), name="admin-delete-user"),
    
    # Admin Recent Reviews
    path("admin/reviews/recent", AdminRecentReviewsView.as_view(), name="admin-recent-reviews"),
    
    # Admin Film Management
    path("admin/films/", AdminFilmsListView.as_view(), name="admin-films-list"),
    path("admin/films/create", AdminFilmCreateView.as_view(), name="admin-film-create"),
    path("admin/films/<str:film_id>/update", AdminFilmUpdateView.as_view(), name="admin-film-update"),
    path("admin/films/<str:film_id>/delete", AdminFilmDeleteView.as_view(), name="admin-film-delete"),
    
    # Admin Badge Stats
    path("admin/badges/stats", AdminBadgeStatsView.as_view(), name="admin-badge-stats"),
    
    # Admin Mood Stats
    path("admin/moods/stats", AdminMoodStatsView.as_view(), name="admin-mood-stats"),
    
    # Admin System Logs
    path("admin/logs", AdminSystemLogsView.as_view(), name="admin-system-logs"),
]
