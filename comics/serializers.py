from rest_framework import serializers
from comics.models import Comic, Panel, Tag


class ComicSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='get_comic_url', read_only=True)

    class Meta:
        model = Comic

class PanelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Panel

class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag