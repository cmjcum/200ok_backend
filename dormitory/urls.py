from django.urls import path
from .views import DormitoryView, Questionview

urlpatterns = [
    path('myroom/', DormitoryView.as_view(), name='myroom'),
    path('sorting/', DormitoryView.as_view(), name='sorting_dorm'),
    path('question/', Questionview.as_view()),
]