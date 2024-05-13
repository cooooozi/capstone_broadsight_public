import pandas as pd
import numpy as np
import re

def get_api_request(data, pivot = False):
    # get api path
    data_request = data[["request_url", "request_verb"]]
    data_api = data_request[data_request["request_url"].str.contains("api")].copy()
    data_api["path"] = data_api["request_url"].str.replace(r'.*/api','',regex=True)
    data_api["path"] = data_api["path"].apply(lambda x: re.sub(r'\?.*', '', x))
    # count api request frequency
    api_data = data_api.groupby(["request_verb","path"]).size().reset_index(name='count')
    api_data = api_data.sort_values(by='count', ascending=False)
    
    if pivot == True:
        api_pivot_table = api_data.pivot_table(index='path', columns='request_verb', values='count', fill_value=0)
        return api_pivot_table
    else:
        return api_data