from django.shortcuts import render
from django.shortcuts import redirect
from rest_framework.response import Response
from django.conf import settings
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import os
from django.urls import reverse



from rest_framework.views import APIView
from rest_framework.response import Response
import requests

class GoogleCalendarInitView(APIView):
    def get(self, request):
        authorization_url = f'https://accounts.google.com/o/oauth2/v2/auth?client_id={settings.GOOGLE_OAUTH2_CLIENT_ID}&redirect_uri={request.build_absolute_uri(reverse("google_calendar_redirect"))}&scope=https://www.googleapis.com/auth/calendar.readonly&response_type=code&access_type=offline&prompt=consent'
        return Response({'authorization_url': authorization_url})

class GoogleCalendarRedirectView(APIView):
    def get(self, request):
        code = request.GET.get('code')
        if not code:
            return Response({'error': 'Code not found in the request'}, status=400)
        response = requests.post('https://oauth2.googleapis.com/token', data={
            'code': code,
            'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
            'client_secret': settings.GOOGLE_OAUTH2_CLIENT_SECRET,
            'redirect_uri': request.build_absolute_uri(reverse("google_calendar_redirect")),
            'grant_type': 'authorization_code',
        })
        if response.status_code != 200:
            return Response({'error': 'Failed to exchange code for token'}, status=response.status_code)
        data = response.json()
        access_token = data['access_token']
        response = requests.get('https://www.googleapis.com/calendar/v3/calendars/primary/events', headers={
            'Authorization': f'Bearer {access_token}'
        })
        if response.status_code != 200:
            return Response({'error': 'Failed to retrieve events'}, status=response.status_code)
        events = response.json().get('items', [])
        return Response({'events': events})

