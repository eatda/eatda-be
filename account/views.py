import jwt
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from eatda_be.settings import SECRET_KEY
from account.serializers import RegisterSerializer, LoginSerializer
from user.serializers import InfoAuthSerializer, InfoSerializer, UserAllergySerializer
from user.models import Info, UserAllergy
from django.contrib.auth import get_user_model

User = get_user_model()


# 회원 가입
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=False):
            # 로그인 유저 정보 저장
            user = serializer.save(request.data)

            # 유저 전체 정보 (info) 저장
            info_serializer = InfoSerializer(data=request.data)
            if info_serializer.is_valid(raise_exception=False):
                user_info = info_serializer.save(request.data)

                # 유저-알러지 정보 저장
                user_allergy = []
                for data in request.data['allergy']:
                    user_allergy.append(UserAllergy(user_id=user.id, allergy_id=data["id"]))
                allergy_serializer = UserAllergySerializer(data=user_allergy, many=True)
                if allergy_serializer.is_valid(raise_exception=False):
                    allergy_serializer.save(user_allergy, many=True)
                else:
                    user_info.delete()
                    user.delete()
            else:  # 유저 정보 저장 시 에러 났다면 -> 로그인 유저 정보도 지우기
                user.delete()
                return Response(info_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # 유저 정보 얻어오기
            info = Info.objects.get(user_id=serializer.data.id)
            info_serializer = InfoAuthSerializer(info)

            # jwt token 발급
            token = TokenObtainPairSerializer.get_token(user)  # 토큰 생성
            refresh_token = str(token)  # refresh 토큰
            access_token = str(token.access_token)  # access 토큰

            res_data = {
                'access_token': access_token,
                'user_info': info_serializer
            }
            return Response(res_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 로그인
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=False):
            access_token = serializer.validated_data.get('access_token')
            refresh_token = serializer.validated_data.get('refresh_token')

            # 유저 정보 얻어오기
            user_id = serializer.validated_data.get('user').id
            info = Info.objects.get(user_id=user_id)
            info_serializer = InfoAuthSerializer(info)

            res_data = {
                'access_token': access_token,
                'user_info': info_serializer
            }
            return Response(res_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 인가
class AuthView(APIView):
    def get(self, request):
        # access token을 decode해서 유저 id 추출
        access_token = request.headers.get('access_token')
        if not access_token:
            return Response({"message": "토큰 없음"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # access token을 decode해서 유저 id 추출
            payload = jwt.decode(access_token, SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')

            # 유저 정보 얻어오기
            user = get_object_or_404(User, pk=user_id)
            return Response({
                'user_id': user_id,
                'user_info' : user.info
            }, status=status.HTTP_200_OK)
        except jwt.exceptions.InvalidSignatureError:
            # 토큰 유효하지 않음
            return Response({"message": "유효하지 않은 토큰"}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.exceptions.ExpiredSignatureError:
            # 토큰 만료 기간 다 됨
            return Response({"message": "토큰 기간 만료"}, status=status.HTTP_403_FORBIDDEN)
