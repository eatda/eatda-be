from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from diet.models import DietAllergy
from diet.serializers import DietAllergySerializer


# 알러지 리스트 불러오는 api
class DietAllergyList(APIView):
    def get(self, request):

        try:
            diet_allergy = DietAllergy.objects.all()
            serializer = DietAllergySerializer(diet_allergy, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
