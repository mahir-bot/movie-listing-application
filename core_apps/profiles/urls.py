from django.urls import path
from .views import ProfileDetailAPIView, ProfileListAPIView, UpdateProfileAPIView,FollowerListView, FollowingListView, FollowAPIView,UnfollowAPIView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('all/', ProfileListAPIView.as_view(), name='all-profile'),
    path('me/', ProfileDetailAPIView.as_view(), name='profile-detail'),
    path('me/update/', UpdateProfileAPIView.as_view(), name='update-profile'),
    path('me/followers/', FollowerListView.as_view(), name='followers'),
    path('me/following/', FollowingListView.as_view(), name='following'),
    path('<uuid:user_id>/follow/', FollowAPIView.as_view(), name='follow'),
    path('<uuid:user_id>/unfollow/', UnfollowAPIView.as_view(), name='unfollow'),
]
