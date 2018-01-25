from rest_framework.views import APIView # Get and show elements, and handle http methods
from rest_framework.response import Response
from . import models, serializers

class Feed(APIView):

    # following 유저들이 업로드한 사진을 가져온다.
    def get(self, request, format=None): # format이 지정되지 않으면 JSON으로 Response
        user = request.user
        following_users = user.following.all()

        image_list = []

        for following_user in following_users:
            user_images = following_user.images.all()[:2] # images는 image model의 creator field에 지정한 related_name

            for image in user_images:
                image_list.append(image)
        
        sorted_list = sorted(image_list, key=lambda x: x.created_at, reverse=True) # image가 시간 순으로 정렬되도록 함

        serializer = serializers.ImageSerializer(sorted_list, many=True) # many=True 복수 개의 object를 serialize

        return Response(serializer.data) # serialized 된 데이터는 data에 저장되어있다.
