from rest_framework import serializers

from diet.models import DietAllergy, Filter, FilterCategory, Data
from django_svg_image_form_field import SvgAndImageFormField


class DietAllergySerializer(serializers.ModelSerializer):
    class Meta:
        model = DietAllergy  # 사용할 모델
        fields = ['id', 'name']  # 사용할 모델 필드


class FilterCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FilterCategory
        fields = ['id', 'name', 'query_name']


class FilterSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField(read_only=True)

    def get_category(self, obj):
        return obj.category.id

    class Meta:
        model = Filter
        fields = ['id', 'name', 'category', 'image', 'image_selected']
        field_classes = {
            'image': SvgAndImageFormField,
            'image_selected': SvgAndImageFormField,
        }


class DietDataSerializer(serializers.ModelSerializer):
    menu = serializers.SerializerMethodField(read_only=True)
    ingredient = serializers.JSONField(default=list)
    recipe = serializers.JSONField(default=list)
    tip = serializers.JSONField(default=list)

    def get_menu(self, obj):
        return obj.menu

    class Meta:
        model = Data
        fields = ['id', 'name', 'image', 'menu', 'carbohydrate', 'protein', 'province', 'salt', 'total_calorie', 'ingredient',
                  'recipe', 'tip', 'user_id', 'type_id', 'flavor_id', 'carbohydrate_type_id']
        field_classes = {
            'image': SvgAndImageFormField,
        }


# 식단 정보 간략하게
class DietSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Data
        fields = ['id', 'name', 'image']
        field_classes = {
            'image': SvgAndImageFormField,
        }
