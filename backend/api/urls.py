from django.urls import path
from . import views


urlpatterns = [
    path('shifts/', views.ShiftListCreate.as_view(), name="shifts"),
    path('shifts/<int:week>', views.ShiftGivenWeekQuery.as_view(), name="shifts"),
    path('shifts/lastweeks/<int:week>',
         views.ShiftLastWeeksQuery.as_view(), name="shifts"),
    path('shifts/delete/<int:pk>', views.ShiftDelete.as_view(), name="delete-shift"),
    path('get-user-data/', views.UserDataView.as_view(), name='get_user_data'),
    path('get-schedules/', views.ShiftListCreate.as_view(), name="get-schedules"),
    path('get-shifts-admin/<int:week>',
         views.ShiftGivenWeekQueryAdmin.as_view(), name="get-shifts-admin"),
    path('user/', views.get_user_details, name="user"),

]
