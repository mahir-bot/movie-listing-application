#TODO: Change this in production
from core.settings.local import DEFAULT_FROM_EMAIL

from django.contrib.auth import get_user_model
from django.core.mail import send_mail


from rest_framework import status,generics
from rest_framework.exceptions import NotFound
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .exceptions import CantFollowYourself
from .models import Profile
from .pagination import ProfilePagination
from .renderers import ProfileJSONRenderer, ProfilesJSONRenderer
from .serializers import ProfileSerializer,FollowingSerializer,UpdateProfileSerializer

User = get_user_model()

class ProfileListAPIView(generics.ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    pagination_class = ProfilePagination
    renderer_classes = [ProfileJSONRenderer]

class ProfileDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer
    renderer_classes = (ProfileJSONRenderer, )

    def get_queryset(self):
        queryset = Profile.objects.select_related('user')
        return queryset
    def get_object(self):
        user = self.request.user
        profile = self.get_queryset().get(user=user)
        return profile
    
class UpdateProfileAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateProfileSerializer
    parser_classes = [MultiPartParser]
    renderer_classes = [ProfileJSONRenderer]

    def get_object(self):
        return self.request.user.profile
    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class FollowerListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request,format=None):
        try:
            profile = Profile.objects.get(user__id=request.user.id)
            follower_profiles = profile.followers.all()
            serializers = FollowingSerializer(follower_profiles, many=True)
            formatter_response = {
                "status_code":status.HTTP_200_OK,
                "followers_count": follower_profiles.count(),
                "followers":serializers.data
            }
            return Response(formatter_response,status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
class FollowingListView(APIView):
    def get(self, request,user_id,format=None):
        try:
            profile = Profile.objects.get(user__id=user_id)
            following_profiles = profile.following.all()
            users = [p.user for p in following_profiles]
            serializers = FollowingSerializer(users, many=True)
            formatter_response = {
                "status_code":status.HTTP_200_OK,
                "following_count": following_profiles.count(),
                "users_i_follow":serializers.data
            }
            return Response(formatter_response,status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        

class FollowAPIView(APIView):

    def post(self, request, user_id, format=None):
        try:
            follower = Profile.objects.get(user=self.request.user)
            user_profile = request.user.profile
            profile = Profile.objects.get(user__id=user_id)
            
            if profile == follower:
                raise CantFollowYourself
            if user_profile.check_following(profile):
                formatter_response = {
                "status_code":status.HTTP_400_BAD_REQUEST,
                "message":f"You are already following {profile.user.first_name} {profile.user.last_name}",
            }
                return Response(formatter_response,status=status.HTTP_400_BAD_REQUEST)
            user_profile.follow(profile)
            subject = "A new user follows you"
            message = f"{profile.user.first_name} {profile.user.last_name} is now following you"
            from_email = DEFAULT_FROM_EMAIL
            recipient_list = [profile.user.email]
            send_mail(subject, message, from_email, recipient_list,fail_silently=True)
            formatter_response = {
                "status_code":status.HTTP_200_OK,
                "message":f"You are now following {profile.user.first_name} {profile.user.last_name}",
            }
            return Response(formatter_response,status=status.HTTP_200_OK) 
        except Profile.DoesNotExist:
            return NotFound("Profile not found")

class UnfollowAPIView(APIView):
    def post(self, request, user_id, *args,**kwargs):
        user_profile = request.user.profile
        profile = Profile.objects.get(user__id=user_id)
        
        if not user_profile.check_following(profile):
            formatted_response={
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": f"You can't unfollow {profile.user.first_name} {profile.user.last_name}, You are not following {profile.user.first_name} {profile.user.last_name}"
            }
            
            return Response(formatted_response,status.HTTP_400_BAD_REQUEST,)
        user_profile.unfollow(profile)
        formatter_response = {
                "status_code":status.HTTP_200_OK,
                "message":f"You have unfollowed {profile.user.first_name} {profile.user.last_name}",
            }
        return Response(formatter_response,status=status.HTTP_200_OK)
        