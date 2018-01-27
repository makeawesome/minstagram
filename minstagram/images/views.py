from rest_framework.views import APIView # Get and show elements, and handle http methods
from rest_framework.response import Response
from rest_framework import status
from . import models, serializers

# following 유저들이 업로드한 사진을 가져온다.
class Feed(APIView):

    def get(self, request, format=None): # format이 지정되지 않으면 JSON으로 Response
        user = request.user
        following_users = user.following.all() # Feed를 요청한 유저가 following 하고 있는 사람들

        image_list = []

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


# image에 like 추가
class LikeImage(APIView):

    def get(self, request, image_id, format=None):
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
