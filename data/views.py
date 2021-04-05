import requests, zipfile, io, os, datetime, json
import pandas as pd

from django.shortcuts import render, Http404, HttpResponse, HttpResponseRedirect
from django.core.cache import cache

from django.http import JsonResponse

def get_file_name_for_today(today):
    '''
    Finds the csv filename for today depending on whether time is greater than or 
    less than 1800 hours.
    '''
    hour = today.hour
    if hour < 18:
        today = today - datetime.timedelta(1)
    dmy = today.strftime("%d-%m-%Y").split("-")
    file_name = "EQ"+dmy[0]+dmy[1]+dmy[2][2:]
    return file_name

def get_file_name_on_cache_miss(today):
    '''
    If filename for today is not in cache, there may have been delay in file-upload or it was not uploaded.
    Find last file name stored then.
    '''
    day = 1
    file_name = ''
    # Find the last most recent file stored. Check last 4 days.
    while(day<=4):
        prev_day = today - datetime.timedelta(day)
        prev_dmy = prev_day.strftime("%d-%m-%Y").split("-")
        file_name = "EQ"+prev_dmy[0]+prev_dmy[1]+prev_dmy[2][2:]
        #print("checking ",file_name)
        if os.path.isfile(os.getcwd()+"/data/"+file_name+".CSV"): 
            break
        day += 1
    return file_name


def get_cached_file_name_and_company_names(today):
    '''
    Finds the last filename stored. If the cache is crashed, again re-populate cache
    with file name as key and  list of company names as value respectively.
    '''
    all_company_names = [] 
    file_name = get_file_name_for_today(today)
    if cache.get(file_name):
        #print("found in file name in cache")
        all_company_names = cache.get(file_name)
    else:
        #print("not found")
        file_name = get_file_name_on_cache_miss(today)
        if cache.get(file_name):
            all_company_names = cache.get(file_name)
        else:
            # If cache is crashed, again repopulate the cache with file name as key and
            # list of company names as value.
            df_equity = pd.read_csv(os.getcwd()+"/data/"+file_name+".CSV")
            all_company_names = df_equity["SC_NAME"].apply(lambda x: str(x).rstrip().lstrip()).tolist()
            cache.set(file_name, all_company_names)
    return file_name, all_company_names

def home(request):
    '''
    view for home page
    '''
    context = {}
    return render(request, "data/equity_data.html", context)

# This is not implemented, it was not working with chrome.
# Will be needed if populate the dropdown via backend. 
def dropdown_data(request):
    '''
    Returns json of company names. This API will be used to populate the dropdown 
    '''
    today = datetime.datetime.now()
    _, all_company_names = get_cached_file_name_and_company_names(today)
    all_company_name_objs = []
    for company_name in all_company_names:
        all_company_name_objs.append({'name':company_name})
    return JsonResponse({'company_names': all_company_name_objs})

def list_company_names(request):
    context = {}
    today = datetime.datetime.now()
    _, all_company_names = get_cached_file_name_and_company_names(today)
    context["company_names"] = all_company_names
    return render(request, "data/list_company_names.html", context)



def search_equity(request):
    '''
    Returns json of matched company details (name, code, open, high, low , close) with 
    the search query
    '''
    company_data = None
    data = json.loads(request.body)
    #search query
    query = data['query'].upper().rstrip().lstrip()

    today = datetime.datetime.now()
    file_name, all_company_names = get_cached_file_name_and_company_names(today)

    # Check if searched company name is valid
    if query in all_company_names:
        # Check if searched company name is in cache 
        if cache.get(query):
            #print(query, "found in cache")
            company_data = cache.get(query)
        else:
            # This is needed if cache is crashed suddenly. Again re-populate the cache with key
            # as company name and details (name, code, open, high, low , close) as value respectively
            # for each company name
            df_equity = pd.read_csv(os.getcwd()+"/data/"+file_name+".CSV")
            for idx in range(len(df_equity)):
                company_name = str(df_equity.iloc[idx]["SC_NAME"]).rstrip().lstrip()
                comapny_code = int(df_equity.iloc[idx]["SC_CODE"])
                company_open = float(df_equity.iloc[idx]["OPEN"])
                company_high = float(df_equity.iloc[idx]["HIGH"])
                company_low = float(df_equity.iloc[idx]["LOW"])
                company_close = float(df_equity.iloc[idx]["CLOSE"])
                attributes = [comapny_code, company_name, company_open, company_high, company_low, company_close]
                cache.set(company_name, attributes)
            # Get the company details from the cache
            company_data = cache.get(query)
        # Create company details object
        if company_data:
            company_obj = {
                "company_code": company_data[0],
                "company_name": company_data[1],
                "open": company_data[2],
                "high": company_data[3],
                "low": company_data[4],
                "close": company_data[5],
            }
            return JsonResponse({"company": company_obj })
    return JsonResponse({"company": {} })


