from django.core.validators import MinValueValidator, MaxValueValidator
from account.models import BaseModel
from django.db import models
from django.contrib.auth import get_user_model
from diet.models import Data, DietAllergy

User = get_user_model()


# 그룹 테이블
class Group(BaseModel):
    code = models.CharField(max_length=10, unique=True)  # 그룹코드


# 캐릭터 테이블
class Character(BaseModel):
    class CharacterType(models.IntegerChoices):  # 캐릭터 이미지
        MOM = 0  # 엄마
        DAD = 1  # 아빠
        BROTHER1 = 2  # 형제1
        BROTHER2 = 3  # 형제2
        BROTHER3 = 4  # 형제3

    id = models.PositiveIntegerField(primary_key=True, choices=CharacterType.choices)  # id
    image = models.ImageField(upload_to='images/', default='default.jpg')  # 캐릭터 이미지


# 유저 정보 테이블
class Info(BaseModel):
    class ActivityType(models.IntegerChoices):  # 활동수준
        NOCHOICES = -1  # 선택을 안 했을 때(비 당뇨인의 경우)
        DEEPLOW = 0  # 활동이 적거나 운동을 안하는 경우
        LOW = 1  # 가벼운 활동 및 운동
        MIDDLE = 2  # 보통의 활동 및 운동
        HIGH = 3  # 적극적인 활동 및 운동
        DEEPHIGH = 4  # 매우 적극적인 활동 및 운동

    class GenderType(models.TextChoices):  # 성별
        FEMALE = 'f'
        MALE = 'm'

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)  # 로그인테이블 ID
    name = models.CharField(max_length=20)  # 이름
    character = models.ForeignKey(Character, on_delete=models.SET_NULL, null=True)  # 캐릭터 ID
    height = models.FloatField(default=None, null=True)  # 키
    weight = models.FloatField(default=None, null=True)  # 몸무게
    gender = models.CharField(max_length=1, choices=GenderType.choices)  # 성별
    is_diabetes = models.BooleanField(default=False)  # 당뇨환자여부
    activity = models.IntegerField(default=ActivityType.NOCHOICES, choices=ActivityType.choices)  # 활동수준
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True)  # 그룹코드 ID


# 식후 혈당량 테이블
class BloodSugarLevel(BaseModel):
    class TimelineType(models.IntegerChoices):  # 시간대
        MORNING = 0  # 아침
        AFTERNOON = 1  # 점심
        NIGHT = 2  # 저녁

    user = models.ForeignKey(Info, on_delete=models.SET_NULL, null=True)  # 유저 id
    diet = models.ForeignKey(Data, on_delete=models.SET_NULL, null=True)  # 식단 id
    time = models.DateTimeField(default=None, null=True)  # 혈당측정시간
    level = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(300)], default=None,
                                null=True)  # 혈당량
    timeline = models.IntegerField(choices=TimelineType.choices)  # 시간대


# 좋아요 테이블
class Like(BaseModel):
    class ReactionType(models.IntegerChoices):  # 좋아요 반응
        HEART = 0  # 하트
        SMILE = 1  # 웃음
        SAD = 2  # 슬픔

    class TargetType(models.IntegerChoices):  # 좋아요 대상 필드
        TODAYDIET = 0  # 오늘의 식단 필드
        AFTERBLOOD = 1  # 식후 혈당량 필드

    class TimelineType(models.IntegerChoices):  # 시간대
        MORNING = 0  # 아침
        AFTERNOON = 1  # 점심
        NIGHT = 2  # 저녁

    user = models.ForeignKey(Info, on_delete=models.SET_NULL, null=True)  # 유저 id
    react = models.IntegerField(choices=ReactionType.choices, default=ReactionType.HEART)  # 좋아요 반응
    target = models.IntegerField(choices=TargetType.choices)  # 좋아요 대상 필드
    timeline = models.IntegerField(choices=TimelineType.choices)  # 시간대


# 선호 레시피 테이블
class OurPick(BaseModel):
    diet = models.ForeignKey(Data, on_delete=models.CASCADE)  # 식단 ID
    user = models.ForeignKey(Info, on_delete=models.CASCADE)  # 유저


# 유저 알러지 테이블
class UserAllergy(BaseModel):
    user = models.ForeignKey(Info, on_delete=models.CASCADE)  # 유저
    allergy = models.ForeignKey(DietAllergy, on_delete=models.CASCADE)  # 알러지 ID
