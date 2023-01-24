from django.urls import path
from account.views import RegisterView, LoginView, AuthView, AccountView

urlpatterns = [
    path('register/', RegisterView.as_view()),  # 회원 가입
    path('login/', LoginView.as_view()),  # 로그인
    path('auth/', AuthView.as_view()),  # 인가 (사용자 확인)
    path('', AccountView.as_view())  # 계정 관리
]
