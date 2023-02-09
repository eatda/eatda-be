from rest_framework import serializers
from user.models import Info, UserAllergy, Character, Group, BloodSugarLevel, OurPick, Like
from diet.serializers import DietSimpleSerializer
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
    group = serializers.CharField(required=True)
    group_code = serializers.SerializerMethodField(read_only=True)

    def get_group_code(self, obj):
        return obj.group.code

    class Meta:
        model = Info
        fields = ['user_id', 'name', 'character', 'is_diabetes', 'group', 'group_code']

    def save(self, validated_data):
        social_id = validated_data.get('social_id')
        email = validated_data.get('email')
        user_id = User.objects.get(social_id=social_id, email=email).id
        name = validated_data.get('name')
        character = validated_data.get('character')
        is_diabetes = validated_data.get('is_diabetes')
        group = validated_data.get('group')
        group_id = Group.objects.get(code=group).id

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
    group = serializers.CharField(required=True)
    group_code = serializers.SerializerMethodField(read_only=True)

    def get_group_code(self, obj):
        return obj.group.code

    class Meta:
        model = Info
        fields = ['user_id', 'name', 'character', 'height', 'weight', 'gender', 'age', 'is_diabetes',
                  'activity', 'group', 'group_code', 'bmr', 'amr']
        extra_kwargs = {
            'height': {'required': True},
            'weight': {'required': True},
            'gender': {'required': True},
            'activity': {'required': True},
            'age': {'required': True}
        }

    # 기초 대사량 계산
    def cal_bmr(self, g, w, h, a):
        result = (9.99 * w) + (6.25 * h) - (4.95 * a)
        if g == 'f':  # 여성
            return result - 161.0
        else:  # 남성
            return result + 5.0

    # 활동 대사량 계산
    def cal_amr(self, bmr, act):
        multipliers = [1.2, 1.375, 1.55, 1.725, 1.9]
        return bmr * multipliers[act]

    def save(self, validated_data):
        social_id = validated_data.get('social_id')
        email = validated_data.get('email')
        user_id = User.objects.get(social_id=social_id, email=email).id
        name = validated_data.get('name')
        character = validated_data.get('character')
        height = validated_data.get('height')
        weight = validated_data.get('weight')
        gender = validated_data.get('gender')
        age = validated_data.get('age')
        is_diabetes = validated_data.get('is_diabetes')
        activity = validated_data.get('activity')
        group = validated_data.get('group')
        group_id = Group.objects.get(code=group).id
        bmr = self.cal_bmr(gender, weight, height, age)

        info = Info(
            user_id=user_id,
            name=name,
            character=character,
            height=height,
            weight=weight,
            gender=gender,
            age=age,
            is_diabetes=is_diabetes,
            activity=activity,
            group_id=group_id,
            bmr=bmr,
            amr=self.cal_amr(bmr, activity)
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
    diet = serializers.SerializerMethodField(read_only=True)
    date = serializers.SerializerMethodField(read_only=True)
    range = serializers.SerializerMethodField(read_only=True)

    def get_range(self, obj):
        if obj.level >= 140:  # 고혈당
            return 2
        elif obj.level >= 70:  # 정상 혈당
            return 1
        else:  # 저혈당
            return 0

    def get_diet(self, obj):
        diet_serializer = DietSimpleSerializer(obj.diet, context=self.context)
        return diet_serializer.data

    def get_date(self, obj):
        return str(obj.created_at)[2:10].replace('-', '.')

    class Meta:
        model = BloodSugarLevel
        depth = 1
        fields = ['id', 'diet', 'date', 'time', 'level', 'timeline', 'range']
        read_only_fields = ('id',)


# 식후 혈당량 정보
class BloodSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)
    range = serializers.SerializerMethodField(read_only=True)

    def get_range(self, obj):
        if obj.level >= 140:  # 고혈당
            return 2
        elif obj.level >= 70:  # 정상 혈당
            return 1
        else:  # 저혈당
            return 0

    class Meta:
        model = BloodSugarLevel
        fields = ['id', 'time', 'level', 'timeline', 'range']
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
    user_id = serializers.UUIDField(required=True, write_only=True)
    diet_id = serializers.IntegerField(required=True, write_only=True)
    diet = serializers.SerializerMethodField(read_only=True)
    date = serializers.SerializerMethodField(read_only=True)

    def get_diet(self, obj):
        diet_serializer = DietSimpleSerializer(obj.diet, context=self.context)
        return diet_serializer.data

    def get_date(self, obj):
        return str(obj.created_at)[2:10].replace('-', '.')

    class Meta:
        model = BloodSugarLevel
        depth = 1
        fields = ['id', 'user_id', 'diet_id', 'diet', 'date', 'timeline']
        read_only_fields = ('id',)


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


# 유저가 홈화면에서 좋아요 눌렀을 때 api
class HomeLikeSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(required=True)

    def save(self, validated_data):
        user_id = validated_data.get('user_id')
        react = validated_data.get('react')
        target = validated_data.get('target')
        timeline = validated_data.get('timeline')

        like = Like(
            user_id = user_id,
            react = react,
            target = target,
            timeline = timeline
        )
        like.save()
        return like

    class Meta:
        model = Like
        fields = ['user_id', 'react', 'target', 'timeline']


