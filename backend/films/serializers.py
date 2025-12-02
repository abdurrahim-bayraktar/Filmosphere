from __future__ import annotations

from rest_framework import serializers


class SearchResultSerializer(serializers.Serializer):
    """Serializer for search result items returned from IMDbService."""

    imdb_id = serializers.CharField()
    title = serializers.CharField()
    year = serializers.IntegerField(required=False, allow_null=True)
    image = serializers.CharField(required=False, allow_null=True)
    type = serializers.CharField(required=False, allow_null=True)



