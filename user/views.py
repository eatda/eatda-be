# 이미 선택된 캐릭터 제외하고 캐릭터 리스트 보내주는 api

from rest_framework import status, exceptions
from rest_framework.response import Response
from rest_framework.views import APIView

from account.views import AuthView
from diet.models import DietAllergy
from user.models import Character, Info, Group, UserAllergy
from user.serializers import CharacterSerializer, GroupSerializer, InfoSerializer, UserAllergySerializer

# 그룹 코드 생성 시 필요한 라이브러리
import uuid, base64, codecs


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

            # 선택된 캐릭터 제외하기
            all_character_list = Character.objects.all()

            for select in selected_character:
                all_character_list = all_character_list.exclude(id=select)

            serializer = CharacterSerializer(all_character_list, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

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