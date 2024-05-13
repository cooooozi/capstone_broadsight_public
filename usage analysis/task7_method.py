import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
import plotly.express as px

from urllib.parse import unquote
from plotly.subplots import make_subplots
import plotly.graph_objects as go

def data_api_filter(data):
    """
    Filter the input data to extract only the API-related entries while excluding entries 
    with IP address-based URLs
    """
    
    data_api = data[data["request_url"].str.contains("api")].copy()

    pattern = r'https://\d+\.\d+\.\d+\.\d+(?::\d+)?/'

    data_api = data_api[~data_api['request_url'].str.contains(pattern)]

    #data_api.to_csv("data_api.csv", index = False)
    #print("Successful save API data")
    return data_api


def data_search_filter(data_api):
    """
    Filter the input API data to extract only entries related to fuzzy search and perform data cleaning 
    for further analysis.
    """
    data_search = data_api[data_api['request_url'].str.contains("fuzzySearch", na=False)].copy()

    # clean the url path
    data_search['request_url'] = data_search['request_url'].str.replace(
        "https://app.broadsighttracker.ca:443/api/", "", regex=False)

    # split function and paramater
    data_search[['path', 'query']] = data_search['request_url'].str.split('?', expand=True)
    data_search[['section', 'action']] = data_search['path'].str.split('/', expand=True)
    data_search.drop(['path'], axis=1, inplace=True)

    # split queryString and category
    query_params = data_search['query'].str.split('&', expand=True).stack().str.split('=', expand=True).reset_index(level=1, drop=True)
    query_params.columns = ['param', 'value']

    query_params = query_params.pivot_table(index=query_params.index, columns='param', values='value', aggfunc='first')

    data_search = pd.concat([data_search.drop('query', axis=1), query_params], axis=1)

    # unquote strings for category and queryString
    data_search["category"] = data_search["category"].apply(unquote)
    data_search["queryString"] = data_search["queryString"].apply(unquote)

    # Replace both 'issues' with 'media interaction' and 'service' with 'service log'
    data_search['section'] = data_search['section'].replace({'issues': 'media interaction', 'services': 'service log'})

    # data_search is the clean data for quickSearch analysis
    return data_search

def search_section_view(data, visual = False):
    """
    Analyze and visualize the count of entries in different sections (ServiceLog and MediaInteraction) based on the provided data.

    Parameters:
    - data (DataFrame): Input DataFrame containing request data.
    - visual (bool, optional): If True, display a count plot visualization. Default is False.

    Returns:
    - Series: Counts of entries in each section.
    """
    
    data_api = data_api_filter(data)
    data_search = data_search_filter(data_api)
    
    counts = data_search["section"].value_counts()
    
    if visual == True:
        sns.countplot(data=data_search, x="section", palette='Set2')
        for i, count in enumerate(counts):
            plt.text(i, count + 0.1, str(count), ha='center', va='bottom', fontsize=12)

        plt.axhline(0, color='grey', linewidth=0.5)

        plt.xlabel('Section', fontsize=14)
        plt.ylabel('Count', fontsize=14)
        plt.title('Count of Each Section', fontsize=16)
        plt.show()
    
    return counts
    

