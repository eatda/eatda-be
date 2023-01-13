from django.urls import path

from diet.views import DietAllergyView

urlpatterns = [
    path('allergy', DietAllergyView.as_view())
]