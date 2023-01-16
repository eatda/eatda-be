from django.urls import path

from diet.views import DietAllergyView, FilterView, DietDataDetailView

urlpatterns = [
    path('allergy/', DietAllergyView.as_view()),
    path('filter/', FilterView.as_view()),
    path('<int:id>/', DietDataDetailView.as_view())
]