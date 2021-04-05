from django.urls import path, include

from data.views import home

urlpatterns = [
	path('', home, name="home"),
	path('data/', include('data.urls')),
]