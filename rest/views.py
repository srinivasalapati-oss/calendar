# import google.oauth2.credentials
# import google_auth_oauthlib.flow
# import googleapiclient.discovery
# from django.http import HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
# from django.views.generic import View
# from rest_framework.views import APIView
#
# #Json credentials
# CLIENT_CONFIG = {
#     "web": {
#         "client_id": "712931087601-pbhtgefhkkn92k6smv0t9kqo3i7i0npc.apps.googleusercontent.com",
#         "project_id": "calendar-384708",
#         "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#         "token_uri": "https://oauth2.googleapis.com/token",
#         "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
#         "redirect_uris":["http://localhost:8000/rest/v1/calendar/redirect/"],
#         "client_secret": "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",
#         "javascript_origins": ["http://localhost:8000"]
#     }
# }
#
# from google_auth_oauthlib.flow import Flow
#
# # defining  CLIENT_ID and CLIENT_SECRET here
# CLIENT_ID = '<your_client_id>'
# CLIENT_SECRET = '<your_client_secret>'
# AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
# TOKEN_URI = 'https://oauth2.googleapis.com/token'
# REDIRECT_URI = 'http://localhost:8000/rest/v1/calendar/redirect/'
# SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
#
#
# class GoogleCalendarInitView(APIView):
#     def get(self, request):
#         # Creating a new instance of the OAuth2 authorization flow
#         flow = Flow.from_client_config(
#             client_config={'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET, 'auth_uri': AUTH_URI,
#                            'token_uri': TOKEN_URI},
#             scopes=SCOPES,
#             redirect_uri=REDIRECT_URI
#         )
#
#         # Generating the authorization URL for the user to click on
#         auth_url, _ = flow.authorization_url(
#             access_type='offline',
#             include_granted_scopes='true'
#             # include_granted_scopes parameter allows the access token to be refreshed automatically
#         )
#
#         # Redirecting user to the authorization URL
#         return HttpResponseRedirect(auth_url)
#
#
# class GoogleCalendarRedirectView(View):
#     def get(self, request, *args, **kwargs):
#         state = request.session['oauth2_state']
#         flow = google_auth_oauthlib.flow.Flow.from_client_config(
#             CLIENT_CONFIG,
#             scopes=['https://www.googleapis.com/auth/calendar.events.readonly'],
#             state=state
#         )
#         flow.redirect_uri = request.build_absolute_uri('/my_projects/v1/calendar/redirect/')
#         authorization_response = request.build_absolute_uri()
#         flow.fetch_token(authorization_response=authorization_response)
#         credentials = flow.credentials
#         request.session['credentials'] = {
#             'token': credentials.token,
#             'refresh_token': credentials.refresh_token,
#             'token_uri': credentials.token_uri,
#             'client_id': credentials.client_id,
#             'client_secret': credentials.client_secret,
#             'scopes': credentials.scopes
#         }
#         return HttpResponseRedirect('//my_projects/v1/calendar/events/')
#
#
# class GoogleCalendarEventsView(View):
#     def get(self, request, *args, **kwargs):
#         if 'credentials' not in request.session:
#             return HttpResponseBadRequest('Missing user credentials')
#
#         credentials = google.oauth2.credentials.Credentials.from_authorized_user_info(
#             request.session['credentials'],
#             scopes=['https://www.googleapis.com/auth/calendar.events.readonly']
#         )
#
#         service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)
#
#         events_result = service.events().list(calendarId='primary', maxResults=10, singleEvents=True,
#                                               orderBy='startTime').execute()
#         events = events_result.get('items', [])
#
#         if not events:
#             return HttpResponseBadRequest('No events found in your calendar')
#
#         response_data = {'events': []}
#
#         for event in events:
#             start = event['start'].get('dateTime', event['start'].get('date'))
#             end = event['end'].get('dateTime', event['end'].get('date'))
#             response_data['events'].append({
#                 'summary': event['summary'],
#                 'start': start,
#                 'end': end
#             })
#
#         return JsonResponse(response_data)


from django.shortcuts import redirect

from rest_framework.decorators import api_view
from rest_framework.response import Response

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import os

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "credentials.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection and REDIRECT URL.
SCOPES = ['https://www.googleapis.com/auth/calendar',
          'https://www.googleapis.com/auth/userinfo.email',
          'https://www.googleapis.com/auth/userinfo.profile',
          'openid']
REDIRECT_URL = 'http://localhost:8000/rest/v1/calendar/redirect'
API_SERVICE_NAME = 'calendar'
API_VERSION = 'v3'


@api_view(['GET'])
def GoogleCalendarInitView(request):
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)

    # The URI created here must exactly match one of the authorized redirect URIs
    # for the OAuth 2.0 client, which you configured in the API Console. If this
    # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
    # error.
    flow.redirect_uri = REDIRECT_URL

    authorization_url, state = flow.authorization_url(
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true',
        # Prompt the user for consent every time the access token needs to be refreshed.
        prompt='consent')

    # Storing the state so the callback can verify the auth server response.
    request.session['state'] = state

    return Response({"authorization_url": authorization_url})


@api_view(['GET'])
def GoogleCalendarRedirectView(request):
    # Specify the state when creating the flow in the callback so that it can
    # verify in the authorization server response.
    state = request.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = REDIRECT_URL

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.get_full_path()
    flow.fetch_token(authorization_response=authorization_response)

    # Save credentials back to session in case access token was refreshed.
    # ACTION ITEM: In a production app, you likely want to save these
    # credentials in a persistent database instead.
    credentials = flow.credentials
    request.session['credentials'] = credentials_to_dict(credentials)

    # Check if credentials are in session
    if 'credentials' not in request.session:
        return redirect('v1/calendar/init')

    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
        **request.session['credentials'])

    # Use the Google API Discovery Service to build client libraries, IDE plugins,
    # and other tools that interact with Google APIs.
    # The Discovery API provides a list of Google APIs and a machine-readable "Discovery Document" for each API
    service = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)

    # Returns the calendars on the user's calendar list
    calendar_list = service.calendarList().list().execute()

    # Getting user ID which is his/her email address
    calendar_id = calendar_list['items'][0]['id']

    # Getting all events associated with a user ID (email address)
    events = service.events().list(calendarId=calendar_id).execute()

    events_list_append = []
    if not events['items']:
        print('No data found.')
        return Response({"message": "No data found or user credentials invalid."})
    else:
        for events_list in events['items']:
            events_list_append.append(events_list)
            return Response({"events": events_list_append})
    return Response({"error": "calendar event aren't here"})


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}
