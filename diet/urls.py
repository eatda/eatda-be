from django.urls import path

from diet.views import DietAllergyView, FilterView, DietDataDetailView, DietDataView

urlpatterns = [
    path('allergy/', DietAllergyView.as_view()),  # 서비스 내 알러지 정보 리스트
    path('filter/', FilterView.as_view()),  # 식단 필터 
    path('<int:id>/', DietDataDetailView.as_view()),  # 식단 상세 정보
    path('', DietDataView.as_view())  # 식단 전체
]