def search_category_view(data, section_split = False, pie_visual = False):
    """
    Analyze and visualize the distribution of searching categories based on the provided data

    Parameters:
    - data (DataFrame): Input DataFrame containing request data.
    - section_split (bool, optional): If True, splits the visualization by section. Default is False.
    - pie_visual (bool, optional): If True, display a pie chart visualization. Default is False.

    Returns:
    - DataFrame or tuple of DataFrames: If section_split is False, returns a DataFrame containing 
      the counts of each category. If section_split is True, returns two DataFrames, one for each section.
    """
    data_api = data_api_filter(data)
    data_search = data_search_filter(data_api)
    
    if section_split == False:
        category_counts = data_search["category"].value_counts()
        
        if pie_visual == True:
            plt.figure(figsize=(6, 6))
            patches, texts, autotexts = plt.pie(category_counts, labels=None, autopct='%1.1f%%', startangle=140)

            percentages = [f'{count / len(data_search) * 100:.1f}%' for count in category_counts.values]
            legend_labels = [f'{label} ({percentage})' for label, percentage in zip(category_counts.index, percentages)]
            plt.legend(legend_labels, title="Category", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

            plt.title('Distribution of Categories', fontdict={'fontsize': 16})

            sns.set()
            sns.despine()
            plt.show()
            
        return category_counts
            
    else:
        df_service = data_search.groupby(["section","category"]).size()["service log"]
        df_service = pd.DataFrame(df_service).reset_index()
        df_service.columns = ['category_service', 'count']
        
        df_media = data_search.groupby(["section","category"]).size()["media interaction"]
        df_media = pd.DataFrame(df_media).reset_index()
        df_media.columns = ['category_media', 'count']
        
        if pie_visual == True:
        
        # split graph
            fig = make_subplots(rows=1, cols=2, specs=[[{'type':'pie'}, {'type':'pie'}]])
            fig.add_trace(
                go.Pie(labels=df_service['category_service'], values=df_service['count'], hole=0.4, name='service log'),
                row=1, col=1
            )
            fig.add_trace(
                go.Pie(labels=df_media['category_media'], values=df_media['count'], hole=0.4, name='media interaction'),
                row=1, col=2
            )
            fig.update_layout(
                title=dict(text='Distribution of Categories', font=dict(size=20)),
                annotations=[
                    dict(text="media interactions", x=0.8, y=-0.1, showarrow=False),
                    dict(text="service log", x=0.2, y=-0.1, showarrow=False),
        
                ],
                legend=dict(font=dict(size=12)),
                height=400, width=800
            )

            fig.show()
        return df_service, df_media
        
    

def search_query_view(data, top_nums = 20, visual = False):
    """
    Analyze and visualize the top queries used for searching based on the provided data.

    Parameters:
    - data (DataFrame): Input DataFrame containing request data.
    - top_nums (int, optional): Number of top queries to consider. Default is 20.
    - visual (bool, optional): If True, display a bar chart visualization. Default is False.

    Returns:
    - Series or Altair Chart: If visual is False, returns a Series containing the counts of 
      top queries. If visual is True, returns an Altair Chart visualizing the top queries.

    """
    data_api = data_api_filter(data)
    data_search = data_search_filter(data_api)
    
    query_counts = data_search["queryString"].value_counts().head(top_nums)
    
    if visual == True:
        df_query = pd.DataFrame({'query': query_counts.index, 'count': query_counts.values})

        chart = alt.Chart(df_query).mark_bar().encode(
            y=alt.Y('query:N', title='Query', sort='-x'),
            x=alt.X('count:Q', title='Count'),
            color=alt.Color('query:N', scale=alt.Scale(scheme='category20'), legend=None),
            tooltip=[alt.Tooltip('count:Q', title='Count')]
        ).properties(
            title=f'Top {top_nums} Queries for Searching',
            width=600,
            height=300
        )

        text = chart.mark_text(
            align='left',
            baseline='middle',
            dx=3  
        ).encode(
            text='count:Q'  
        )
        
        chart_top = (chart + text).configure_axis(
                                labelFontSize=12,
                                titleFontSize=14
                                ).configure_title(
                                fontSize=16
                            )
        
        return chart_top
    
    else:
        return query_counts


def apply_custom_theme(chart):
    # helper function for plot
    return chart.configure_title(fontSize=16, fontWeight='normal', color='black') \
                .configure_axis(labelFontSize=12, titleFontSize=14, titleFontWeight='normal', labelColor='black', titleColor='black') \
                .configure_legend(labelFontSize=11, titleFontSize=12, titleFontWeight='bold', labelColor='black', titleColor='black')


def search_query_view_split(data, top_nums = 10, visual = False):
    """
    Analyze and visualize the top queries used for searching split by section (ServiceLog and MediaInteraction) based on the provided data.

    Parameters:
    - data (DataFrame): Input DataFrame containing request data.
    - top_nums (int, optional): Number of top queries to consider. Default is 10.
    - visual (bool, optional): If True, display a combined bar chart visualization for both sections. Default is False.

    Returns:
    - Altair Chart or tuple of DataFrames: If visual is True, returns a combined Altair Chart visualizing 
      the top queries for both sections. If visual is False, returns two DataFrames, one for each section.

    """
    data_api = data_api_filter(data)
    data_search = data_search_filter(data_api)
    
    # service Log
    query_counts_services = data_search[data_search["section"] == "service log"]["queryString"].value_counts().head(top_nums)
    df_query_services = pd.DataFrame({'query_service': query_counts_services.index, 'count': query_counts_services.values})
    
    # media interaction
    query_counts_issues = data_search[data_search["section"] == "media interaction"]["queryString"].value_counts().head(top_nums)
    df_query_media = pd.DataFrame({'query_media': query_counts_issues.index, 'count': query_counts_issues.values})
    
    if visual == True:
        # plot service query
        chart_services = alt.Chart(df_query_services).mark_bar().encode(
            y=alt.Y('query_service:N', title='Searched Query', sort='-x'),
            x=alt.X('count:Q', title='Count'),
            color=alt.Color('query_service:N', scale=alt.Scale(scheme='category20'), legend=None),
            tooltip=[alt.Tooltip('count:Q', title='Count')]
        ).properties(
            title='ServiceLog Searching',
            width=250,  
            height=250)

        text_services = chart_services.mark_text(
            align='left',
            baseline='middle',
            dx=3  
        ).encode(
            text='count:Q'  
        )
        
        # plot media query
        
        chart_issues = alt.Chart(df_query_media).mark_bar().encode(
            y=alt.Y('query_media:N', title=None,sort='-x'),
            x=alt.X('count:Q', title='Count'),
            color=alt.Color('query_media:N', scale=alt.Scale(scheme='category20'), legend=None),
            tooltip=[alt.Tooltip('count:Q', title='Count')]
        ).properties(
            title='MediaInteraction Searching',
            width=250,  
            height=250,
        )

        text_issues = chart_issues.mark_text(
            align='left',
            baseline='middle',
            dx=3  
        ).encode(
            text='count:Q'  
        )
        
        # combine two charts 
        # use shard color because the queryStrings are not same in two plots
        combined_chart = alt.hconcat(chart_services + text_services, chart_issues + text_issues).resolve_scale(color='shared')
        combined_chart = apply_custom_theme(combined_chart)

        combined_chart = combined_chart.properties(
             title=alt.TitleParams(text=f"Top {top_nums} Searching Queries", fontWeight='bold',fontSize=20, anchor='middle')
        )
        
        return combined_chart
    else:
        return df_query_services, df_query_media
    


def search_time_series(data, section_split = False):
    """
    Analyze and visualize the time series of query counts based on the provided data.

    Parameters:
    - data (DataFrame): Input DataFrame containing request data.
    - section_split (bool, optional): If True, visualize time series for each section separately. Default is False.

    """
    data_api = data_api_filter(data)
    data_search = data_search_filter(data_api)
    data_search["time"] = pd.to_datetime(data_search["time"])
    data_search.set_index("time", inplace=True)
    
    if section_split == True:
        grouped_data = data_search.groupby('section')
        plt.figure(figsize=(10, 6))
        colors = ['blue', 'green'] 
        for i, (name, group) in enumerate(grouped_data):
            daily_mean = group.resample('D').size().mean()
            plt.axhline(y=daily_mean, linestyle='--', label=f'Average {name} Search Count ', color=colors[i])
            group.resample('D').size().plot(label=f'Daily {name} Search Count ')

        plt.title('Time Series of Query Counts (Daily)')
        plt.xlabel('Date')
        plt.ylabel('Query Counts')
        plt.legend()
        plt.grid(True)
        plt.show()
    else:
        daily_mean = data_search.resample('D').size().mean()
        
        plt.figure(figsize=(10, 6))
        plt.axhline(y=daily_mean, color='r', linestyle='--', label='Average Search Count')
        data_search.resample('D').size().plot(label='Daily Search Count')
        plt.title('Time Series of Query Counts (Daily)')
        plt.xlabel('Date')
        plt.ylabel('Query Counts')
        plt.legend()
        plt.grid(True)
        plt.show()
        