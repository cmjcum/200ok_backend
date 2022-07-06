from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from user import serializers

from user.serializers import UserSerializer

from deeplearning.deeplearning_make_portrait import make_portrait
from multiprocessing import Process, Queue
from user.serializers import OriginalPicSerializer
from rest_framework.permissions import IsAuthenticated
from .models import OriginalPic
from .serializers import UserInfoSerializer

import boto3


class UserView(APIView):

    # 회원가입
    def post(self, request):
        user_serializer = UserSerializer(data=request.data)

        if user_serializer.is_valid(raise_exception=True):
            user_serializer.save()
            return Response({"messages" : "가입 성공"})
            # return Response(user_serializer.data, status=status.HTTP_200_OK)

        else:
            print(serializers.errors)
            return Response({"messages" : "가입 실패"})


q = Queue()
p = None
class MainView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, requeset):
        return Response({'msg': 'success'})
    
    def post(self, request):
        global q, p
        print(request.data)
        user_id = request.user.id
        request.data['user'] = user_id
        print(request.data)
        pic = request.data.pop('pic')[0]
        filename = pic.name
        print(filename)

        s3 = boto3.client('s3')
        s3.put_object(
            ACL="public-read",
            Bucket="200okhg",
            Body=pic,
            Key=filename,
            ContentType=pic.content_type)

        url = f'https://200okhg.s3.ap-northeast-2.amazonaws.com/{filename}'
        request.data['pic'] = url

        original_pic_serializer = OriginalPicSerializer(data=request.data)

        if original_pic_serializer.is_valid():
            original_pic_serializer.save()

            p = Process(target=make_portrait, args=(q, url, user_id))
            p.start()

            return Response({'msg': 'send'}, status=status.HTTP_200_OK)

        print(original_pic_serializer.error_messages)

        return Response({"error": "failed"}, status=status.HTTP_400_BAD_REQUEST)



class InfoView(APIView):

    def get(self, request):
        return Response({'msg': 'get'}, status=status.HTTP_200_OK)

    def post(self, request):
        global p, q
        print(request.data)
        if p is not None:
            p.join()

            request.data['user'] = request.user.id
            request.data['portrait'] = q.get()

            print(request.data)

            userinfo_serializer = UserInfoSerializer(data=request.data)
            print(userinfo_serializer)

            if userinfo_serializer.is_valid():
                userinfo_serializer.save()
                return Response({'msg': 'success'}, status=status.HTTP_200_OK)
        print(userinfo_serializer.error_messages)
        return Response({'error': 'failed'}, status=status.HTTP_400_BAD_REQUEST)
