from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from dormitory.serializers import DormUserSerializer, QuestionSerializer
from dormitory.models import Question


class DormitoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        return Response(DormUserSerializer(user).data)


class Questionview(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        questions = Question.objects.all()
        question_serializer = QuestionSerializer(questions, many=True).data

        return Response({'questions': question_serializer}, status=status.HTTP_200_OK)

        