from urllib.parse import urlparse, parse_qs
import urllib
from datetime import datetime, timedelta
import requests
import os
import subprocess
import sys

def check_num_power(num):
    return round_to_nearest_ten(int(num))

def round_to_nearest_ten(number):
    return round(number, -1)

def time_a_day_from_now():
    now = datetime.utcnow()
    future_time = now - timedelta(days=1)
    return str(future_time.strftime("%Y-%m-%dT%H:%M:%SZ"))

def time_a_week_from_now():
    now = datetime.utcnow()
    future_time = now - timedelta(weeks=1)
    return str(future_time.strftime("%Y-%m-%dT%H:%M:%SZ"))

def time_a_month_from_now():
    now = datetime.utcnow()
    future_time = now - timedelta(days=30)
    return str(future_time.strftime("%Y-%m-%dT%H:%M:%SZ"))

def time_a_year_from_now():
    now = datetime.utcnow()
    future_time = now - timedelta(days=365)
    return str(future_time.strftime("%Y-%m-%dT%H:%M:%SZ"))

def get_image_location(asset):
    # A, B and C are present
    if asset['location']['city'] and asset['location']['state'] and asset['location']['country']:
        image_location = asset['location']['city'] + ", " +  asset['location']['state'] + ", " +  asset['location']['country']
    # A and C are present
    elif asset['location']['city'] and asset['location']['country']:
        image_location = asset['location']['city'] + ", " +  asset['location']['country']
    # A and B are present
    elif asset['location']['city'] and asset['location']['state']:
        image_location = asset['location']['city'] + ", " +  asset['location']['state']
    # B and C are present
    elif asset['location']['state'] and asset['location']['country']:
        image_location = asset['location']['state'] + ", " +  asset['location']['country']
    # Only A is present
    elif asset['location']['city']:
        image_location = asset['location']['city']
    # Only B is present
    elif asset['location']['state']:
        image_location = asset['location']['state']
    # Only C is present
    elif asset['location']['country']:
        image_location = asset['location']['country']
    else:
        image_location = "NIL"
    return image_location

