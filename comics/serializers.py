from rest_framework import serializers
from comics.models import Comic, Panel, Tag


class ComicSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comic
        fields = ('id', 'title', 'image_url', 'alt_text', 'thumb', 'tags', 'pebbles')

class PanelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Panel

class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag