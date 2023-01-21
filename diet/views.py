import ast

from django.db.models import Sum, F, Q
from django.http import JsonResponse

# Create your views here.
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from account.views import AuthView
from user.models import Info
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
    def get_query_array(self, query):  # 쿼리 스트링 array로 변환
        return [int(x) for x in query.split(',')]
    
    def get_min_max_kcal(self, amr):  # 활동대사량에 따른 칼로리 범위
        if amr is None:
            return 0, 2000
        elif amr >= 2400:
            return 600, 2000
        elif amr >= 2100:
            return 500, 700
        elif amr >= 1800:
            return 400, 600
        return 0, 500

    def get_filter_ingredient(self, query_list):  # 재료에서 필터링하는 필터 만들어주는 함수
        filter_names = Filter.objects.filter(id__in=query_list).values_list('name')  # 필터 name 얻어오기
        temp_q = Q()
        for x in filter_names:
            temp_q |= (Q(ingredient__icontains=x[0]) | Q(side__ingredient__icontains=x[0]))
        return temp_q

    def get(self, request):
        # 인가확인
        if AuthView.get(self, request).status_code is not status.HTTP_200_OK:
            return Response({"error": "로그인 필요"}, status=status.HTTP_401_UNAUTHORIZED)

        # 접속한 유저 정보 가져오기
        user_id = AuthView.get(self, request).data['user_id']
        user = get_object_or_404(Info, user_id=user_id)

        # 그룹의 당뇨인의 amr 가져오기
        amr = None
        if Info.objects.filter(group=user.group_id, is_diabetes=True).exists():
            amr = Info.objects.get(group=user.group_id, is_diabetes=True).amr

        # 유저 활동 대사량에 따른 칼로리 범위 구하기
        start, end = self.get_min_max_kcal(amr)

        # 활동 대사량에 맞춘 식단 필터링
        try:
            data = Data.objects. \
                annotate(side_total_calorie=Sum('side__total_calorie')). \
                annotate(total=F('total_calorie') + F('side_total_calorie')). \
                filter(total__isnull=False, total__gte=start, total__lte=end)  # 사이드 메뉴 있는 식단 필터링
            data2 = Data.objects. \
                annotate(side_total_calorie=Sum('side__total_calorie')). \
                annotate(total=F('total_calorie') + F('side_total_calorie')). \
                filter(total__isnull=True, total_calorie__gte=start, total_calorie__lte=end)  # 주메뉴만 있는 식단 필터링
            feat_diet = data | data2
            # feat_diet = data.union(data2)  # 필드 에러 걱정 없이 합칠 수 있지만, union으로 합치면 filter가 안됨
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # 쿼리스트링에서 필터 값 가져오기
        type = request.GET.get('type', None)  # 음식 종류
        flavor = request.GET.get('flavor', None)  # 맛
        carbohydrate_type = request.GET.get('carbohydrate_type', None)  # 탄수화물 종류
        meat = request.GET.get('meat', None)  # 고기
        vegetable = request.GET.get('vegetable', None)  # 채소

        # feat_diet = Data.objects.all()
        # 필터 만들기
        q = Q()
        # q &= Q(id__in=feat_diet.values('id'))  # union으로 합쳤을 때 쓸 수 있는 코드. 다시 filter 걸기
        if type:  # 음식 종류
            q &= Q(type_id__in=self.get_query_array(type))
        if flavor:  # 맛
            q &= Q(flavor_id__in=self.get_query_array(flavor))
        if carbohydrate_type:  # 탄수화물 종류
            query_list = self.get_query_array(carbohydrate_type)
            q &= self.get_filter_ingredient(query_list)
        if meat:  # 고기
            query_list = self.get_query_array(meat)
            q &= self.get_filter_ingredient(query_list)
        if vegetable:  # 채소
            query_list = self.get_query_array(vegetable)
            q &= self.get_filter_ingredient(query_list)

        feat_diet = feat_diet.filter(q).distinct()
        serializer = DietSimpleSerializer(feat_diet, many=True, context={"request": request})
        return Response({"개수": len(feat_diet), "data":serializer.data}, status=status.HTTP_200_OK)
