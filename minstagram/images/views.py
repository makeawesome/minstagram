from rest_framework.views import APIView # Get and show elements, and handle http methods
from rest_framework.response import Response
from rest_framework import status
from . import models, serializers
from minstagram.users import models as user_models
from minstagram.users import serializers as user_serializers
from minstagram.notifications import views as notification_views

# following 유저들이 업로드한 사진을 가져온다.
class Feed(APIView):

    def get(self, request, format=None): # format이 지정되지 않으면 JSON으로 Response
        user = request.user
        following_users = user.following.all() # Feed를 요청한 유저가 following 하고 있는 사람들

        image_list = []

        # 내가 업로드한 이미지를 가지고 온다.
        my_images = user.images.all()[:2]

        for image in my_images:
            image_list.append(image)

        # following 하고 있는 사람들이 업로드한 이미지를 가지고 온다.
        for following_user in following_users:
            # images는 image model의 creator field에 지정한 related_name.
            # related_name을 지정하지 않았다면, images 대신 image_set이 쓰여졌을 것이다.
            # images(=image_set)는 user model의 필드로, 유저가 업로드한 image의 id를 모은 'set'이다.
            user_images = following_user.images.all()[:2]

            for image in user_images:
                image_list.append(image)

        sorted_list = sorted(image_list, key=lambda x: x.created_at, reverse=True) # image가 시간 순으로 정렬되도록 함

        serializer = serializers.ImageSerializer(sorted_list, many=True) # many=True 복수 개의 object를 serialize

        return Response(serializer.data) # serialized 된 데이터는 data에 저장되어있다.


# image에 like 추가/조회
class LikeImage(APIView):

    # like 조회
    def get(self, request, image_id, format=None):
        likes = models.Like.objects.filter(image__id=image_id) # image에 달린 likes
        like_creators_ids = likes.values('creator_id')  # likes를 누른 users' ids
        users = user_models.User.objects.filter(id__in=like_creators_ids) # user id로 user 정보를 가지고 온다.

        serializer = user_serializers.ListUserSerializer(users, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    # like 추가
    def post(self, request, image_id, format=None):
        user = request.user

        #id로 image를 찾는다.
        try:
            found_image = models.Image.objects.get(id=image_id)

        except models.Image.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # 이미 like한 image이면 like 유지
        try:
            preexisting_like = models.Like.objects.get(
                creator = user,
                image = found_image,
            )

            return Response(status=status.HTTP_304_NOT_MODIFIED)

        # like 되어 있지 않으면 like 추가
        except models.Like.DoesNotExist:
            new_like = models.Like.objects.create(
                creator=user,
                image=found_image,
            )
            new_like.save() # like 추가

            notification_views.CreateNotification(user, found_image.creator, 'like', found_image)

            return Response(status=status.HTTP_201_CREATED)


# image에 like 제거
class UnlikeImage(APIView):

    def delete(self, request, image_id, format=None):
        user = request.user

        #id로 image를 찾는다.
        try:
            found_image = models.Image.objects.get(id=image_id)

        except models.Image.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # 이미 like한 image이면 like 취소
        try:
            preexisting_like = models.Like.objects.get(
                creator=user,
                image=found_image,
            )
            preexisting_like.delete() # like 기록 삭제

            return Response(status=status.HTTP_204_NO_CONTENT)

        # like 되어 있지 않으면 동작하지 않음
        except models.Like.DoesNotExist:
            return Response(status=status.HTTP_304_NOT_MODIFIED)


# image에 comment 추가
class CommentOnImage(APIView):

    def post(self, request, image_id, format=None):
        user = request.user

        # id로 이미지를 찾는다.
        try:
            found_image = models.Image.objects.get(id=image_id)
        except models.Image.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = serializers.CommentSerializer(data=request.data) # JSON을 파이썬 객체로 변환

        # data의 유효성을 판단.
        # commentSerializer의 field 중 id는 사용자가 관여할 수 없고, creator는 read_only이므로 message의 유효성만 판단한다.
        if serializer.is_valid():
            serializer.save(    # serialized 된 데이터에 creator, image를 추가하여 DB에 저장
                creator=user,
                image=found_image,
            )

            notification_views.CreateNotification(user, found_image.creator, 'comment', found_image, serializer.data['message'])

            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# comment 삭제
class Comment(APIView):

    def delete(self, request, comment_id, format=None):

        user = request.user

        # comment id와 user로 자신이 쓴 comment 찾기
        try:
            comment = models.Comment.objects.get(id=comment_id, creator=user)
            comment.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        except models.Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

# hashtag 검색
class Search(APIView):

    def get(self, request, format=None):
        
        hashtags = request.query_params.get('hashtags', None)

        if hashtags is not None:
            hashtags = hashtags.split(',')

            images = models.Image.objects.filter(tags__name__in=hashtags).distinct()

            serializer = serializers.CountImageSerializer(images, many=True)

            return Response(data=serializer.data, status=status.HTTP_200_OK)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


# image에 달린 comment 삭제
class ModerateComments(APIView):

    def delete(self, request, image_id, comment_id, format=None):
        user = request.user

        # image__creator에서 user가 image를 업로드한 사람과 동일한지 확인
        try:
            comment_to_delete = models.Comment.objects.get(
                id=comment_id, image__id=image_id, image__creator=user)

            comment_to_delete.delete()
            
        except models.Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)


# image 하나만 상세히 조회/수정/삭제
class ImageDetail(APIView):

    def find_own_image(self, image_id, user):
        try:
            image = models.Image.objects(id=image_id, creator=user)
            return image
        except models.Image.DoesNotExist:
            return None

    # image 조회
    def get(self, request, image_id, format=None):

        try:
            image = models.Image.objects.get(id=image_id)
        except models.Image.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = serializers.ImageSerializer(image)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    # image 수정
    def put(self, request, image_id, format=None):
        user = request.user

        image = self.find_own_image(image_id, user)

        if image is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        try:
            image = models.Image.objects(id=image_id, creator=user)
        except models.Image.DoesNotExist:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = serializers.InputImageSerializer(image, data=request.data, partial=True) # partial=True는 모든 fields를 작성할 필요 없다는 의미

        if serializers.is_valid():
            serializers.save(creator=user)
            return Response(data=serializers.data, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(data=serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # image 삭제
    def delete(self, request, image_id, format=None):
        user = request.user
        image = self.find_own_image(image_id, user)

        if image is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        image.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)