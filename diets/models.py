from accounts.models import BaseModel
from users.models import Info
from django.db import models


# 필터 카테고리 테이블
class FilterCategory(BaseModel):
    id = models.PositiveIntegerField(primary_key=True)  # id
    name = models.CharField(max_length=32)  # 필터 카테고리 이름


# 필터 테이블
class Filter(BaseModel):
    id = models.PositiveIntegerField(primary_key=True)  # id
    name = models.CharField(max_length=32)  # 필터 이름
    filter_category = models.ForeignKey(FilterCategory, on_delete=models.CASCADE)  # 필터 카테고리 id


# 주 식단 테이블
class Data(BaseModel):
    name = models.JSONField(default=dict)  # 음식 이름
    image = models.ImageField(upload_to='images/', default='default.jpg')  # 음식 이미지
    carbohydrate = models.IntegerField(default=0)  # 탄수화물
    protein = models.IntegerField(default=0)  # 단백질
    province = models.IntegerField(default=0)  # 지방
    salt = models.IntegerField(default=0)  # 나트륨
    total_calorie = models.IntegerField(default=0)  # 총 칼로리
    ingredient = models.JSONField(default=list)  # 재료
    recipe = models.TextField(default='')  # 레시피
    tip = models.TextField(default='')  # 건강 비결
    user = models.ForeignKey(Info, on_delete=models.SET_NULL, null=True, default=None)  # 작성자
    type = models.ForeignKey(Filter, on_delete=models.SET_NULL, null=True, related_name='type', default=None)  # 음식 종류
    flavor = models.ForeignKey(Filter, on_delete=models.SET_NULL, null=True, related_name='flavor', default=None)  # 맛
    carbohydrate_type = models.ForeignKey(Filter, on_delete=models.SET_NULL,
                                          null=True, related_name='carbohydrate_type', default=None)  # 현미 종류


# 사이드 식단 테이블
class SideData(BaseModel):
    name = models.JSONField(default=dict)  # 음식 이름
    image = models.ImageField(upload_to='images/', default='default.jpg')  # 음식 이미지
    carbohydrate = models.IntegerField(default=0)  # 탄수화물
    protein = models.IntegerField(default=0)  # 단백질
    province = models.IntegerField(default=0)  # 지방
    salt = models.IntegerField(default=0)  # 나트륨
    total_calorie = models.IntegerField(default=0)  # 총 칼로리
    ingredient = models.JSONField(default=list)  # 재료
    recipe = models.TextField(default='')  # 레시피
    tip = models.TextField(default='')  # 건강 비결
    user = models.ForeignKey(Info, on_delete=models.SET_NULL, null=True, default=None)  # 작성자
    type = models.ForeignKey(Filter, on_delete=models.SET_NULL, null=True, related_name='type', default=None)  # 음식 종류
    flavor = models.ForeignKey(Filter, on_delete=models.SET_NULL, null=True, related_name='flavor', default=None)  # 맛
    carbohydrate_type = models.ForeignKey(Filter, on_delete=models.SET_NULL,
                                          null=True, related_name='carbohydrate_type', default=None)  # 현미 종류


# 사이드 메뉴 관계 테이블
class MainSide(BaseModel):
    main = models.ForeignKey(Data, on_delete=models.CASCADE, related_name='main')  # 메인 메뉴
    side = models.ForeignKey(SideData, on_delete=models.CASCADE, related_name='side')  # 사이드 메뉴


# 알러지 테이블
class Allergy(BaseModel):
    id = models.PositiveIntegerField(primary_key=True)  # id
    name = models.CharField(max_length=32)  # 알러지 이름
