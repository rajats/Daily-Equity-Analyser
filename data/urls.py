from django.urls import path

from .views import search_equity, list_company_names

urlpatterns = [
    path('search/', search_equity, name="search_equity"),
    path('listcompanynames/', list_company_names, name="list_company_names"),
]