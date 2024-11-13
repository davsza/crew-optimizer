from django.urls import path
from . import views


urlpatterns = [
    path('message/', views.MessageListCreate.as_view(), name="message"),
    path('rosters/<int:week_number>',
         views.RosterGivenWeekQuery.as_view(), name="rosters"),
    path('rosters/lastweeks/<int:week_number>',
         views.RosterPreviousWeeksQuery.as_view(), name="rosters"),
    path('rosters/delete/<int:pk>',
         views.RosterDelete.as_view(), name="delete-roster"),
    path('get-user-data/', views.UserDataView.as_view(), name='get_user_data'),
    path('get-schedules/', views.RosterListCreate.as_view(), name="get-schedules"),
    path('get-rosters-admin/<int:week_number>',
         views.RosterGivenWeekQueryAdmin.as_view(), name="get-rosters-admin"),
    path('user/', views.get_user_details, name="user"),
    path('agent/', views.AgentView.as_view(), name="success"),

]
