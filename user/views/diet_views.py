from collections import Counter
from datetime import datetime, timedelta

from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from account.views import AuthView
from diet.models import Data
from diet.serializers import DietSimpleSerializer
from user.models import Info, BloodSugarLevel, OurPick
from user.serializers import DietSerializer, OurPickSerializer, BloodDietSerializer


# 오늘의 식단 등록 api
class UserDietView(APIView):
    def get(self, request):
        # 인가확인
        if AuthView.get(self, request).status_code is not status.HTTP_200_OK:
            return Response({"error": "로그인 필요"}, status=status.HTTP_401_UNAUTHORIZED)

        # 접속한 유저 정보 가져오기
        user_id = AuthView.get(self, request).data['user_id']
        user = get_object_or_404(Info, user_id=user_id)

        # 같은 그룹 내의 식후 혈당량 없는 오늘의 식단 가져오기
        try:
            diet_list = BloodSugarLevel.objects.filter(user_id__group=user.group_id, level=None).order_by('created_at')
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        serializer = DietSerializer(diet_list, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # 인가확인
        if AuthView.get(self, request).status_code is not status.HTTP_200_OK:
            return Response({"error": "로그인 필요"}, status=status.HTTP_401_UNAUTHORIZED)

        # 접속한 유저 정보 가져오기
        user_id = AuthView.get(self, request).data['user_id']
        user = get_object_or_404(Info, user_id=user_id)

        # 오늘의 식단 등록 전 데이터 유효성 검사
        request.data["user_id"] = user.user_id
        serializer = DietSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 식단 존재 확인
        get_object_or_404(Data, id=request.data["diet_id"])

        # 현재 날짜 가져오기
        date = datetime.now().date()

        # 이미 등록한 시간대인지 확인
        timeline = request.data["timeline"]
        if BloodSugarLevel.objects.filter(user_id__group=user.group_id,
                                          created_at__contains=date, timeline=timeline).exists():
            return Response({"error": "이미 해당 시간대에 등록된 식단이 있습니다."}, status=status.HTTP_403_FORBIDDEN)

        serializer.save()
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request):
        # 인가확인
        if AuthView.get(self, request).status_code is not status.HTTP_200_OK:
            return Response({"error": "로그인 필요"}, status=status.HTTP_401_UNAUTHORIZED)

        # 접속한 유저 정보 가져오기
        user_id = AuthView.get(self, request).data['user_id']
        user = get_object_or_404(Info, user_id=user_id)

        # 오늘의 식단 삭제 전 데이터 유효성 검사
        diet_id = request.data.get("diet_id")
        timeline = request.data.get("timeline")

        # 현재 날짜 가져오기
        date = datetime.now().date()

        try:
            data = BloodSugarLevel.objects.get(user_id__group=user.group_id, created_at__contains=date,
                                               timeline=timeline, diet_id=diet_id)
            data.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# 유저가 선택한 Our-Pick 관련 api
