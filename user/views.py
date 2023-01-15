from django.shortcuts import render

# 이미 선택된 캐릭터 제외하고 캐릭터 리스트 보내주는 api

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from account.views import AuthView
from user.models import Character, Info, BloodSugarLevel
from user.serializers import CharacterSerializer, GroupSerializer, BloodSerializer, BloodDietSerializer, DietSerializer
from diet.serializers import DietSimpleSerializer
from diet.models import Data
from datetime import datetime

# 그룹 코드 생성 시 필요한 라이브러리
import uuid, base64, codecs


class UserCharacterView(APIView):
    def get(self, request):
        try:
            # 그룹 내 유저들의 캐릭터 ID 받아오기
            group_id = request.GET.get('groupid')
            groupList = Info.objects.filter(group=group_id).values()  # 해당하는 그룹id의 유저들 get
            selected_character = list()

            for users in groupList:
                selected_character.append(users['character_id'])
            selected_character.sort()

            # 선택된 캐릭터 제외하기
            allCharacterList = Character.objects.all()

            for select in selected_character:
                allCharacterList = allCharacterList.exclude(id=select)

            serializer = CharacterSerializer(allCharacterList, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)


# 그룹 코드 생성 api
class UserGroupView(APIView):
    def generate_random_slug_code(self, length=6):
        return base64.urlsafe_b64encode(
            codecs.encode(uuid.uuid4().bytes, "base64").rstrip()
        ).decode()[:length].upper()

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


# 홈 화면 api
class UserHomeView(APIView):
    def get(self, request):
        # 인가확인
        if AuthView.get(self, request).status_code is not status.HTTP_200_OK:
            return Response({"error": "로그인 필요"}, status=status.HTTP_401_UNAUTHORIZED)

        # 접속한 유저 정보 가져오기
        user_id = AuthView.get(self, request).data['user_id']

        # 현재 날짜 가져오기
        # date = datetime.now().date()
        date = "2023-01-15"

        # 오늘의 식단 & 혈당량 정보 리스트로 가져오기
        try:
            diet_blood_list = BloodSugarLevel.objects.filter(user_id=user_id, created_at__contains=date)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # 아침, 점심, 저녁 마다 식단 & 혈당량 정보 얻어오기
        diet = [{}, {}, {}]
        blood_sugar_level = [{}, {}, {}]
        for timeline in range(0, 3):
            try:
                blood_detail = diet_blood_list.get(timeline=timeline)  # 식후 혈당량
                diet_detail = blood_detail.diet  # 식단
                try:
                    serializer = DietSimpleSerializer(diet_detail, context={'request': request})
                except Exception as e:
                    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
                diet[timeline]["is_exist"] = True
                diet[timeline]["data"] = serializer.data
                diet[timeline]["data"]["timeline"] = timeline

                if blood_detail.time is None:  # 식후 혈당량 없다면
                    blood_sugar_level[timeline]["is_exist"] = False
                else:  # 식후 혈당량 입력 되어있다면
                    blood_sugar_level[timeline]["is_exist"] = True
                    serializer = BloodSerializer(blood_detail)
                    blood_sugar_level[timeline]["data"] = serializer.data
            except:
                diet[timeline]["is_exist"] = blood_sugar_level[timeline]["is_exist"] = False
        res_data = {
            "diet": diet,
            "blood_sugar_level": blood_sugar_level
        }
        return Response(res_data, status=status.HTTP_200_OK)
