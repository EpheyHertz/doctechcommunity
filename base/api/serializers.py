from rest_framework import serializers
from base.models import Room



class RoomSerializer(serializers.ModelSerializer):
   
    topic = serializers.StringRelatedField()  # String representation of the topic
   
    like_count = serializers.SerializerMethodField()
    dislike_count = serializers.SerializerMethodField()
    participants_count = serializers.SerializerMethodField()  # New field for participants count

    class Meta:
        model = Room
        fields = [
            'id','topic', 'name', 'description', 
            'updated', 'created', 
            'like_count', 'dislike_count', 'participants_count'  # Add participants_count here
        ]

    def get_like_count(self, obj):
        return obj.likes.count()

    def get_dislike_count(self, obj):
        return obj.dislikes.count()

    def get_participants_count(self, obj):
        return obj.participants.count()  # Return the count of participants
