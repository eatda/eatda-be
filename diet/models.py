from account.models import BaseModel
from django.db import models


def articles_image_path(instance, filename):
    # MEDEIA_ROOT/user_<pk>/ 경로로 <filename> 이름으로 업로드
    return f'user_{instance.pk}/{filename}'


# 필터 카테고리 테이블
class FilterCategory(BaseModel):
    id = models.PositiveIntegerField(primary_key=True)  # id
    name = models.CharField(max_length=32)  # 필터 카테고리 이름
    query_name = models.CharField(max_length=32, default='')  # 필터 카테고리 쿼리 이름 (식단 모델 필드 이름)


# 필터 테이블
class Filter(BaseModel):
    id = models.PositiveIntegerField(primary_key=True)  # id
    name = models.CharField(max_length=32)  # 필터 이름
    image = models.ImageField(upload_to=articles_image_path, default='default.jpg')  # 필터 이미지
    image_selected = models.ImageField(upload_to=articles_image_path, default='default1.jpg')  # 필터 선택된 이미지
    category = models.ForeignKey(FilterCategory, on_delete=models.CASCADE)  # 필터 카테고리 id


# 주 식단 테이블
class Data(BaseModel):
    name = models.JSONField(default=dict)  # 음식 이름
    image = models.ImageField(upload_to=articles_image_path, default='default.jpg')  # 음식 이미지
    carbohydrate = models.FloatField(default=0)  # 탄수화물
    protein = models.FloatField(default=0)  # 단백질
    province = models.FloatField(default=0)  # 지방
    salt = models.FloatField(default=0)  # 나트륨
    total_calorie = models.FloatField(default=0)  # 총 칼로리
    ingredient = models.TextField(default='[]')  # 재료
    recipe = models.TextField(default='')  # 레시피
    tip = models.TextField(default='')  # 건강 비결
    user = models.ForeignKey('user.Info', on_delete=models.SET_NULL, null=True, default=None)  # 작성자
    type = models.ForeignKey(Filter, on_delete=models.SET_NULL, null=True,
                             related_name='%(class)s_type', default=None)  # 음식 종류
    flavor = models.ForeignKey(Filter, on_delete=models.SET_NULL, null=True,
                               related_name='%(class)s_flavor', default=None)  # 맛
    carbohydrate_type = models.ForeignKey(Filter, on_delete=models.SET_NULL,
                                          null=True, related_name='%(class)s_carbohydrate_type', default=None)  # 현미 종류
    side = models.ManyToManyField('SideData', through='MainSide', related_name='main')


# 사이드 식단 테이블
class SideData(BaseModel):
    name = models.JSONField(default=dict)  # 음식 이름
    image = models.ImageField(upload_to=articles_image_path, default='default.jpg')  # 음식 이미지
    carbohydrate = models.FloatField(default=0)  # 탄수화물
    protein = models.FloatField(default=0)  # 단백질
    province = models.FloatField(default=0)  # 지방
    salt = models.FloatField(default=0)  # 나트륨
    total_calorie = models.FloatField(default=0)  # 총 칼로리
    ingredient = models.TextField(default='[]')  # 재료
    recipe = models.TextField(default='')  # 레시피
    tip = models.TextField(default='')  # 건강 비결
    user = models.ForeignKey('user.Info', on_delete=models.SET_NULL, null=True, default=None)  # 작성자
    type = models.ForeignKey(Filter, on_delete=models.SET_NULL, null=True,
                             related_name='%(class)s_type', default=None)  # 음식 종류
    flavor = models.ForeignKey(Filter, on_delete=models.SET_NULL, null=True,
                               related_name='%(class)s_flavor', default=None)  # 맛
    carbohydrate_type = models.ForeignKey(Filter, on_delete=models.SET_NULL,
                                          null=True, related_name='%(class)s_carbohydrate_type', default=None)  # 현미 종류


# 사이드 메뉴 관계 테이블
class MainSide(BaseModel):
    main = models.ForeignKey(Data, on_delete=models.CASCADE, related_name='main_side')  # 메인 메뉴
    side = models.ForeignKey(SideData, on_delete=models.CASCADE, related_name='main_side')  # 사이드 메뉴


# 알러지 테이블
class DietAllergy(BaseModel):
    name = models.CharField(max_length=32)  # 알러지 이름
