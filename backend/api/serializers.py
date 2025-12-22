from rest_framework import serializers


class RecommendationChatSerializer(serializers.Serializer):
    user_message = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=2000,
        trim_whitespace=True,
    )


class ModerationResultSerializer(serializers.Serializer):
    allow = serializers.BooleanField()
    flags = serializers.ListField(child=serializers.CharField(), required=False)
    reason = serializers.CharField(required=False, allow_blank=True)
