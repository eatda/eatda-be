from django.conf.urls.static import static
from django.urls import path

from eatda_be import settings
from user.views import UserCharacterView, UserGroupView, UserInfoDetailView, UserHomeView, UserDietView, OurPickView, BloodSugarLevelView


urlpatterns = [
    path('info/', UserInfoDetailView.as_view()),  # 유저 정보
    path('character/', UserCharacterView.as_view()),  # 캐릭터 정보
    path('group/code/', UserGroupView.as_view()),  # 그룹 정보
    path('home/', UserHomeView.as_view()),  # 홈
    path('diet/', UserDietView.as_view()),  # 유저 식단
    path('diet/like/', OurPickView.as_view()),  # OurPick
    path('blood-sugar-level/', BloodSugarLevelView.as_view())  # 식후 혈당량
]
