from django.urls import path

from diet.views import DietAllergyList

urlpatterns = [
    path('allergy/', DietAllergyList.as_view())
]