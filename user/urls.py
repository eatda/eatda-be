from django.conf.urls.static import static
from django.urls import path

from eatda_be import settings
from user.views import UserCharacterView, UserInfoDetailView

urlpatterns = [
    path('info/', UserInfoDetailView.as_view()),  # 유저 정보
    path('character/', UserCharacterView.as_view())  # 캐릭터 정보
]
