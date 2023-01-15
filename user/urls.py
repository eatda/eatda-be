from django.conf.urls.static import static
from django.urls import path

from eatda_be import settings
from user.views import UserCharacterView, UserGroupView

urlpatterns = [
    path('character', UserCharacterView.as_view()),
    path('group/code/', UserGroupView.as_view())
]
