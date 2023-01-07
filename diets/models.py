import accounts.models
from django.db import models


# 필터 카테고리 테이블
class FilterCategory(accounts.models.BaseModel):
    id = models.PositiveIntegerField(primary_key=True)  # id
    name = models.CharField(max_length=32)  # 필터 카테고리 이름


# 필터 테이블
class Filter(accounts.models.BaseModel):
    id = models.PositiveIntegerField(primary_key=True)  # id
    name = models.CharField(max_length=32)  # 필터 이름
    filter_category = models.ForeignKey(FilterCategory, on_delete=models.CASCADE)  # 필터 카테고리 id


# 식단 테이블
class Data(accounts.models.BaseModel):
    name = models.JSONField(default=dict)  # 음식 이름
    image = models.ImageField(upload_to='images/')  # 음식 이미지
    carbohydrate = models.IntegerField(default=0)  # 탄수화물
    protein = models.IntegerField(default=0)  # 단백질
    province = models.IntegerField(default=0)  # 지방
    salt = models.IntegerField(default=0)  # 나트륨
    total_calorie = models.IntegerField(default=0)  # 총 칼로리
    ingredient = models.JSONField(default=list)  # 재료
    recipe = models.TextField(default='')  # 레시피
    tip = models.TextField(default='')  # 건강 비결
    # 작성자
    type = models.ForeignKey(Filter, on_delete=models.SET_NULL, null=True, related_name='type')  # 음식 종류
    flavor = models.ForeignKey(Filter, on_delete=models.SET_NULL, null=True, related_name='flavor')  # 맛
    carbohydrate_type = models.ForeignKey(Filter, on_delete=models.SET_NULL,
                                          null=True, related_name='carbohydrate_type')  # 현미 종류


# 알러지 테이블
class Allergy(models.Model):
    id = models.PositiveIntegerField(primary_key=True)  # id
    name = models.CharField(max_length=32)  # 알러지 이름
