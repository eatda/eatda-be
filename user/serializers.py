from rest_framework import serializers
from user.models import Info, UserAllergy, Character, Group
from django.contrib.auth import get_user_model

User = get_user_model()


# 유저 ID 정보
class InfoAuthSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(read_only=True)
    character = serializers.SerializerMethodField(read_only=True)

    def get_character(self, obj):
        request = self.context.get('request')
        if obj.character.image:
            return request.build_absolute_uri(obj.character.image.url)
        return None

    class Meta:
        model = Info
        fields = ['user_id', 'is_diabetes', 'character']


# 유저 전체 정보
class InfoSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(read_only=True)
    character_id = serializers.IntegerField(write_only=True)
    character = serializers.SerializerMethodField(read_only=True)

    def get_character(self, obj):
        request = self.context.get('request')
        if obj.character.image:
            return request.build_absolute_uri(obj.character.image.url)
        return None

    class Meta:
        model = Info
        fields = ['user_id', 'name', 'character_id', 'character', 'height', 'weight', 'gender', 'is_diabetes',
                  'activity', 'group_id']

    def save(self, validated_data):
        social_id = validated_data.get('social_id')
        email = validated_data.get('email')
        user_id = User.objects.get(social_id=social_id, email=email).id
        name = validated_data.get('name')
        character_id = validated_data.get('character_id')
        height = validated_data.get('height')
        weight = validated_data.get('weight')
        gender = validated_data.get('gender')
        is_diabetes = validated_data.get('is_diabetes')
        activity = validated_data.get('activity')
        group_id = validated_data.get('group_id')

        info = Info(
            user_id=user_id,
            name=name,
            character_id=character_id,
            height=height,
            weight=weight,
            gender=gender,
            is_diabetes=is_diabetes,
            activity=activity,
            group_id=group_id
        )
        try:  # 유저 정보 저장
            info.save()
        except:
            raise serializers.ValidationError("Cannot save user")
        return info


# 캐릭터 리스트 정보
class CharacterSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField(read_only=True)

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None

    class Meta:
        model = Character
        fields = ['id', 'image']


# 유저 알러지 정보
class UserAllergySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAllergy
        fields = ['user_id', 'allergy_id']


# 유저 그룹 정보
class GroupSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'code']
