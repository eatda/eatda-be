# 그룹 코드 생성 시 필요한 라이브러리
import base64
import codecs
import uuid
from collections import Counter

from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import status, exceptions
from rest_framework.response import Response
from rest_framework.views import APIView

from account.views import AuthView
from diet.models import Data
from diet.serializers import DietSimpleSerializer
from user.models import Character, Info, Group, UserAllergy, BloodSugarLevel, Like, OurPick
from user.serializers import CharacterSerializer, GroupSerializer, InfoSerializer, UserAllergySerializer, \
    BloodSerializer, DietSerializer, OurPickSerializer, BloodDietSerializer, HomeLikeSerializer

from datetime import datetime, timedelta


# 유저 정보 가져오는 api
class UserInfoDetailView(APIView):
    def get(self, request):
        # 인가확인
        if AuthView.get(self, request).status_code is status.HTTP_200_OK:
            # 접속한 유저 정보 가져오기
            login_user = AuthView.get(self, request).data
            login_user_detail = Info.objects.get(user_id=login_user['user_id'])

            if login_user_detail is not None:
                try:
                    allergy_list = UserAllergy.objects.filter(user_id=login_user['user_id'])

                    info_serializer = InfoSerializer(login_user_detail, context={'request': request})
                    allergy_serializer = UserAllergySerializer(allergy_list, many=True, context={"request": request})

                    # 유저 알러지 리스트 가져오기
                    allergy_filter = []
                    for allergy in allergy_serializer.data:
                        data = {
                            'id': allergy['allergy_id'],
                            'name': allergy['allergy_name']
                        }
                        allergy_filter.append(data)

                    data = {
                        'name': info_serializer.data['name'],
                        'character': info_serializer.data['character'],
                        'height': info_serializer.data['height'],
                        'weight': info_serializer.data['weight'],
                        'gender': info_serializer.data['gender'],
                        'age': info_serializer.data['age'],
                        'activity': info_serializer.data['activity'],
                        'is_diabetes': info_serializer.data['is_diabetes'],
                        'group': info_serializer.data['group_code'],
                        'allergy': allergy_filter
                    }

                    return Response(data, status=status.HTTP_200_OK)

                except Exception as e:
                    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        elif AuthView.get(self, request).status_code is status.HTTP_400_BAD_REQUEST:
            raise exceptions.ValidationError(detail='Please login for getting user info')

        elif AuthView.get(self, request).status_code is status.HTTP_401_UNAUTHORIZED:
            raise exceptions.ValidationError(detail='token is expired')

        elif AuthView.get(self, request).status_code is status.HTTP_403_FORBIDDEN:
            raise exceptions.ValidationError(detail='Please login again')


# 유저 캐릭터 리스트 가져오는 api
class UserCharacterView(APIView):
    def get(self, request):
        try:
            # 그룹 내 유저들의 캐릭터 ID 받아오기
            group = request.GET.get('group')
            if Group.objects.filter(code=group).exists() is False:
                return Response({"error": "올바른 그룹 코드를 적어주세요."}, status=status.HTTP_400_BAD_REQUEST)
            group_list = Info.objects.filter(group__code=group).values()  # 해당하는 그룹 code의 유저들 get
            selected_character = list()

            for users in group_list:
                selected_character.append(users['character'])
            selected_character.sort()

            # 전체 등록된 캐릭터 리스트 가져오기
            all_character_list = [character[0] for character in Info.character.field.choices]

            # 선택된 캐릭터 제외하기
            for select in selected_character:
                all_character_list.remove(select)

            res_data = []

            for character_id in all_character_list:
                res_data.append({'id': character_id})

            return Response(res_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# 그룹 코드 api
class UserGroupView(APIView):
    def generate_random_slug_code(self, length=6):
        return base64.urlsafe_b64encode(
            codecs.encode(uuid.uuid4().bytes, "base64").rstrip()
        ).decode()[:length].upper()

    # 그룹 코드 생성
    def get(self, request):
        try:
            code = self.generate_random_slug_code()
            serializer = GroupSerializer(data={"code": code})
            if serializer.is_valid():  # 유효한 그룹코드 생성했다면
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # 그룹 코드 검증
    def post(self, request):
        id = request.data["id"]
        code = request.data["code"]

        # 그룹 코드 조회
        try:
            data = Group.objects.get(id=id)
        except Exception as e:
            return Response({"error": "존재하지 않는 그룹입니다."}, status=status.HTTP_404_NOT_FOUND)

        if data.code != code:
            return Response({"error": "존재하지 않는 그룹입니다."}, status=status.HTTP_404_NOT_FOUND)

        # 그룹 인원 수 조회
        try:
            group_users = Info.objects.filter(group_id=id)
        except Exception as e:
            return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)

        # 그룹 인원 수 확인 (이미 5명이라면)
        if group_users.count() == 5:
            return Response({"error": "이미 인원이 모두 찬 그룹입니다."}, status=status.HTTP_403_FORBIDDEN)

        # 당뇨인 조회
        is_diabetes = True if group_users.filter(is_diabetes=True).count() == 1 else False
        return Response({"is_diabetes": is_diabetes}, status=status.HTTP_200_OK)


