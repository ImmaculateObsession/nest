from rest_framework import serializers
from comics.models import Comic


class ComicSerializer(serializers.ModelSerializer):

    pk = serializers.Field()
    title = serializers.CharField(required=False)
    image_url = serializers.URLField(required=False)
    alt_text = serializers.CharField(required=False)

    class Meta:
        model = Comic
        fields = ('id', 'title', 'image_url', 'alt_text')