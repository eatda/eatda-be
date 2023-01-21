import ast

from django.http import JsonResponse

# Create your views here.
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from diet.models import DietAllergy, Filter, FilterCategory, Data, MainSide
from diet.serializers import DietAllergySerializer, FilterSerializer, FilterCategorySerializer, DietDataSerializer, \
    DietSimpleSerializer


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


# 식단 상세 정보 가져오는 API
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

    def get_menu(self, menu, name):  # 메인메뉴 및 사이드 메뉴 리스트 가져오는 함수
        menu.append(name['title'])

        return menu

    def get_ingredients(self, ingredients, recipe):  # 각 레시피 스텝에 있는 재료 구하는 함수
        recipe = ast.literal_eval(recipe)  # text to json

        for data in recipe:
            for ingredient in ingredients:
                if ingredient["name"] in data["step"]:  # 해당 step에 재료가 있다면
                    data["ingredients"].append(ingredient["name"])
        return recipe

    def get(self, request, id):  # 레시피 상세 get
        try:
            # 주 식단 얻기
            diet = self.get_object(id)
            diet.ingredient = ast.literal_eval(diet.ingredient)
            menu_list = []  # 식단 메뉴들 리스트
            menu_list = self.get_menu(menu_list, diet.name)

            if diet.recipe != '':
                diet.recipe = self.get_ingredients(diet.ingredient, diet.recipe)

            if self.is_json_key_present(diet.name, "title"):
                diet.recipe = [{"title": diet.name["title"], "process": diet.recipe}]
                diet.ingredient = [{"title": diet.name["title"], "data": diet.ingredient}]

            if diet.tip != '':
                diet.tip = ast.literal_eval(diet.tip)  # list

            # 사이드 식단 얻기
            if MainSide.objects.filter(main_id=id).exists():
                diet_side = MainSide.objects.filter(main_id=id)
                for data in diet_side:
                    side_menu = data.side
                    side_menu.ingredient = ast.literal_eval(side_menu.ingredient)

                    # 사이드 메뉴의 레시피가 있는 경우 추가
                    if side_menu.recipe != '':
                        side_menu.recipe = self.get_ingredients(side_menu.ingredient, side_menu.recipe)
                        diet.recipe.append({"title": side_menu.name["title"], "process": side_menu.recipe})

                    # 전체 음식의 탄단지 및 칼로리 양 구하기
                    diet.carbohydrate += side_menu.carbohydrate
                    diet.protein += side_menu.protein
                    diet.province += side_menu.province
                    diet.salt += side_menu.salt
                    diet.total_calorie += side_menu.total_calorie

                    # ingredient가 비어있으면 title만 보내고, 아니라면 재료도 같이 보내기
                    if len(side_menu.ingredient) != 0:
                        diet.ingredient.append({"title": side_menu.name["title"], "data": side_menu.ingredient})
                        menu_list = self.get_menu(menu_list, side_menu.name)
                    else:
                        menu_list = self.get_menu(menu_list, side_menu.name)

            diet.menu = menu_list
            serializer = DietDataSerializer(diet, context={"request": request})
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# 식단 전체 리스트 가져오는 API
class DietDataView(APIView):
    def get(self, request):
        try:  # 식단 전체 리스트
            all_diet_list = Data.objects.all()
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = DietSimpleSerializer(all_diet_list, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
