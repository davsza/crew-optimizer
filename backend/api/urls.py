from django.urls import path
from . import views

urlpatterns = [
    path('shifts/', views.ShiftListCreate.as_view(), name="shifts"),
    path('shifts/delete/<int:pk>', views.ShiftDelete.as_view(), name="delete-shift"),
]
