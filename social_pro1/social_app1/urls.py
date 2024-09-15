from django.urls import path
from social_app1.views import SignupView, CustomLoginView, SearchUserView, SendFriendRequestView, HandleFriendRequestView, ListFriendsView, ListPendingRequestsView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('search/', SearchUserView.as_view(), name='search_users'),
    path('send-friend-request/', SendFriendRequestView.as_view(), name='send_friend_request'),
    path('handle_friend_request/<int:pk>/', HandleFriendRequestView.as_view(), name='handle_friend_request'),
    path('friends/', ListFriendsView.as_view(), name='list_friends'),
    path('friend-request/pending/', ListPendingRequestsView.as_view(), name='pending_requests'),
]
