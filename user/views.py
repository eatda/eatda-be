from django.shortcuts import render

# 이미 선택된 캐릭터 제외하고 캐릭터 리스트 보내주는 api

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from user.models import Character
from user.serializers import CharacterSerializer


class UserCharacterView(APIView):
    def get(self, request):
        try:
            group_id = request.GET.get('groupid')
            characterList = Character.objects.exclude(id=group_id)
            serializer = CharacterSerializer(characterList, many=True,context={'request': request})
            print(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


