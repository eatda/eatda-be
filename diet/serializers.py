from rest_framework import serializers

from diet.models import DietAllergy


class DietAllergySerializer(serializers.ModelSerializer):
    class Meta:
        model = DietAllergy  # 사용할 모델
        fields = ['id', 'name']  # 사용할 모델 필드
