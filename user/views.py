from django.shortcuts import render

# 이미 선택된 캐릭터 제외하고 캐릭터 리스트 보내주는 api

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from user.models import Character, Info
from user.serializers import CharacterSerializer, GroupSerializer

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