class OurPickView(APIView):
    def get_like_character(self, like_list):
        who_liked = []
        for like in like_list:
            who_liked.append(like.character)
        return who_liked

    def post(self, request):
        # 인가확인
        if AuthView.get(self, request).status_code is not status.HTTP_200_OK:
            return Response({"error": "로그인 필요"}, status=status.HTTP_401_UNAUTHORIZED)

        # 접속한 유저 정보 가져오기
        user_id = AuthView.get(self, request).data['user_id']
        user = get_object_or_404(Info, user_id=user_id)

        # ourpick 저장 전 데이터 유효성 검사
        request.data["user_id"] = user.user_id
        serializer = OurPickSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 식단 존재 확인
        get_object_or_404(Data, id=request.data["diet_id"])

        if OurPick.objects.filter(user_id=user.user_id, diet_id=request.data['diet_id']).exists():
            return Response({"error": "이미 좋아요한 식단입니다."}, status=status.HTTP_403_FORBIDDEN)

        serializer.save(serializer.data)
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request):
        # 인가확인
        if AuthView.get(self, request).status_code is not status.HTTP_200_OK:
            return Response({"error": "로그인 필요"}, status=status.HTTP_401_UNAUTHORIZED)

        # 접속한 유저 정보 가져오기
        user_id = AuthView.get(self, request).data['user_id']
        user = get_object_or_404(Info, user_id=user_id)

        try:
            # 식단 존재 확인
            get_object_or_404(Data, id=request.data["diet_id"])

            # ourpick model에서 선택 삭제
            ourpick = OurPick.objects.get(user_id=user_id, diet_id=request.data['diet_id'])
            ourpick.delete()

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def get(self, request):

        # 인가확인
        if AuthView.get(self, request).status_code is not status.HTTP_200_OK:
            return Response({"error": "로그인 필요"}, status=status.HTTP_401_UNAUTHORIZED)

        # 접속한 유저 정보 가져오기
        user_id = AuthView.get(self, request).data['user_id']
        user = get_object_or_404(Info, user_id=user_id)

        # ourpick 리스트 가져오기 (해당 그룹에 대한)
        try:
            ourpick_list = OurPick.objects.filter(user_id__group=user.group_id)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # 같은 그룹이 2명 이상 좋아요한 리스트 및 각자들이 좋아한 리스트 불러오기
        popular_diet_id_list = []  # 그룹이 좋아요한 diet_id 리스트
        for pick in ourpick_list:
            popular_serializer = OurPickSerializer(pick)
            popular_diet_id_list.append(popular_serializer.data['diet_id'])
        popular_cnt_list = dict(Counter(popular_diet_id_list))
        print(popular_cnt_list)
        total_popular = []  # 최종적으로 2개 이상 선택된 diet_id 리스트

        # 내림차순 순으로 2개 이상 선택된 diet_list 저장하기
        for key in sorted(popular_cnt_list.keys(), reverse=True):
            if popular_cnt_list[key] >= 2:
                total_popular.append(key)

        popular_pick = []  # 가족들의 인기 픽 리스트
        for diet_id in total_popular:
            # 식단 존재 확인
            get_object_or_404(Data, id=diet_id)

            diet_detail = Data.objects.get(id=diet_id)
            diet_simple = DietSimpleSerializer(diet_detail, context={'request': request})

            try:
                is_me_liked = True if ourpick_list.get(user_id=user_id, diet_id=diet_id) else False
            except:
                is_me_liked = False

            popular_user = ourpick_list.filter(diet_id=diet_id)

            liked_user = []
            for pUser in popular_user:
                liked_user.append(pUser.user)

            who_liked = self.get_like_character(liked_user)
            who_liked.sort()

            popular_data = {
                'diet': diet_simple.data,
                'is_me_liked': is_me_liked,
                'who_liked': who_liked
            }

            popular_pick.append(popular_data)

        # 각자 좋아요한 리스트
        # 그룹에서 속해있는 유저들 가져오기
        indivisual_list = []  # 같은 그룹에서 각자 좋아하는거 저장하는 리스트
        group_users = Info.objects.filter(group=user.group_id)

        for gUser in group_users:
            diet_list = []  # 각자마다 식단을 저장하는 배열
            for pick in ourpick_list:
                if pick.user_id == gUser.user.id:
                    print(user_id)
                    diet_detail = Data.objects.get(id=pick.diet_id)
                    diet_simple = DietSimpleSerializer(diet_detail, context={'request': request})

                    try:
                        is_me_liked = True if ourpick_list.get(user_id=user_id,
                                                               diet_id=pick.diet_id) else False  # 만약 내가 좋아한 식단이면 True
                    except:
                        is_me_liked = False  # 아니면 False
                    print(is_me_liked)

                    diet_data = {
                        'diet': diet_simple.data,
                        'is_me_liked': is_me_liked
                    }

                    diet_list.append(diet_data)
            is_exist = True if len(diet_list) != 0 else False

            res_data = {
                'user_name': gUser.name,
                'is_exist': is_exist,
                'data': diet_list
            }
            indivisual_list.append(res_data)

        res_data = {
            'popular_pick': popular_pick,
            'indivisual_list': indivisual_list
        }
        return Response(res_data, status=status.HTTP_200_OK)


