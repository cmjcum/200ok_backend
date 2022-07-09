from rest_framework import serializers
from .models import Board
from user.models import User
from dormitory.models import Dormitory
from django.utils import timezone, dateformat


class DormitoriesSerializer(serializers.ModelSerializer):
    users = serializers.SerializerMethodField()

    def get_users(self, obj):
        users = obj.userinfo_set.filter(dormitory=obj.id).values()
        portrait = obj.userinfo_set.filter(dormitory=obj.id)[0].portrait
        users.portrait = portrait
        return users

    class Meta:
        model = Dormitory
        fields = ["name", "users"]


class DormitorySerializer(serializers.ModelSerializer):
    users = serializers.SerializerMethodField(read_only=True)

    def get_users(self, obj):
        return obj.userinfo_set.filter(dormitory=obj.id).order_by("?").values()

    class Meta:
        model = Dormitory
        fields = ["name", "desc", "logo", "users"]


class BoardSerializer(serializers.ModelSerializer):
    icon = serializers.SerializerMethodField(read_only=True)
    author_name = serializers.SerializerMethodField(read_only=True)
    created = serializers.SerializerMethodField(read_only=True)
    dorm_name = serializers.SerializerMethodField(read_only=True)

    def get_author_name(self, obj):
        return User.objects.get(username=obj.author).fullname

    def get_dorm_name(self, obj):
        return obj.author.userinfo.dormitory.name

    def get_icon(self, obj):
        try:
            dorm_name = obj.author.userinfo.dormitory
            dorm = Dormitory.objects.get(name=dorm_name)
            icon = dorm.logo.url
            return icon
        except:
            return ''

    def get_created(self, obj):
        return dateformat.format(obj.created, 'y.m.d')

    def validate(self, data):
        if len(data.get('content')) <= 5:
            raise serializers.ValidationError(
                detail={"error": "5글자를 넘아야 합니다."},
            )

        return data

    def create(self, validated_data):
        cemment = Board(**validated_data)
        cemment.save()

        return validated_data

    def update(self, instance, validated_data):
        formatted_date = dateformat.format(timezone.now(), 'y.m.d H:i')

        for key, value in validated_data.items():
            if key == 'content':
                value = value + f' ({formatted_date} 수정)'
                setattr(instance, key, value)
        instance.save()

        return instance

    class Meta:
        model = Board
        fields = "__all__"


class UserInfoSerializer(serializers.ModelSerializer):
    portrait = serializers.SerializerMethodField(read_only=True)
    dormitory_name = serializers.SerializerMethodField(read_only=True)

    def get_portrait(self, obj):
        portrait = obj.userinfo.portrait
        return portrait

    def get_dormitory_name(self, obj):
        dormitory_name = obj.userinfo.dormitory.name
        return dormitory_name

    class Meta:
        model = User
        fields = ["id", "username", "fullname", "portrait", "dormitory_name"]

