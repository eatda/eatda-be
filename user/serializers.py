from rest_framework import serializers
from user.models import Info, UserAllergy, Character, Group, BloodSugarLevel, OurPick
from django.contrib.auth import get_user_model

User = get_user_model()


# 유저 ID 정보
class InfoAuthSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Info
        fields = ['user_id', 'is_diabetes', 'character']


# 기본 유저 정보 (비당뇨인 전체 정보)
class InfoBasicSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(read_only=True)
    group_id = serializers.IntegerField(required=True)

    class Meta:
        model = Info
        fields = ['user_id', 'name', 'character', 'is_diabetes', 'group_id']

    def save(self, validated_data):
        social_id = validated_data.get('social_id')
        email = validated_data.get('email')
        user_id = User.objects.get(social_id=social_id, email=email).id
        name = validated_data.get('name')
        character = validated_data.get('character')
        is_diabetes = validated_data.get('is_diabetes')
        group_id = validated_data.get('group_id')

        info = Info(
            user_id=user_id,
            name=name,
            character=character,
            is_diabetes=is_diabetes,
            group_id=group_id
        )
        # 유저 정보 저장
        info.save()
        return info


# 유저 전체 정보 (당뇨인)
class InfoSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(read_only=True)
    height = serializers.FloatField(required=True)
    weight = serializers.FloatField(required=True)
    group_id = serializers.IntegerField(required=True)

    class Meta:
        model = Info
        fields = ['user_id', 'name', 'character', 'height', 'weight', 'gender', 'is_diabetes',
                  'activity', 'group_id']

    def validate(self, data):
        if data.get("gender") is None or data.get("activity") is None:
            raise serializers.ValidationError("You have to fill all information")
        return data

    def save(self, validated_data):
        social_id = validated_data.get('social_id')
        email = validated_data.get('email')
        user_id = User.objects.get(social_id=social_id, email=email).id
        name = validated_data.get('name')
        character = validated_data.get('character')
        height = validated_data.get('height')
        weight = validated_data.get('weight')
        gender = validated_data.get('gender')
        is_diabetes = validated_data.get('is_diabetes')
        activity = validated_data.get('activity')
        group_id = validated_data.get('group_id')

        info = Info(
            user_id=user_id,
            name=name,
            character=character,
            height=height,
            weight=weight,
            gender=gender,
            is_diabetes=is_diabetes,
            activity=activity,
            group_id=group_id
        )
        # 유저 정보 저장
        info.save()
        return info


# 캐릭터 리스트 정보
class CharacterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Character
        fields = ['id']


# 유저 알러지 정보
class UserAllergySerializer(serializers.ModelSerializer):
    allergy_name = serializers.SerializerMethodField(read_only=True)

    def get_user_id(self, obj):
        return obj.user.pk

    def get_allergy_id(self, obj):
        return obj.allergy.pk

    def get_allergy_name(self, obj):
        return obj.allergy.name

    class Meta:
        model = UserAllergy
        fields = ['user_id', 'allergy_id', 'allergy_name']


# 유저 그룹 정보
class GroupSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'code']


# 식후 혈당량 & 식단 정보
class BloodDietSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodSugarLevel
        fields = ['user_id', 'diet_id', 'time', 'level', 'timeline']


# 식후 혈당량 정보
class BloodSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)

    class Meta:
        model = BloodSugarLevel
        fields = ['id', 'time', 'level', 'timeline']
        read_only_fields = ('timeline',)
        extra_kwargs = {
            'time': {'required': True},
            'level': {'required': True}
        }

    def save(self, validated_data):
        id = validated_data.get("id")
        data = BloodSugarLevel.objects.get(id=id)
        data.level = validated_data.get("level")
        data.time = validated_data.get("time")
        data.save()
        return data


# 오늘의 식단 정보
class DietSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(required=True)
    diet_id = serializers.IntegerField(required=True)

    class Meta:
        model = BloodSugarLevel
        fields = ['user_id', 'diet_id', 'timeline']


# 유저의 OurPick
class OurPickSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(required=True)
    diet_id = serializers.IntegerField(required=True)

    def save(self, validated_data):
        user_id = validated_data.get('user_id')
        diet_id = validated_data.get('diet_id')

        ourpick = OurPick(
            user_id=user_id,
            diet_id=diet_id
        )

        ourpick.save()
        return ourpick

    class Meta:
        model = OurPick
        fields = ['user_id', 'diet_id']
