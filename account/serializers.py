from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


# 회원 가입
class RegisterSerializer(serializers.ModelSerializer):
    social_id = serializers.CharField(
        required=True,
        write_only=True,
    )

    email = serializers.EmailField(
        required=True,
        write_only=True,
    )

    class Meta:
        model = User
        fields = ['social_id', 'email']

    def save(self, validated_data):
        social_id = validated_data.get('social_id')
        email = validated_data.get('email')
        user = User(
            social_id=social_id,
            email=email
        )
        user.save()
        return user

    def validate(self, data):
        social_id = data.get('social_id', None)
        email = data.get('email', None)

        # 이미 존재하는 계정인지 확인
        if User.objects.filter(social_id=social_id, email=email).exists():
            raise serializers.ValidationError("User already exists")
        return data


# 로그인
class LoginSerializer(serializers.ModelSerializer):
    social_id = serializers.CharField(
        required=True,
        write_only=True,
    )

    email = serializers.EmailField(
        required=True,
        write_only=True,
    )

    class Meta:
        model = User
        fields = ['social_id', 'email']

    def validate(self, data):
        social_id = data.get('social_id', None)
        email = data.get('email', None)

        if User.objects.filter(social_id=social_id, email=email).exists():
            user = User.objects.get(social_id=social_id, email=email)
        else:
            raise serializers.ValidationError("user account not exist")

        token = RefreshToken.for_user(user)  # 토큰 생성
        refresh_token = str(token)  # refresh 토큰
        access_token = str(token.access_token)  # access 토큰

        data = {
            'user': user,
            'refresh_token': refresh_token,
            'access_token': access_token,
        }

        return data