# 홈 화면 api
class UserHomeView(APIView):
    def get_like_character(self, like_list):
        who_liked = []
        for like in like_list:
            who_liked.append(like.user.character)
        return who_liked

    def get(self, request):
        # 인가확인
        if AuthView.get(self, request).status_code is not status.HTTP_200_OK:
            return Response({"error": "로그인 필요"}, status=status.HTTP_401_UNAUTHORIZED)

        # 접속한 유저 정보 가져오기
        user_id = AuthView.get(self, request).data['user_id']
        user = get_object_or_404(Info, user_id=user_id)

        # 현재 날짜 가져오기
        date = datetime.now().date()

        # 오늘의 식단 & 혈당량 & 좋아요 정보 리스트로 가져오기 (해당 그룹에 대한)
        try:
            diet_blood_list = BloodSugarLevel.objects.filter(user_id__group=user.group_id, created_at__contains=date)
            like_list = Like.objects.filter(user_id__group=user.group_id, created_at__contains=date)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # 아침, 점심, 저녁 마다 식단 & 혈당량 & 좋아요 정보 얻어오기
        diet = [{}, {}, {}]
        blood_sugar_level = [{}, {}, {}]
        for timeline in [timeline[0] for timeline in BloodSugarLevel.timeline.field.choices]:
            try:
                blood_detail = diet_blood_list.get(timeline=timeline)  # 식후 혈당량
                diet_detail = blood_detail.diet  # 식단
                try:
                    diet_like = like_list.filter(target=0, timeline=timeline)  # 식단 좋아요
                except:
                    diet_like = []
                try:
                    blood_like = like_list.filter(target=1, timeline=timeline)  # 식후 혈당량 좋아요
                except:
                    blood_like = []

                try:
                    serializer = DietSimpleSerializer(diet_detail, context={'request': request})
                except Exception as e:
                    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
                diet[timeline]["is_exist"] = True
                diet[timeline]["data"] = serializer.data
                diet[timeline]["data"]["timeline"] = timeline
                try:
                    diet[timeline]["is_me_liked"] = True if diet_like.get(user_id=user.user_id) else False
                except:
                    diet[timeline]["is_me_liked"] = False
                try:
                    diet[timeline]["who_liked"] = self.get_like_character(diet_like)
                except Exception as e:
                    return Response(str(e))

                if blood_detail.time is None:  # 식후 혈당량 없다면
                    blood_sugar_level[timeline]["is_exist"] = False
                else:  # 식후 혈당량 입력 되어있다면
                    blood_sugar_level[timeline]["is_exist"] = True
                    serializer = BloodSerializer(blood_detail)
                    blood_sugar_level[timeline]["data"] = serializer.data
                    try:
                        blood_sugar_level[timeline]["is_me_liked"] = True if blood_like.get(
                            user_id=user.user_id) else False
                    except:
                        blood_sugar_level[timeline]["is_me_liked"] = False
                    blood_sugar_level[timeline]["who_liked"] = self.get_like_character(blood_like)
            except:
                diet[timeline]["is_exist"] = blood_sugar_level[timeline]["is_exist"] = False

        res_data = {
            "diet": diet,
            "blood_sugar_level": blood_sugar_level
        }
        return Response(res_data, status=status.HTTP_200_OK)


