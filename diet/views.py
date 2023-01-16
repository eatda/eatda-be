import ast
import json

from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from diet.models import DietAllergy, Filter, FilterCategory, Data, MainSide
from diet.serializers import DietAllergySerializer, FilterSerializer, FilterCategorySerializer, DietDataSerializer


# 알러지 리스트 불러오는 api
class DietAllergyView(APIView):
    def get(self, request):
        try:
            diet_allergy = DietAllergy.objects.all()
            serializer = DietAllergySerializer(diet_allergy, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


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


class DietDataDetailView(APIView):
    def get_object(self, id):  # 오브젝트 존재 확인
        diet = get_object_or_404(Data, pk=id)
        return diet

    def is_json_key_present(self, json_data, key):  # 키 값 존재 확인
        try:
            buf = json_data[key]
        except KeyError:
            return False
        return True

    def get_ingredients(self, ingredients, recipe):  # 각 레시피 스텝에 있는 재료 구하는 함수
        recipe = ast.literal_eval(recipe)  # text to json

        for data in recipe:
            for ingredient in ingredients:
                if ingredient["name"] in data["step"]:  # 해당 step에 재료가 있다면
                    data["ingredients"].append(ingredient["name"])
        print('get', recipe)
        return recipe

    def get(self, request, id):  # 레시피 상세 get
        try:
            # 주 식단 얻기
            diet = self.get_object(id)

            if diet.recipe != '':
                diet.recipe = self.get_ingredients(diet.ingredient, diet.recipe)

            if self.is_json_key_present(diet.name, "title"):
                diet.recipe = [{"title": diet.name["title"], "process": diet.recipe}]
                diet.ingredient = [{"title": diet.name["title"], "datas": diet.ingredient}]

            diet.name = [diet.name]  #string

            if diet.tip != '':
                diet.tip = ast.literal_eval(diet.tip)  #list

            # 사이드 식단 얻기
            if MainSide.objects.filter(main_id=id).exists():
                diet_side = MainSide.objects.filter(main_id=id)
                for data in diet_side:
                    side_menu = data.side

                    if side_menu.recipe != '':
                        side_menu.recipe = self.get_ingredients(side_menu.ingredient, side_menu.recipe)
                        diet.recipe.append({"title": side_menu.name["title"], "process": side_menu.recipe})

                    diet.name.append(side_menu.name)
                    diet.ingredient.append({"title": side_menu.name["title"], "datas": side_menu.ingredient})

            serializer = DietDataSerializer(diet, context={"request": request})
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)