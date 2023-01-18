from rest_framework import serializers

from diet.models import DietAllergy, Filter, FilterCategory, Data


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
    image = serializers.SerializerMethodField(read_only=True)
    image_selected = serializers.SerializerMethodField(read_only=True)

    def get_category(self, obj):
        return obj.category.id

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_image_selected(self, obj):
        request = self.context.get('request')
        if obj.image_selected:
            return request.build_absolute_uri(obj.image_selected.url)
        return None

    class Meta:
        model = Filter
        fields = ['id', 'name', 'category', 'image', 'image_selected']


class DietDataSerializer(serializers.ModelSerializer):
    menu = serializers.SerializerMethodField(read_only=True)
    recipe = serializers.JSONField(default=list)
    tip = serializers.JSONField(default=list)
    image = serializers.SerializerMethodField(read_only=True)

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_menu(self, obj):
        return obj.menu

    class Meta:
        model = Data
        fields = ['id', 'name', 'image', 'menu', 'carbohydrate', 'protein', 'province', 'salt', 'total_calorie', 'ingredient',
                  'recipe', 'tip', 'user_id', 'type_id', 'flavor_id', 'carbohydrate_type_id']


# 식단 정보 간략하게
class DietSimpleSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField(read_only=True)

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None

    class Meta:
        model = Data
        fields = ['id', 'name', 'image']
