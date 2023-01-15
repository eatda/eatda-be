from django.urls import path

from diet.views import DietAllergyView, FilterView

urlpatterns = [
    path('allergy/', DietAllergyList.as_view()),
    path('filter/', FilterView.as_view())
]
