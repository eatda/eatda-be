from django.conf.urls.static import static
from django.urls import path

from eatda_be import settings
from user.views import UserCharacterView, UserGroupView, UserInfoDetailView, UserHomeView, UserDietView, OurPickView, \
    BloodSugarLevelView, HomeLikeView, DietRankView, BloodLevelReportView, DietFitView, TestDietAllView

urlpatterns = [
    path('info/', UserInfoDetailView.as_view()),  # 유저 정보
    path('character/', UserCharacterView.as_view()),  # 캐릭터 정보
    path('group/code/', UserGroupView.as_view()),  # 그룹 정보
    path('home/', UserHomeView.as_view()),  # 홈
    path('home/like/', HomeLikeView.as_view()),  # 홈화면 좋아요
    path('diet/', UserDietView.as_view()),  # 유저 식단
    path('diet/like/', OurPickView.as_view()),  # OurPick
    path('blood-sugar-level/', BloodSugarLevelView.as_view()),  # 식후 혈당량
    path('diet/rank/', DietRankView.as_view()),  # best&worst top 3 식단
    path('blood-sugar-level/report/', BloodLevelReportView.as_view()),  # 주간 혈당 리포트
    path('diet/fit/', DietFitView.as_view()),  # 유저 맞춤 식단
    path('test/diet/all', TestDietAllView.as_view())  # (테스트용) 유저 관련 식후혈당 기록 모두 삭제
]
