from django.db import models

# Create your models here.
import accounts.models

# 그룹 테이블
class Group(accounts.models.BaseModel):
    code = models.CharField(max_length=10, unique=True)     #그룹코드

# 캐릭터 테이블
class Character(accounts.models.BaseModel):
    class CharacterType(models.IntegerChoices): #캐릭터 이미지
        MOM = 0         #엄마
        DAD = 1         #아빠
        BROTHER1 = 2    #형제1
        BROTHER2 = 3    #형제2
        BROTHER3 = 4    #형제3

    id = models.PositiveIntegerField(primary_key=True)          #id
    type = models.IntegerField(choices = CharacterType.choices) #캐릭터 이미지


# 유저 정보 테이블
class Info(accounts.models.BaseModel):
    class ActivityType(models.IntegerChoices):      #활동수준
        NOCHOICES = -1  #선택을 안 했을 때(비 당뇨인의 경우)
        DEEPLOW = 0     #활동이 적거나 운동을 안하는 경우
        LOW = 1         #가벼운 활동 및 운동
        MIDDLE = 2      #보통의 활동 및 운동
        HIGH = 3        #적극적인 활동 및 운동
        DEEPHIGH = 4    #매우 적극적인 활동 및 운동

    class GenderType(models.TextChoices):           #성별
            FEMALE = 'f'
            MALE = 'm'

    # id                                                                                            #로그인테이블 ID
    name = models.CharField(max_length=20)                                                          #이름
    character_id = models.ForeignKey(Character, on_delete=models.SET_NULL, null=True)               #캐릭터 ID
    height = models.FloatField(default=None, null=True)                                             #키
    weight = models.FloatField(default=None, null=True)                                             #몸무게
    gender = models.CharField(max_length=1, choices = GenderType.choices)                           #성별
    is_diabetes = models.BooleanField(default=False)                                                #당뇨환자여부
    activity = models.IntegerField(default=ActivityType.NOCHOICES, choices = ActivityType.choices)  #활동수준
    # account_user_group_id                                                                         #그룹코드 ID


# 식후 혈당량 테이블
class BloodSugarLevel(accounts.models.BaseModel):
    class TimelineType(models.IntegerChoices): #시간대
        MORNING = 0         #아침
        AFTERNOON = 1       #점심
        NIGHT = 2           #저녁

    # account_user_id
    # diet_id
    time = models.DateTimeField(default = None, null = True)            #혈당측정시간
    level = models.IntegerField(max_length=4, default=None, null=True)  #혈당량
    timeline = models.IntegerField(choices = TimelineType.choices)      #시간대


# 좋아요 테이블
class Like(accounts.models.BaseModel):
    class ReactionType(models.IntegerChoices): #좋아요 반응
        HEART = 0       #하트
        SMILE = 1       #웃음
        SAD = 2         #슬픔

    class TargetType(models.IntegerChoices):   #좋아요 대상 필드
        TODAYDIET = 0       #오늘의 식단 필드
        AFTERBLOOD = 1      #식후 혈당량 필드

    class TimelineType(models.IntegerChoices): #시간대
        MORNING = 0         # 아침
        AFTERNOON = 1       # 점심
        NIGHT = 2           # 저녁

    # account_user_id                                               #유저
    react = models.IntegerField(choices = ReactionType.choices)     #좋아요 반응
    target = models.IntegerField(choices = TargetType.choices)      #좋아요 대상 필드
    timeline = models.IntegerField(choices = TimelineType.choices)  #시간대


# 선호 레시피 테이블
class OurPick(accounts.models.BaseModel):
    # diet_id                                               #식단 ID
    # account_user_id                                       #유저
    pass


# 유저 알러지 테이블
class Allergy(accounts.models.BaseModel):
    # account_user_id                                       #유저
    # allergy_id                                            #알러지 ID
    pass