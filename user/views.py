from django.shortcuts import render

# 이미 선택된 캐릭터 제외하고 캐릭터 리스트 보내주는 api

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from user.models import Character, Info
from user.serializers import CharacterSerializer


class UserCharacterView(APIView):
    def get(self, request):
        try:
            # 그룹 내 유저들의 캐릭터 ID 받아오기
            group_id = request.GET.get('groupid')
            groupList = Info.objects.filter(group=group_id).values() #해당하는 그룹id의 유저들 get
            selected_character = list()

            for users in groupList:
                selected_character.append(users['character_id'])
            selected_character.sort()

            # 선택된 캐릭터 제외하기
            allCharacterList = Character.objects.all()

            for select in selected_character:
                unselected = allCharacterList.exclude(id=select)

            serializer = CharacterSerializer(unselected, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


