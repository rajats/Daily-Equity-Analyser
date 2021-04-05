from django.urls import path

from .views import search_equity, dropdown_data, list_company_names

urlpatterns = [
	path('populatedroddown/', dropdown_data, name="dropdown_data"),
    path('search/', search_equity, name="search_equity"),
    path('listcompanynames/', list_company_names, name="list_company_names"),
]