def parse_url(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    return query_params

def convert_date_format(date_value):
    if '-' in date_value:
        return date_value.split("-")[0][:4]+ "-" + date_value.split("-")[0][4:6] + "-" + date_value.split("-")[0][6:] + "T00:00:00Z", date_value.split("-")[1][:4]+ "-" + date_value.split("-")[1][4:6] + "-" + date_value.split("-")[1][6:] + "T23:59:59Z"
    elif date_value == '1d':
        return time_a_day_from_now(), None  # Implement time_a_day_from_now() function
    elif date_value == '1w':
        return time_a_week_from_now(), None  # Implement time_a_week_from_now() function
    elif date_value == '1m':
        return time_a_month_from_now(), None  # Implement time_a_month_from_now() function
    elif date_value == '1y':
        return time_a_year_from_now(), None # Implement time_a_year_from_now() function
    else:
        return None, None

def refactor_params(params):
    searchQueryList = ['branch', 'date', 'cocom', 'unit', 'country', 'state', 'credit', 'sort', 'type']
    refactored_params = {}
    for key, value in params.items():

        if "filter[" in key:
          key = key.replace("filter[", '').replace(']', '')
        elif "filter\\" in key:
          key = key.replace("filter\\", '').replace('[','').replace(']', '')

        if key == 'date':
            from_date, to_date = convert_date_format(value[0])
            if from_date and to_date:
                refactored_params['from_date'] = from_date
                refactored_params['to_date'] = to_date
            elif from_date:
              refactored_params['from_date'] = from_date
            else:
              refactored_params[key] = value[0]
        elif key == 'journalist':
          refactored_params['credit'] = value[0]
        elif key in searchQueryList:
            refactored_params[key] = value[0]
    return refactored_params


headers = {
    "Accept-Encoding": "gzip, deflate",
    "User-Agent": "Zend_Http_Client",
    "Accept": "application/json, text/javascript",
    "Referer": "https://api.dvidshub.net"
}

def search_dvidshub_api(search_params):
    search_params['max_results'] = 50
    search_params['fields'] = ['id']
    search_params['api_key'] = api_key
    url = "https://api.dvidshub.net/search"
    response = requests.get(url, params=search_params, headers=headers)
    try:
      return response.json()['results']
    except:
      return response.json()

def asset_dvidshub_api(id):
    params = {
    "id": id,
    "api_key": "Removed for obvious reasons 😄"
    }
    url = "https://api.dvidshub.net/asset"
    response = requests.get(url, params=params, headers=headers )
    try:
      return response.json()['results']  # Assuming the response is binary data (e.g., an image)
    except:
      return response.json()

def get_total_results(search_params):
    search_params['max_results'] = 1
    search_params['api_key'] = api_key
    url = "https://api.dvidshub.net/search"
    response = requests.get(url, params=search_params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        page_info = data.get('page_info')
        if page_info:
            total_results = page_info.get('total_results')
            return total_results
    else:
      print(response)
    return None

def convert_to_human_readable(time_str):
  try:
    # Parse the time string
    time_obj = datetime.strptime(time_str, '%Y-%d-%mT%H:%M:%S%z')

    # Format the date into a human readable string
    return str(time_obj.strftime('%B %d, %Y'))
  except ValueError:
    try:
      time_obj = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S%z')
      return str(time_obj.strftime('%B %d, %Y'))
    except ValueError:
      print("Invalid_time_string: ", time_str)
      return "Invalid time format."



# Main Logic
# Example usage:
search_results_list = []
api_key = "Removed for obvious reasons 😄"
print("****************************************************")
print("PLEASE NOTE: This scraper only works with Dvidshub search URLs. To use it, please perform a search on Dvidshub.net, applying any filters you desire. Once you have completed your search, copy the URL, start the scraper, and paste the URL here.")
print("****************************************************")
url = input("Paste your url here:> ")
print("Started Scraping...")
params = parse_url(url)
searchParamDict = refactor_params(params)
print("Getting the Total Number of data...")
totalNoData = input("How many images are you expecting (put any amount of images you want to work with if you don't know)? ")
final_no = int(totalNoData)
#print(check_num_power(totalNoData))
if int(totalNoData) > 9:
  totalNoData = check_num_power(totalNoData)
else:
  totalNoData = int(totalNoData)

print("Getting data...\nPlease be patient, your data extraction will start soon :)")
if totalNoData >= 50:
  loop_iterator = round(totalNoData/50)
else:
  loop_iterator = 1

#print(loop_iterator)

for i in range(1, loop_iterator + 2):

    searchParamDict['page'] = i
    try:
      search_results = search_dvidshub_api(searchParamDict)
    except Exception as e:
       print("The following error occurred: ", e,)
       print("Report this to Tari on Upwork @ 'https://www.upwork.com/freelancers/~01cb3c617ddbf2a8a8' ")
       input('Press any key to exit...')
       sys.exit()

    for search_result in search_results:
        search_results_list.append(search_result['id'])

current_datetime = datetime.now()
save_dir = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
os.makedirs(save_dir, exist_ok=True)



#print("Creating Excel sheet 'AllDVIDSHUBData.csv'...")
print("""
________                              __  .__
\_____  \ ______   ________________ _/  |_|__| ____   ____
 /   |   \\____ \_/ __ \_  __ \__  \\   __\  |/  _ \ /    \/
/    |    \  |_> >  ___/|  | \// __ \|  | |  (  <_> )   |  \/
\_______  /   __/ \___  >__|  (____  /__| |__|\____/|___|  /
        \/|__|        \/           \/                    \/
  _________ __                                .__  .__
 /   _____//  |________   ____ _____    _____ |  | |__| ____   ____
 \_____  \\   __\_  __ \_/ __ \\__  \  /     \|  | |  |/    \_/ __ \/
 /        \|  |  |  | \/\  ___/ / __ \|  Y Y  \  |_|  |   |  \  ___/
/_______  /|__|  |__|    \___  >____  /__|_|  /____/__|___|  /\___  >
        \/                   \/     \/      \/             \/     \/

""")



j = 0
for i in range(0, len(search_results_list)):
    #print(id)
    #asset = asset_dvidshub_api(search_results_list[i])
    #print(asset)

    try:
      asset = asset_dvidshub_api(search_results_list[i])
    except Exception as e:
       print("The following error occurred: ", e,)
       print("Report this to Tari on Upwork @ 'https://www.upwork.com/freelancers/~01cb3c617ddbf2a8a8' ")
       input('Press any key to exit...')
       sys.exit()

    if asset.get('errors') != None:
      continue

    img_download_url = asset['image']
    image_name = f"{j + 1}"
    j = j + 1
    if asset['image'][-4] == '.':
        image_name = image_name + asset['image'][-4:]
    else:
        image_name = image_name + asset['image'][-5:]

    try: #Image not found
      urllib.request.urlretrieve(img_download_url, save_dir+"//"+image_name)
    except Exception as e:
      continue


    image_location = get_image_location(asset).strip()

    if "Undisclosed Location" in image_location:
      image_location = "NIL"

    image_title = asset['title'].strip()

    if not image_title:
      image_title = "NIL"

    image_description = asset['description']

    if not image_description:
      image_description = "NIL"



    image_date = convert_to_human_readable(asset['date'])

    if image_description != "NIL":
      if image_date != "Invalid time format.":
        image_description = asset['description'].strip() + " ca. " + image_date
      else:
        image_description = asset['description'].strip()


      # OPERATION STREAMLINE LOGIC
      
      image_file_path = save_dir + "\\" + image_name

      current_directory = os.getcwd()

      exiftool_file_name = 'exiftool.exe'

      exiftool_file_path = os.path.join(current_directory, exiftool_file_name)

      exiftool_command = [
          exiftool_file_path,
          '-m',
          f'-Headline={image_description}',
          f'-Description={image_description}',
          f'-CreatorWebsite={asset["url"]}',
          f'{image_file_path}']

      process = subprocess.Popen(args=exiftool_command)

      process.wait()

      un_path = f'{image_file_path}_original'

      if os.path.exists(un_path):
          os.unlink(un_path)
      else:
        pass
        continue
        exiftool_command = [
          exiftool_file_path,
          '-m',
          f'-Headline={image_description}',
          f'-Description={image_description}',
          f'{image_file_path}']

        process = subprocess.Popen(args=exiftool_command)

        process.wait()

        un_path = f'{image_file_path}_original'

        if os.path.exists(un_path):
            os.unlink(un_path)
        else:
          pass

      print(image_name + " medadata and image " + " data has been saved to:", image_file_path)

print(f"All {final_no} plus surplus data has been scraped along with the metadata edited")
input("Press Anything to close the scraper...")