# 홈화면에서 좋아요 눌렀을 때 api
class HomeLikeView(APIView):
    def post(self, request):
        # 인가확인
        if AuthView.get(self, request).status_code is not status.HTTP_200_OK:
            return Response({"error": "로그인 필요"}, status=status.HTTP_401_UNAUTHORIZED)

        # 접속한 유저 정보 가져오기
        user_id = AuthView.get(self, request).data['user_id']
        user = get_object_or_404(Info, user_id=user_id)

        try:
            react = request.data["react"]
        except:
            react = Like.ReactionType.HEART

        target = request.data["target"]
        timeline = request.data["timeline"]

        serializer = HomeLikeSerializer(data={
            "user_id": user_id,
            "react": react,
            "target": target,
            "timeline": timeline
        })

        serializer.is_valid(raise_exception=True)
        date = datetime.now().date()

        # 이미 좋아요한 유저, 반응, 타겟 및 시간대인지 확인
        if Like.objects.filter(user_id__user=user_id, react=react, target=target,
                               timeline=timeline, created_at__date=date).exists():
            return Response({"error": "이미 해당 시간대에 반응을 표시한 식단입니다."}, status=status.HTTP_403_FORBIDDEN)

        print(serializer.data)
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
            try:
                react = request.data["react"]
            except:
                react = Like.ReactionType.HEART

            target = request.data["target"]
            timeline = request.data["timeline"]
            date = datetime.now().date()

            # 반응 존재 확인
            if Like.objects.filter(user_id__user=user_id, react=react, target=target,
                                   timeline=timeline, created_at__date=date).exists() is False:
                return Response({"error": "반응한 요소가 없습니다"}, status=status.HTTP_403_FORBIDDEN)

            # 좋아요 필드에서 선택 삭제
            like = Like.objects.get(user_id__user=user_id, react=react, target=target,
                                    timeline=timeline, created_at__date=date)
            like.delete()

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)


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


