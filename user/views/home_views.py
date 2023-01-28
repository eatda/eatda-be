from datetime import datetime

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from account.views import AuthView
from diet.serializers import DietSimpleSerializer
from user.models import Info, BloodSugarLevel, Like
from user.serializers import BloodSerializer, HomeLikeSerializer


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
