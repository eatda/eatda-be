from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from diet.models import DietAllergy, Filter, FilterCategory
from diet.serializers import DietAllergySerializer, FilterSerializer, FilterCategorySerializer


# 알러지 리스트 불러오는 api
class DietAllergyView(APIView):
    def get(self, request):
        try:
            dietAllergy = DietAllergy.objects.all()
            serializer = DietAllergySerializer(dietAllergy, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


# 필터 리스트 불러오는 api
class FilterView(APIView):
    def get(self, request):
        # 필터 카테고리 전체 리스트 불러오기
        try:
            category_list = FilterCategory.objects.all()
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        res_data = []
        for category in category_list:
            # 카테고리 직렬화
            category_serializer = FilterCategorySerializer(category)

            # 각 카테고리별 필터 리스트 불러오기
            try:
                filter_list = Filter.objects.filter(category_id=category.id)
                print(filter_list)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            filter_serializer = FilterSerializer(filter_list, many=True, context={"request": request})

            data = {
                "category": category_serializer.data,
                "filter": filter_serializer.data
            }
            res_data.append(data)
        return Response(res_data, status=status.HTTP_200_OK)
