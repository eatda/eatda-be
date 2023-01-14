from django.conf.urls.static import static
from django.urls import path

from eatda_be import settings
from user.views import UserCharacterView

urlpatterns = [
    path('character', UserCharacterView.as_view())
]