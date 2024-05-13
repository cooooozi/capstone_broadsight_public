import pandas as pd
import sys
import os
def analyze_requests(file_path, search_keyword):
    # Load the data from CSV
    data = pd.read_csv(file_path)
    # Filter rows where the ‘request_url’ column contains the specified search keyword
    filtered_data = data[data["request_url"].str.contains(search_keyword, na=False)]
    # Group by ‘client_ip’ and count the occurrences
    ip_counts = filtered_data.groupby("client_ip").size().reset_index(name="count")
    # Print the counts of IPs
    print(ip_counts)

    # Get current dir
    current_dir = os.path.dirname(__file__)
    # Specify searchResult folder path
    folder_path = os.path.join(current_dir, "searchResult")
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    # Generate dynamic file name using the search keyword
    file_name = f"ip_counts_{search_keyword}.csv"
    # Generate full file path
    file_path = os.path.join(folder_path, file_name)
    
    # save count results as csv
    ip_counts.to_csv(file_path, index = False)
    print("Successfully save search result as csv")
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python task2.py <file_path> <search_keyword>")
    else:
        file_path = sys.argv[1]
        search_keyword = sys.argv[2]
        analyze_requests(file_path, search_keyword)