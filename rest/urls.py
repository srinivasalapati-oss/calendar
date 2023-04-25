# from django.urls import path
# from .views import GoogleCalendarInitView, GoogleCalendarRedirectView
#
# urlpatterns = [
#     path('calendar/init/', GoogleCalendarInitView.as_view(), name='google_calendar_init'),
#     path('calendar/redirect/', GoogleCalendarRedirectView.as_view(), name='google_calendar_redirect'),
# ]

from django.urls import path
from .views import GoogleCalendarInitView, GoogleCalendarRedirectView

urlpatterns = [
    path('calendar/init/', GoogleCalendarInitView, name='google_calendar_init'),
    path('calendar/redirect/', GoogleCalendarRedirectView, name='google_calendar_redirect'),
]
