import matplotlib.pyplot as plt
from urllib.parse import urlparse, parse_qs

def count_parameter_values_for_endpoint(data, endpoint, parameter):
    # Check if the endpoint starts with '/api'
    if not endpoint.startswith('/api'):
        endpoint_path = '/api' + endpoint
    else:
        endpoint_path = endpoint
    
    endpoint_data = data[data['request_url'].apply(lambda x: urlparse(x).path == endpoint_path)].copy()
    endpoint_data['query_params'] = endpoint_data["request_url"].apply(lambda x: parse_qs(urlparse(x).query))
    endpoint_data[parameter] = endpoint_data['query_params'].apply(lambda x: x.get(parameter, [None])[0])
    
    parameter_count = endpoint_data[parameter].value_counts()
    return parameter_count


def plot_parameter_count(parameter_count):
    plt.figure()  
    bars = plt.bar(parameter_count.index, parameter_count.values, color='skyblue') 
    plt.title('Frequency of Parameters for the Specified Endpoint Path',fontsize = 16) 
    plt.xlabel('Parameter Values')
    plt.ylabel('Counts')  
    plt.xticks(rotation=45)  
    # add counts number on each bar
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval, int(yval),  
                 ha='center', va='bottom', fontsize=10)  
    return plt