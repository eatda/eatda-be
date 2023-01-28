from django.urls import path
from user.views import base_views, blood_views, diet_views, home_views

urlpatterns = [
    # base_views.py
    path('info/', base_views.UserInfoDetailView.as_view()),  # 유저 정보
    path('character/', base_views.UserCharacterView.as_view()),  # 캐릭터 정보
    path('group/code/', base_views.UserGroupView.as_view()),  # 그룹 정보
    path('test/diet/all', base_views.TestDietAllView.as_view()),  # (테스트용) 유저 관련 식후혈당 기록 모두 삭제

    # home_views.py
    path('home/', home_views.UserHomeView.as_view()),  # 홈
    path('home/like/', home_views.HomeLikeView.as_view()),  # 홈화면 좋아요

    # diet_views.py
    path('diet/', diet_views.UserDietView.as_view()),  # 유저 식단
    path('diet/like/', diet_views.OurPickView.as_view()),  # OurPick
    path('diet/rank/', diet_views.DietRankView.as_view()),  # best&worst top 3 식단
    path('diet/fit/', diet_views.DietFitView.as_view()),  # 유저 맞춤 식단

    # blood_views.py
    path('blood-sugar-level/', blood_views.BloodSugarLevelView.as_view()),  # 식후 혈당량
    path('blood-sugar-level/report/', blood_views.BloodLevelReportView.as_view()),  # 주간 혈당 리포트
]
