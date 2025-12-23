from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import UserProfile
from users.serializers import (
    UserProfileSerializer,
    UserRegistrationSerializer,
)


class RegisterView(CreateAPIView):
    """User registration endpoint."""

    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    """User login endpoint."""
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {"detail": "Username and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(username=username, password=password)

    if user is None:
        return Response(
            {"detail": "Invalid credentials."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    refresh = RefreshToken.for_user(user)

    return Response(
        {
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
        },
        status=status.HTTP_200_OK,
    )


class UserProfileView(RetrieveUpdateAPIView):
    """Get or update user profile."""

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "username"
    lookup_url_kwarg = "username"

    def get_queryset(self):
        return UserProfile.objects.select_related("user").all()

    def get_object(self):
        username = self.kwargs.get("username")
        if username == "me":
            profile, created = UserProfile.objects.get_or_create(user=self.request.user)
            return profile
        try:
            return UserProfile.objects.get(user__username=username)
        except UserProfile.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("User profile not found.")

    def update(self, request, *args, **kwargs):
        """Only allow users to update their own profile."""
        username = self.kwargs.get("username")
        if username != "me" and request.user.username != username:
            return Response(
                {"detail": "You can only update your own profile."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """Handle PATCH requests for partial updates."""
        username = self.kwargs.get("username")
        if username != "me" and request.user.username != username:
            return Response(
                {"detail": "You can only update your own profile."},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    """Get current authenticated user's profile."""
    serializer = UserProfileSerializer(request.user.profile)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def search_users_view(request):
    """Search users by username."""
    query = request.query_params.get("q", "").strip()
    
    if not query:
        return Response(
            {"detail": "Query parameter 'q' is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    # Search users by username (case-insensitive, partial match)
    users = User.objects.filter(username__icontains=query)[:20]  # Limit to 20 results
    
    # Get profiles for these users
    profiles = UserProfile.objects.filter(user__in=users).select_related("user")
    
    # Serialize results
    serializer = UserProfileSerializer(profiles, many=True)
    return Response({
        "query": query,
        "results": serializer.data,
        "count": len(serializer.data)
    })
