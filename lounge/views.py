from dataclasses import field
import django.apps
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.shortcuts import render, redirect
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import BoardSerializer, UserInfoSerializer, DormitorySerializer, DormitoriesSerializer
from .models import Board
from user.models import User, UserInfo
from dormitory.models import Dormitory


class LoungeView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    # permission_classes = [permissions.IsAuthenticated]


    # TODO  라운지 페이지 띄우기
    def get(self, request):
        user = request.user
        userinfo = User.objects.filter(id=user.id)
        userdorm = Dormitory.objects.filter(name=user.userinfo.dormitory.name)
        dorm = Dormitory.objects.all()
        dorm_count = dorm.count()
        board = Board.objects.all().order_by('-created')

        lounge_serialrzer = UserInfoSerializer(userinfo, many=True).data
        dormitory_serializer = DormitorySerializer(userdorm, many=True).data
        dormitories_serializer = DormitoriesSerializer(dorm, many=True).data
        board_serializer = BoardSerializer(board, many=True).data

        dorm_name_list = [dormitories_serializer[i]['name'] for i in range(dorm_count)]
        dorm_users_count_list = [dormitories_serializer[i]['users'].count() for i in range(dorm_count)]
        
        comments_list = [board_serializer[i]['dorm_name'] for i in range(board.count())]
        comments_count_list = []
        for dorm in dorm_name_list:
            cnt = comments_list.count(dorm)
            comments_count_list.append(cnt)
        
        dormitory_serializer[0]['users'] = dormitory_serializer[0]['users'].exclude(user_id=user.id)

        if len(dormitory_serializer[0]['users']) == 0:
            dormitory_serializer[0]['users'] = None

        if len(dormitory_serializer[0]['users']) >= 5:
                dormitory_serializer[0]['users'] = dormitory_serializer[0]['users'][:5]

        lounge_data = {
            "user": lounge_serialrzer,
            "house": dormitory_serializer,
            "dorm_name":dorm_name_list,
            "users_count": dorm_users_count_list,
            "comments_count":comments_count_list,
            "board": board_serializer
        }

        return Response(lounge_data, status=status.HTTP_200_OK)

    # TODO 게시글 쓰기
    def post(self, request):
        request.data['author'] = request.user.id
        board_serializer = BoardSerializer(data=request.data)

        if board_serializer.is_valid():
            board_serializer.save()
            # return redirect('lounge')
            return Response(board_serializer.data, status=status.HTTP_200_OK)

        return Response(board_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # TODO 게시글 수정
    def put(self, request, obj_id):
        comment = Board.objects.get(id=obj_id)
        board_serializer = BoardSerializer(comment, data=request.data, partial=True)
        # print(f'author: {comment.author}, user: {request.user.username}')

        if comment.author == request.user:
            if board_serializer.is_valid():
                board_serializer.save()
                # return redirect('lounge')
                return Response(board_serializer, status=status.HTTP_200_OK)

            return Response(board_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': '이 글을 작성한 사람이 아닙니다!'}, status=status.HTTP_400_BAD_REQUEST)

    # TODO 게시글 삭제
    def delete(self, request, obj_id):
        comment = Board.objects.get(id=obj_id)

        if comment.author == request.user:
            comment.delete()
            return Response({'message': '삭제완료!'}, status=status.HTTP_200_OK)
            
        return Response({'message': '이 글을 작성한 사람이 아닙니다!'}, status=status.HTTP_400_BAD_REQUEST)