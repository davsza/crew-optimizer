from django.urls import path
from . import views


urlpatterns = [
    path('shifts/', views.ShiftListCreate.as_view(), name="shifts"),
    path('shifts/delete/<int:pk>', views.ShiftDelete.as_view(), name="delete-shift"),
    path('get-user-group/', views.get_user_group, name='get_user_group'),
]