# 식후 혈당량 api
class BloodSugarLevelView(APIView):
    def get(self, request):
        # 인가확인
        if AuthView.get(self, request).status_code is not status.HTTP_200_OK:
            return Response({"error": "로그인 필요"}, status=status.HTTP_401_UNAUTHORIZED)

        # 접속한 유저 정보 가져오기
        user_id = AuthView.get(self, request).data['user_id']
        user = get_object_or_404(Info, user_id=user_id)

        # 같은 그룹 내의 식후 혈당량 가져오기
        try:
            blood_list = BloodSugarLevel.objects.filter(user_id__group=user.group_id, level__isnull=False).order_by(
                '-created_at')
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        serializer = BloodDietSerializer(blood_list, many=True, context={"request": request})

        # 날짜별로 데이터 묶기
        res_data = []
        prev_date = ''  # 현재 탐색 날짜
        data = []  # 식후 혈당량 리스트
        for blood in serializer.data:
            if blood["date"] == prev_date:
                data.insert(0, blood)
            else:
                if prev_date is not '':
                    res_data.append({"date": prev_date[3:8], "data": data})
                data = [blood]
                prev_date = blood["date"]
        res_data.append({"date": prev_date[3:8], "data": data})  # 마지막 날짜 데이터
        return Response(res_data, status=status.HTTP_200_OK)

    def post(self, request):
        # 인가확인
        if AuthView.get(self, request).status_code is not status.HTTP_200_OK:
            return Response({"error": "로그인 필요"}, status=status.HTTP_401_UNAUTHORIZED)

        # 접속한 유저 정보 가져오기
        user_id = AuthView.get(self, request).data['user_id']
        user = get_object_or_404(Info, user_id=user_id)

        # 당뇨인이 아니라면 등록 거부
        if user.is_diabetes is False:
            return Response({"error": "당뇨인 본인만 혈당을 입력할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN)

        # request body 데이터 유효성 검사
        serializer = BloodSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 그룹 내 오늘의 식단 정보 맞는지 검사
        try:
            diet_data = BloodSugarLevel.objects.get(id=request.data["id"], user_id__group=user.group_id)
        except:
            return Response({"error": "존재하지 않는 식단입니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 식후 혈당량 이미 있는지 검사
        if diet_data.level is not None:
            return Response({"error": "식후 혈당량 값이 이미 존재합니다."}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(validated_data=request.data)
        return Response(status=status.HTTP_201_CREATED)


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
                                                             created_at__date__range=[start_date, end_date]).order_by(
                '-level')
            low_blood_list = BloodSugarLevel.objects.filter(user_id__group=user.group_id, level__isnull=False,
                                                            created_at__date__range=[start_date, end_date]).order_by(
                'level')
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        high_blood_serializer = BloodDietSerializer(high_blood_list, many=True, context={"request": request})
        low_blood_serializer = BloodDietSerializer(low_blood_list, many=True, context={'request': request})

        # best top 3
        for i in range(0, 3):
            try:
                best.append(low_blood_serializer.data[i]['diet'])
            except:
                break

        # worst top 3
        for i in range(0, 3):
            try:
                worst.append(high_blood_serializer.data[i]['diet'])
            except:
                break

        res_data = {
            'best': best,
            'worst': worst
        }

        return Response(res_data, status=status.HTTP_200_OK)


# 주간 혈당 리포트 api
class BloodLevelReportView(APIView):
    def get_blood_level(self, blood_sugar_level):
        if blood_sugar_level >= 140:  # 고혈당
            return 3
        elif blood_sugar_level >= 70:  # 정상 혈당
            return 2
        else:  # 저혈당
            return 1

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

        # 일주일간 그룹의 식후 혈당량 정보 가져오기
        try:
            all_blood_data = BloodSugarLevel.objects.filter(user_id__group=user.group_id)
            blood_data = all_blood_data.filter(created_at__date__range=[start_date, end_date]).order_by(
                'created_at__date')
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # 일주일간 데이터가 총 데이터 수와 같다면 (아직 서비스 가입 후 일주일이 지나지 않음)
        if all_blood_data.count() == blood_data.count():
            start_date = blood_data[0].created_at.date()

        # 요일 별 혈당량 평균과 저혈당, 정상혈당, 고혈당 개수 세기
        data = []
        cur_date = end_date
        blood_level = [0, 0, 0, 0]  # 1: 저혈당 요일 수, 2: 정상 혈당 요일 수, 3: 고혈당 요일 수
        days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        print(cur_date, start_date)
        while cur_date >= start_date:
            date_level_avg = BloodSugarLevel.objects.filter(created_at__date=cur_date).values('created_at__date'). \
                annotate(Avg('level')).filter(user_id__group=user.group_id, level__isnull=False)
            if date_level_avg.count() == 0:
                data.append({"day": days[cur_date.weekday()], "level": 0})
            else:
                day = date_level_avg[0]["created_at__date"].weekday()
                level = self.get_blood_level(date_level_avg[0]["level__avg"])
                blood_level[level] += 1
                data.append({"day": days[day], "level": level})
            cur_date -= timedelta(days=1)  # 하루 빼기

        res_data = {
            "start": start_date.strftime('%Y.%m.%d')[2:10],
            "end": end_date.strftime('%Y.%m.%d')[5:10],
            "low": blood_level[1],
            "common": blood_level[2],
            "high": blood_level[3],
            "data": data
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

        # 일주일 이내 식후 혈당량 오름차순 정렬해서 가져오기
        try:
            blood_list = BloodSugarLevel.objects.filter(user_id__group=user.group_id, level__isnull=False,
                                                        created_at__date__range=[start_date, end_date]).order_by(
                'level')
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if blood_list.count() < 3:
            return Response({"error": "아직 나에게 딱 맞는 레시피가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        res_data = []
        serializer = BloodDietSerializer(blood_list, many=True, context={"request": request})
        for i in range(0, 2):
            res_data.append(serializer.data[i]["diet"])
        return Response(res_data, status=status.HTTP_200_OK)
