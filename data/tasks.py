from __future__ import absolute_import, unicode_literals

import requests, zipfile, io, os, datetime, json
import pandas as pd

from django.core.cache import cache

from celery import shared_task

@shared_task(name = "downloads_and_cache_the_csv_file")
def download_and_cache_csv():
    '''
    Downloads the CSV file, clear the cache, populate the cache with new data
    '''
    today = datetime.datetime.now()
    dmy = today.strftime("%d-%m-%Y").split("-")
    file_name = "EQ"+dmy[0]+dmy[1]+dmy[2][2:]
    url = "https://www.bseindia.com/download/BhavCopy/Equity/"+file_name+"_CSV.ZIP"
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36"}
    req = requests.get(url, headers=headers)
    if req.ok:
        zipped = zipfile.ZipFile(io.BytesIO(req.content))
        zipped.extractall(os.getcwd()+"/data")
        # Delete the previous file. It may have happened that for a day, CSV file was not released.
        # Go back from today for 5 days and check if you can find any previous CSV file and delete it.
        day = 1
        while(day<=5):
            prev_day = today - datetime.timedelta(day)
            prev_dmy = prev_day.strftime("%d-%m-%Y").split("-")
            prev_file_name = "EQ"+prev_dmy[0]+prev_dmy[1]+prev_dmy[2][2:]
            #print(prev_file_name)
            if os.path.isfile(os.getcwd()+"/data/"+prev_file_name+".CSV"): 
                os.remove(os.getcwd()+"/data/"+prev_file_name+".CSV")
                break
            day += 1
        # Clear the old cache data
        cache.clear()
        # Cache the list of company names using filename as key.
        df_equity = pd.read_csv(os.getcwd()+"/data/"+file_name+".CSV")
        all_company_names = df_equity["SC_NAME"].apply(lambda x: str(x).rstrip().lstrip()).tolist()
        cache.set(file_name, all_company_names)
        # Cache the equity data of each company using name as key.
        for idx in range(len(df_equity)):
            company_name = str(df_equity.iloc[idx]["SC_NAME"]).rstrip().lstrip()
            comapny_code = int(df_equity.iloc[idx]["SC_CODE"])
            company_open = float(df_equity.iloc[idx]["OPEN"])
            company_high = float(df_equity.iloc[idx]["HIGH"])
            company_low = float(df_equity.iloc[idx]["LOW"])
            company_close = float(df_equity.iloc[idx]["CLOSE"])
            attributes = [comapny_code, company_name, company_open, company_high, company_low, company_close]
            cache.set(company_name, attributes)