# best & worst top 3 식단 api
class DietRankView(APIView):
    def get(self, request):
        # 인가확인
        if AuthView.get(self, request).status_code is not status.HTTP_200_OK:
            return Response({"error": "로그인 필요"}, status=status.HTTP_401_UNAUTHORIZED)

        # 접속한 유저 정보 가져오기
        user_id = AuthView.get(self, request).data['user_id']
        user = get_object_or_404(Info, user_id=user_id)

        best, worst = [], []

        # 현재 날짜 가져오기
        end_date = datetime.now().date()  # 현재 날짜
        start_date = end_date - timedelta(days=6)  # 일주일 전 날짜

        # 해당 유저의 식후 혈당량 가져오기
        try:
            high_blood_list = BloodSugarLevel.objects.filter(user_id__group=user.group_id, level__isnull=False,
                                                             created_at__date__range=[start_date, end_date]).values('diet_id').annotate(avg_level=Avg('level')).order_by(
                '-avg_level')[:3]
            low_blood_list = BloodSugarLevel.objects.filter(user_id__group=user.group_id, level__isnull=False,
                                                            created_at__date__range=[start_date, end_date]).values('diet_id').annotate(avg_level=Avg('level')).order_by(
                'avg_level')[:3]
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # best top 3
        for diet in low_blood_list:
            try:
                diet_id = diet['diet_id']
                diet_data = Data.objects.get(id=diet_id)
                diet_serializer = DietSimpleSerializer(diet_data, context={"request": request})
                best.append(diet_serializer.data)

            except Exception as e:
                return Response('아직 best&worst 식단이 없습니다.', status=status.HTTP_404_NOT_FOUND)

        # worst top 3
        for diet in high_blood_list:
            try:
                diet_id = diet['diet_id']
                diet_data = Data.objects.get(id=diet_id)
                diet_serializer = DietSimpleSerializer(diet_data, context={"request": request})
                worst.append(diet_serializer.data)

            except Exception as e:
                return Response('아직 best&worst 식단이 없습니다.', status=status.HTTP_404_NOT_FOUND)

        res_data = {
            'best': best,
            'worst': worst
        }

        return Response(res_data, status=status.HTTP_200_OK)


# 유저 맞춤형 식단 추천 API
class DietFitView(APIView):
    def get(self, request):
        # 인가확인
        if AuthView.get(self, request).status_code is not status.HTTP_200_OK:
            return Response({"error": "로그인 필요"}, status=status.HTTP_401_UNAUTHORIZED)

        # 접속한 유저 정보 가져오기
        user_id = AuthView.get(self, request).data['user_id']
        user = get_object_or_404(Info, user_id=user_id)

        # 현재 날짜 가져오기
        end_date = datetime.now().date()  # 현재 날짜
        start_date = end_date - timedelta(days=6)  # 일주일 전 날짜

        # 일주일 이내 식단 별 식후 혈당량 오름차순 정렬해서 가져오기
        try:
            blood_list = BloodSugarLevel.objects.filter(user_id__group=user.group_id, level__isnull=False,
                                                        created_at__date__range=[start_date, end_date]).values(
                'diet').annotate(avg_level=Avg('level')).order_by(
                'avg_level')
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if blood_list.count() < 3:
            return Response({"error": "아직 나에게 딱 맞는 레시피가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        diet_list = []
        for data in blood_list[:2]:
            diet_list.append(Data.objects.get(id=data["diet"]))

        res_data = []
        serializer = DietSimpleSerializer(diet_list, many=True, context={"request": request})
        for data in serializer.data:
            data["is_me_liked"] = True if OurPick.objects.filter(user_id=user_id, diet_id=
            data["id"]).exists() else False
            res_data.append(data)
        return Response(res_data, status=status.HTTP_200_OK)
