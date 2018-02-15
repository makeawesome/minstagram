# Get and show elements, and handle http methods
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter # Facebook Login
from rest_auth.registration.views import SocialLoginView # Facebook Login
from . import models, serializers
from minstagram.notifications import views as notification_views

class ExploreUsers(APIView):

    def get(self, request, format=None):
        last_five = models.User.objects.all().order_by('-date_joined')[:5]

        serializer = serializers.ListUserSerializer(last_five, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


# follow an user
class FollowUser(APIView):

    def post(self, request, user_id, format=None):
        user = request.user

        try:
            user_to_follow = models.User.objects.get(id=user_id)
        except models.User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        user.following.add(user_to_follow)
        user.save() # following list에 추가

        # user_to_follow의 follower에도 변화가 있어야 하는데?

        # user_to_follow에게 notification 전송
        notification_views.CreateNotification(user, user_to_follow, 'follow')

        return Response(status=status.HTTP_200_OK)


# unfollow an user
class UnfollowUser(APIView):

    def post(self, request, user_id, format=None):
        user = request.user

        try:
            user_to_unfollow = models.User.objects.get(id=user_id)
        except models.User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        user.following.remove(user_to_unfollow) # remove()는 many-to-many 관계 제거(following 하는 사람 중 한 명이 없어짐). delete()는 object 제거
        user.save()

        return Response(status=status.HTTP_200_OK)

# user profile 조회/수정
class UserProfile(APIView):

    def get_user(self, user_name):
        try:
            found_user = models.User.objects.get(username=user_name)
        except models.User.DoesNotExist:
            return None

    # 조회
    def get(self, request, user_name, format=None):
        found_user = self.get_user(user_name)

        if found_user is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = serializers.UserProfileSerializer(found_user)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    # 수정
    def put(self, request, user_name, format=None):
        found_user = self.get_user(user_name)

        if found_user is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        elif found_user.username != user.username:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        else:
            serializer = serializers.UserProfileSerializer(found_user, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            

# User의 follower 리스트
class UserFollowers(APIView):

    def get(self, request, user_name, format=None):

        try:
            found_user = models.User.objects.get(username=user_name)
        except models.User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        user_followers = found_user.followers.all()

        serializer = serializers.ListUserSerializer(user_followers, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

# User의 following 리스트
class UserFollowing(APIView):

    def get(self, request, user_name, format=None):
        try:
            found_user = models.User.objects.get(username=user_name)
        except models.User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        user_following = found_user.following.all()

        serializer = serializers.ListUserSerializer(user_following, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

class Search(APIView):

    def get(self, request, format=None):

        username = request.query_params.get('username', None)
        
        if username is not None:
            users = models.User.objects.filter(username__icontains=username)

            serializer = serializers.ListUserSerializer(users, many=True)

            return Response(data=serializer.data, status=status.HTTP_200_OK)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


# 비밀번호 변경
class ChangePassword(APIView):

    def put(self, request, user_name, format=None):
        user = request.user

        # 비밀번호 변경 신청 유저가 본인이 맞는지 확인
        if user.username != user_name:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # 사용자가 입력한 현재 비밀번호
        current_password = request.data.get('current_password', None)
        # 사용자가 입력한 새로운 비밀번호
        new_password = request.data.get('new_password', None)

        if current_password is not None and new_password is not None:
            # 사용자가 입력한 현재 비밀번호가 실제 저장된 비밀번호와 일치하는지 확인
            password_match = user.check_password(current_password) # django에서 제공하는 method

            # 일치한다면 새로운 비밀번호로 변경
            if password_match:
                user.set_password(new_password) # django에서 제공하는 method
                user.save()

                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


# Facebook Login
class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter