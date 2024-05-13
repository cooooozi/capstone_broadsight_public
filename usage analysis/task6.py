import pandas as pd
import re

def get_avg_processing_time(data, separate_by_ip=False):
    # Calculate total processing time
    data["processing_time"] = data["request_processing_time"] + data["target_processing_time"] + data["response_processing_time"]
    
    # Filter rows where the URL contains "api" and extract the path
    data_api = data[data["request_url"].str.contains("api")].copy()
    data_api["path"] = data_api["request_url"].str.replace(r'.*/api','',regex=True)
    data_api["path"] = data_api["path"].apply(lambda x: re.sub(r'\?.*', '', x))
    
    # Define grouping criteria based on whether data is separated by client IP
    grouping_columns = ['request_verb', 'path']
    if separate_by_ip:
        grouping_columns.append('client_ip')

    # Group data by the specified criteria
    grouped = data_api.groupby(grouping_columns)['processing_time']
    
    # Calculate mean and variance for each group
    result = grouped.agg(['mean', 'var']).reset_index()
    
    # Rename columns for clarity
    result.rename(columns={'mean': 'Average Processing Time', 'var': 'Variance'}, inplace=True)

    return result
