from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from social_app1.models import FriendRequest, User
from social_app1.serializers import UserSerializer, FriendRequestSerializer, LoginSerializer,HandleFriendRequestSerializer, CreateFriendRequestSerializer
from rest_framework.decorators import permission_classes
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView, GenericAPIView
from django.http import Http404
from django.utils.timezone import now, timedelta
from rest_framework.exceptions import Throttled

# User = get_user_model()

class SignupView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        email = request.data.get('email', '').lower()
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        password = request.data.get('password', '')  #   Get password from the request

        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        if not password:
            return Response({'error': 'Password is required'}, status=status.HTTP_400_BAD_REQUEST)

        user = User(email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)  # Set the hashed password
        user.save()

        return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)

# Custom Login view (email case-insensitive)
class CustomLoginView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer  # Specify the serializer for validation

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email'].lower()  # Make email case-insensitive
        password = serializer.validated_data['password']
        
        user = authenticate(username=email, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

# Search users by email or name
class SearchUserView(generics.ListAPIView):
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    permission_classes = [AllowAny]

    def get_queryset(self):
        keyword = self.request.query_params.get('search', '').lower()
        if '@' in keyword:
            return User.objects.filter(email__iexact=keyword)
        else:
            return User.objects.filter(
                Q(email__icontains=keyword) |
                Q(first_name__icontains=keyword) |
                Q(last_name__icontains=keyword)
            )
# Send friend request
class SendFriendRequestView(generics.CreateAPIView):
    serializer_class = CreateFriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Check how many friend requests have been sent in the last minute
        one_minute_ago = now() - timedelta(minutes=1)
        recent_requests_count = FriendRequest.objects.filter(
            from_user=request.user,
            timestamp__gte=one_minute_ago
        ).count()

        if recent_requests_count >= 3:
            raise Throttled(detail="You have exceeded the limit of 3 friend requests per minute.", code='throttled')

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        friend_request = serializer.save()

        # Serialize the output using FriendRequestSerializer
        response_serializer = FriendRequestSerializer(friend_request)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
from django.contrib.auth import login, authenticate

# Accept/Reject friend request
class HandleFriendRequestView(generics.UpdateAPIView):
    serializer_class = HandleFriendRequestSerializer
    permission_classes = [IsAuthenticated]
    queryset = FriendRequest.objects.all()  # Ensure to provide the queryset

    def get_object(self):
        request_id = self.kwargs.get('pk')  # Use 'pk' if you are using a URL parameter for the ID
        friend_request = FriendRequest.objects.filter(id=request_id).first()
        
        try:
            if friend_request.to_user != self.request.user:
                login(self.request, friend_request.to_user)

            friend_request = FriendRequest.objects.get(id=request_id, to_user=self.request.user)
            return friend_request
        except FriendRequest.DoesNotExist:
            raise Http404

    def update(self, request, *args, **kwargs):
        partial = True  # Update only provided fields
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({'detail': f'Friend request {serializer.validated_data["status"]}.'}, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        serializer.save()

# List friends
class ListFriendsView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(received_requests__from_user=self.request.user, received_requests__status='accepted')    


# List pending friend requests
class ListPendingRequestsView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        pending_requests = FriendRequest.objects.filter(status='pending')
        if pending_requests:
            return FriendRequest.objects.filter(status='pending')
