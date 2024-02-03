import requests
# import parser
from html.parser import HTMLParser
from bs4 import BeautifulSoup
import json
import argparse
import os

# Confluence Username and Apitoken
username = os.environ["CONFLUENCE_USERNAME"]
confluence_apitoken = os.environ["CONFLUENCE_APITOKEN"]

def get_confluence_page_html(username, confluence_apitoken):
    """Get the confluence page to read the table data.

    Args:
        username (str) : email id
        confluence_apitoken (str) : confluence api token
        
    Returns:
        page_body : confluence page body where table resides
    """
    params = {"expand": "body.view"}
    auth = (username, confluence_apitoken)

    response = requests.get(confluence_rest_api, params=params, auth=auth)
    if response.status_code == 200:
        data = response.json()
        storage_content = data.get("body", {}).get("storage", {}).get("value", "")
        page_body = decode_confluence_storage(storage_content)
        return page_body
    else:
        print(
            f"Failed to retrieve Confluence page. Status code: {response.status_code}"
        )
        return None

def decode_confluence_storage(storage_content):
    """Get the decode confluence storage data.

    Args:
        storage_content (str) :html parser
          
    Returns:
        soup : decode html parser confluence storage.
    """
    soup = BeautifulSoup(storage_content, "html.parser")
    return str(soup)

def extract_table_data(html_content):
    """Get the table data.

    Args:
        html_content (str) : content of html
          
    Returns:
        table_data : Extract table data as a list.
    """
    
    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.find("table")
    
    if table:
        # Extract table data as a list of lists
        table_data = []
        for row in table.find_all("tr"):
            row_data = [
                cell.get_text(strip=True) for cell in row.find_all(["td", "th"])
            ]
            table_data.append(row_data)
        return table_data
    else:
        print("No table found on the Confluence page.")
        return None

def find_service_name(data, name):
    """Get the service name from confluence page table

    Args:
        data (str) : table data from confluence
        name (str) : application name
        
    Returns:
        service_name_dict : Application name and service name as key and value
    """
    
    service_name_dict = {}
    for row in data[1:]:
        if row[2] == name:
            key = row[2]
            value = row[3]
            service_name_dict[key] = value
            return service_name_dict
    return None

#Get confluence url and application name
argparser = argparse.ArgumentParser(prog='service-getter',
                                    description='To read table content from confluence page and providing output to jenkins pipeline')
argparser.add_argument('-u', '--url', type=str, metavar='', required=True, help='url to access confluence page')
argparser.add_argument('-a','--appname', type=str, metavar='', required=True, help='Application name')

args = argparser.parse_args()
confluence_rest_api = args.url
application_name = args.appname

#  To get confluence page data
html_content = get_confluence_page_html(username, confluence_apitoken)
# print(f"html_content : {html_content}")

if html_content:
    table_data = extract_table_data(html_content)
    # print(f"table_data : {table_data}")
    if table_data:
        service_names = find_service_name(table_data, application_name)
        if service_names:
            service_names_json = json.dumps(service_names)
            print(service_names_json)
        else:
            print(f"service names not found ")