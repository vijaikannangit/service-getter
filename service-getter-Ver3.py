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
        header = [th.get_text(strip=True) for th in table.find_all('th')]
        # for row in table.find_all("tr"):
        for row in table.find_all('tr')[1:]:
            # row_data = [
                # cell.get_text(strip=True) for cell in row.find_all(["td", "th"])
            row_data = [str(td) for td in row.find_all(['td', 'th'])]
            # table_data.append(row_data)
            table_data.append(dict(zip(header, row_data)))
        return table_data
    else:
        print("No table found on the Confluence page.")
        return None


# def find_service_name(data, name):
#     """Get the service name from confluence page table

#     Args:
#         data (str) : table data from confluence
#         name (str) : application name
        
#     Returns:
#         service_name_dict : Application name and service name as key and value
#     """
    
#     service_name_dict = {}
#     for row in data[1:]:
#         if row[2] == name:
#             key = row[2]
#             value = row[3]
#             service_name_dict[key] = value
#             return service_name_dict
#     return None

def clean_text(text):
    return text.replace('<br/>', '').replace('<p>', '').replace('</p>', '').strip()


# def find_service_name(table_data, target_application_name):
#     result = {}
#     for row in table_data:
#         application_name = row['Applications']
#         if target_application_name.lower() in application_name.lower():
#             # Clean application name
#             application_name = BeautifulSoup(application_name, 'html.parser').get_text(strip=True)

#             service_name_data = row['ServiceName']
#             # Extract service names and corresponding values
#             service_names = [item.split(':') for item in service_name_data.split('<p>') if ':' in item]
#             service_data = {name.strip(): value.strip() for name, value in service_names if len(name) > 0 and len(value) > 0}
#             # Remove paragraphs and line breaks from service data
#             service_data = {key: value.replace('<br/>', '').replace('<p>', '').replace('</p>', '') for key, value in service_data.items()}
            
#             result[application_name] = service_data
#     return result

def clean_text(text):
    # Remove HTML tags
    cleaned_text = BeautifulSoup(text, 'html.parser').get_text(strip=True)
    # Remove additional characters
    cleaned_text = cleaned_text.replace('<br/>', '').replace('<p>', '').replace('</p>', '').replace('</td>', '')
    return cleaned_text.strip()

# def find_service_name(table_data, target_application_name):
#     result = {}
#     for row in table_data:
#         application_name = row['Applications']
#         if target_application_name.lower() in application_name.lower():
#             # Clean application name
#             application_name = clean_text(application_name)

#             service_name_data = row['ServiceName']
#             # Extract service names and corresponding values
#             service_names = [item.split(':') for item in service_name_data.split('<p>') if ':' in item]
#             service_data = {name.strip(): clean_text(value) for name, value in service_names if len(name) > 0 and len(value) > 0}
            
#             result[application_name] = service_data
#     return result

def find_service_name(table_data, target_application_name):
    result = {}
    for row in table_data:
        application_name = row['Applications']
        if target_application_name.lower() in application_name.lower():
            # Clean application name
            application_name = clean_text(application_name)

            service_name_data = row['ServiceName']
            # Extract service names and corresponding values
            service_names = [item.split(':') for item in service_name_data.split('<p>') if ':' in item]
            service_data = {name.strip(): clean_text(value) for name, value in service_names if len(name) > 0 and len(value) > 0}
            
            result[application_name] = service_data

    # Format the result with line breaks
    # formatted_result = json.dumps(result, indent=2)
    # print(formatted_result)
    return result

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
    # print(f"\n Vijai table_data : {table_data}")
    if table_data:
        service_names = find_service_name(table_data, application_name)
        # print(f"\n Real service_name : {service_names}")
        # Print the result in the desired format
        # for application_name, service_data in service_names.items():
        #     print(f'\nservice_name : {application_name}: {service_data}')
              
        if service_names:
            # service_names_json = json.dumps(service_names)
            service_names_json = json.dumps(service_names, indent=2)
            print(service_names_json)
        else:
            print(f"service names not found ")    