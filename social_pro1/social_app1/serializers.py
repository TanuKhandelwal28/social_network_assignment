from rest_framework import serializers
from social_app1.models import FriendRequest, User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password']

class FriendRequestSerializer(serializers.ModelSerializer):
    from_user_email = serializers.SerializerMethodField()
    to_user_email = serializers.SerializerMethodField()


    class Meta:
        model = FriendRequest
        fields = ['from_user_email', 'to_user_email', 'status', 'timestamp']


class CreateFriendRequestSerializer(serializers.Serializer):
    to_user_email = serializers.EmailField()

    def validate_to_user_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value

    def create(self, validated_data):
        from_user = self.context['request'].user
        to_user = validated_data.get('to_user_email')
        to_user = User.objects.get(email=to_user)


        # Check if a friend request already exists
        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
            raise serializers.ValidationError("Friend request already sent.")

        # Create a new friend request
        friend_request = FriendRequest.objects.create(from_user=from_user, to_user=to_user)
        return friend_request


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class HandleFriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ['id', 'status']

    def validate_status(self, value):
        if value not in ['accepted', 'rejected']:
            raise serializers.ValidationError("Invalid status.")
        return value

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance