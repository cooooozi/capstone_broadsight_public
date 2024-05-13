import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from urllib.parse import unquote


def clean_api_endpoint(data):
    ## prepare and clean dataframe
    data_with_api = data[data["request_url"].str.contains("api")].copy()
    data_with_api["request_url"]
    # remove basepath from api
    data_with_api["endpoint"] = data_with_api["request_url"].str.replace(r'.*/api','',regex=True)
    # remove parameters from api
    data_with_api["endpoint"] = data_with_api["endpoint"].apply(lambda x: re.sub(r'\?.*', '', x))
    
    # remove unnecessary direction (include UUID and encoded format) for same endpoint
    data_with_api["endpoint_cleaned"] = data_with_api["endpoint"].apply(clean_endpoint)
    data_with_api["endpoint_cleaned"] = data_with_api["endpoint_cleaned"].apply(clean_UUID)
    data_with_api["endpoint_cleaned"] = data_with_api["endpoint_cleaned"].apply(clean_percent_encoded_path)
    
    return data_with_api

def get_highest_traffic_endpoint_per_ip(data):
    data_with_api = clean_api_endpoint(data)
    
    ## find the highest-traffic-endpoint for each ip
    grouped_data = data_with_api.groupby(["client_ip", "endpoint_cleaned"]).size()
    unstacked_data = grouped_data.unstack(fill_value=0)
    max_requests_per_ip = unstacked_data.max(axis=1)
    max_endpoint_per_ip = unstacked_data.idxmax(axis=1)

    max_requests_per_ip_df = pd.DataFrame({
        "max_requests": max_requests_per_ip,
        "max_endpoint": max_endpoint_per_ip
    }).reset_index()

    max_requests_per_ip_df.rename(columns={'index': 'client_ip'}, inplace=True)
    return max_requests_per_ip_df


def plot_top_n_endpoints(df, n):
    # First, ensure the total requests per endpoint is correctly calculated
    endpoint_totals = df.groupby('max_endpoint')['max_requests'].sum()

    # Sort and pick the top 'n' endpoints
    top_endpoints = endpoint_totals.nlargest(n)

    # Filter the original dataframe to only include the top 'n' endpoints
    filtered_df = df[df['max_endpoint'].isin(top_endpoints.index)]

    # Now group by 'max_endpoint' and 'client_ip', summing requests for stacking
    grouped_data = filtered_df.groupby(['max_endpoint', 'client_ip'])['max_requests'].sum().unstack(fill_value=0)
    sorted_grouped_data = grouped_data.sum(axis=1).sort_values(ascending=False).index
    sorted_grouped_data = grouped_data.loc[sorted_grouped_data]

    # Plotting
    ax = sorted_grouped_data.plot(kind='bar', stacked=True, figsize=(10, 7))
    ax.set_title(f'Top {n} Most Frequently Popular Endpoints)')
    ax.set_xlabel('Endpoint')
    ax.set_ylabel('Total Requests')
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Client IP', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()

    plt.show()
