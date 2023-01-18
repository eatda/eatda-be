# 그룹 코드 생성 시 필요한 라이브러리
import base64
import codecs
import uuid

from django.shortcuts import get_object_or_404
from rest_framework import status, exceptions
from rest_framework.response import Response
from rest_framework.views import APIView

from account.views import AuthView
from diet.models import Data
from diet.serializers import DietSimpleSerializer
from user.models import Character, Info, Group, UserAllergy, BloodSugarLevel, Like, OurPick
from user.serializers import CharacterSerializer, GroupSerializer, InfoSerializer, UserAllergySerializer, BloodSerializer, DietSerializer, OurPickSerializer

from datetime import datetime


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
                        'is_diabetes': info_serializer.data['is_diabetes'],
                        'group_id': info_serializer.data['group_id'],
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


# 유저 캐릭터 리스트 가져오느 api
class UserCharacterView(APIView):
    def get(self, request):
        try:
            # 그룹 내 유저들의 캐릭터 ID 받아오기
            group_id = request.GET.get('groupid')
            group_list = Info.objects.filter(group=group_id).values()  # 해당하는 그룹id의 유저들 get
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


# 오늘의 식단 등록 api
class UserDietView(APIView):
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

        serializer.save(serializer.data)
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request):
        # 인가확인
        if AuthView.get(self, request).status_code is not status.HTTP_200_OK:
            return Response({"error": "로그인 필요"}, status=status.HTTP_401_UNAUTHORIZED)

        # 접속한 유저 정보 가져오기
        user_id = AuthView.get(self, request).data['user_id']
        user = get_object_or_404(Info, user_id=user_id)
        ourpick = request.data

        ourpick = OurPick.objects.get(user_id = user_id, diet_id = request.data['diet_id'])

        # ourpick 삭제 전 데이터 유효성 검사
        request.data["user_id"] = user.user_id
        serializer = OurPickSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 식단 존재 확인
        get_object_or_404(Data, id=request.data["diet_id"])

        # ourpick model에서 선택 삭제
        ourpick.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)