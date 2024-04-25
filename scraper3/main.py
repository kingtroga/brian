from urllib.parse import urlparse, parse_qs
import urllib
from datetime import datetime, timedelta
import requests
import os
import subprocess
import sys
import re 

def has_open_access(string):
    pattern = r'\bopenAccess\b'
    if re.search(pattern, string):
        return True
    else:
        return False

def has_highlights(string):
    pattern = r'\bhighlights\b'
    if re.search(pattern, string):
        return True
    else:
        return False

def has_image(string):
    pattern = r'\bwithImage\b'
    if re.search(pattern, string):
        return True
    else:
        return False


#TEST URL(s)
""" url = "https://www.metmuseum.org/art/collection/search?searchField=All&showOnly=openAccess%7CwithImage&sortBy=relevance&era=A.D.+1800-1900"
url2 = "https://www.metmuseum.org/art/collection/search?searchField=ArtistCulture&showOnly=openAccess%7CwithImage&sortBy=relevance&era=A.D.+1800-1900&q=Money"
url3 = "https://www.metmuseum.org/art/collection/search?searchField=Gallery&showOnly=openAccess%7CwithImage&sortBy=relevance&q=Money"
url4 = "https://www.metmuseum.org/art/collection/search?showOnly=openAccess%7CwithImage%7Chighlights&sortBy=relevance&q=Money"
url5 = "https://www.metmuseum.org/art/collection/search?showOnly=openAccess%7CwithImage%7Chighlights&sortBy=relevance&q=Money&material=Brass"
url6 = "https://www.metmuseum.org/art/collection/search?showOnly=openAccess%7CwithImage%7Chighlights&sortBy=relevance&q=Money&geolocation=Africa"
url7 = "https://www.metmuseum.org/art/collection/search?showOnly=openAccess%7CwithImage%7Chighlights&sortBy=relevance&era=A.D.+1800-1900&q=Money"
url8 = "https://www.metmuseum.org/art/collection/search?showOnly=openAccess%7CwithImage%7Chighlights&sortBy=relevance&era=A.D.+1800-1900&department=1"
url9 = "https://www.metmuseum.org/art/collection/search?showOnly=openAccess%7CwithImage%7Chighlights&sortBy=relevance&material=Aerophones%7CAlto"
url10 = "https://www.metmuseum.org/art/collection/search?showOnly=openAccess%7CwithImage%7Chighlights&sortBy=relevance&era=A.D.+1800-1900"
url11 = "https://www.metmuseum.org/art/collection/search?showOnly=openAccess%7CwithImage%7Chighlights&sortBy=relevance&era=A.D.+1600-1800"
url12 = "https://www.metmuseum.org/art/collection/search?showOnly=openAccess%7CwithImage%7Chighlights&sortBy=relevance&era=A.D.+1400-1600"
url13 = "https://www.metmuseum.org/art/collection/search?showOnly=openAccess%7CwithImage%7Chighlights&sortBy=relevance&era=A.D.+1000-1400"
url14 = "https://www.metmuseum.org/art/collection/search?showOnly=openAccess%7CwithImage%7Chighlights&sortBy=relevance&era=1000+B.C.-A.D.+1"
url15 = "https://www.metmuseum.org/art/collection/search?showOnly=openAccess%7CwithImage%7Chighlights&sortBy=relevance&era=A.D.+500-1000"
url16 = "https://www.metmuseum.org/art/collection/search?showOnly=openAccess%7CwithImage%7Chighlights&sortBy=relevance&era=2000-1000+B.C."
url17 = "https://www.metmuseum.org/art/collection/search?showOnly=openAccess%7CwithImage%7Chighlights&sortBy=relevance&era=A.D.+1-500"
url18 = "https://www.metmuseum.org/art/collection/search?showOnly=openAccess%7CwithImage%7Chighlights&sortBy=relevance&era=A.D.+1900-present"
url19 = "https://www.metmuseum.org/art/collection/search?showOnly=openAccess%7CwithImage%7Chighlights&sortBy=relevance&era=8000-2000+B.C."
brain_url = "https://www.metmuseum.org/art/collection/search?searchField=All&showOnly=openAccess%7CwithImage&sortBy=relevance&era=A.D.+1800-1900"
 """
# RULE 1:
# When 'searchField' == ['All'] and no q is given then api_url = "https://collectionapi.metmuseum.org/public/collection/v1/search?q=*" + additional items

# RULE 2:
# When 'searchField' == ['ArtistCulture'] then api_url = "https://collectionapi.metmuseum.org/public/collection/v1/search?artistOrCulture=true&q=*" + additional items

# RULE 3:
# When 'searchField' == ['Gallery'] then api_url = "https://collectionapi.metmuseum.org/public/collection/v1/search?isOnView=true&q=*" plus additionally items

# RULE 4:
# when 'openAccess' in 'showOnly'[0] allow the scraper to work if not don't allow it to work use REGEX/chatgpt

# RULE 5:
# when 'highlights' in 'showOnly'[0] then api_url = "https://collectionapi.metmuseum.org/public/collection/v1/search?isHighlight=true&q=*"

# RULE 6:
# when 'material' = ['Material'] then api_url = "https://collectionapi.metmuseum.org/public/collection/v1/search?q=*&medium='Material'"

# RULE 7:
# when 'geolocation' = ['Place'] then api_url = "https://collectionapi.metmuseum.org/public/collection/v1/search?geoLocation=France&q=*"

# RULE 8:
# when 'era' = ['era' ] then api_url = "https://collectionapi.metmuseum.org/public/collection/v1/search?dateBegin=eraBegin&dateEnd=eraEnd&q=*"

# RULE 9:
# when 'department' = ['1'] then find the department website then api_url = "https://collectionapi.metmuseum.org/public/collection/v1/search?dateBegin=eraBegin&dateEnd=eraEnd&q=*"

departments =  {
     1 : "American Decorative Arts",
     3 : "Ancient Near Eastern Art",
     4 : "Arms and Armor",
     5 : "Arts of Africa, Oceania, and the Americas",
     6 : "Asian Art",
     7 : "The Cloisters",
     8 : "The Costume Institute",
     9 : "Drawings and Prints",
     10 : "Egyptian Art",
     11 : "European Paintings",
     12 : "European Sculpture and Decorative Arts",
     13 : "Greek and Roman Art",
     14 : "Islamic Art",
     15 : "The Robert Lehman Collection",
     16 : "The Libraries",
     17 : "Medieval Art",
     18 : "Musical Instruments",
     19 : "Photographs",
     21 : "Modern Art",
}

eras = {
    'A.D. 1800-1900' : [1800, 1900],
    'A.D. 1600-1800' : [1600, 1800],
    'A.D. 1400-1600' : [1400, 1600],
    'A.D. 1000-1400' : [1000, 1400],
    '1000 B.C.-A.D. 1' : [-1000, 1],
    'A.D. 500-1000': [500, 1000],
    '2000-1000 B.C.': [-2000, -1000],
    'A.D. 1-500': [1, 500],
    'A.D. 1900-present': [1900, datetime.now().year],
    '8000-2000 B.C.': [-8000, -2000],
}



def parse_url(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    return query_params

def refactor_params(params):
    refactored_params = {}
    for key, value in params.items():
        #print(key, value)

        if key == 'showOnly' and has_open_access(str(value[0])) == False:
            return "NULL"
        if key == 'showOnly' and has_highlights(str(value[0])):
            refactored_params['isHighlight'] = 'true'


        if key == 'searchField' and str(value[0]) == 'All' and params.get('q') == None:
            refactored_params['q'] = '*'
        if key == 'searchField' and str(value[0]) == 'ArtistCulture':
            refactored_params['artistOrCulture'] = 'true'
        if key == 'searchField' and str(value[0]) == 'Gallery':
            refactored_params['isOnView'] = 'true'
        if params.get('searchField') == None and params.get('q') == None:
            refactored_params['q'] = '*'
        if params.get('q') == None:
            refactored_params['q'] = '*'



        if key == 'q':
            refactored_params['q'] = str(value[0])

        if key == 'material':
            refactored_params['medium'] = str(value[0])
        
        if key == 'geolocation':
            refactored_params['geolocation'] = str(value[0])

        if key == 'era':
            date = eras[str(value[0])]
            #dateBegin=1700&dateEnd=1800
            refactored_params['dateBegin'] = date[0]
            refactored_params['dateEnd'] = date[1]

        if key == 'department':
            refactored_params['departmentId'] = str(value[0])

            
    return refactored_params

headers = {
    "Accept-Encoding": "gzip, deflate",
    "User-Agent": "Zend_Http_Client",
    "Accept": "application/json, text/javascript",
    "Referer": "https://collectionapi.metmuseum.org"
}

def search_met_api(search_params):
    url = "https://collectionapi.metmuseum.org/public/collection/v1/search"
    response = requests.get(url, params=search_params, headers=headers)
    #print(response.json()['objectIDs'])
    print(f"Total results found {response.json()['total']}. NOTE: Not all these results have images so the scraper might take a little bit more time to filter through them")
    return response.json()['objectIDs']
    """ try:
      return response.json()['results']
    except:
      return response.json() """

def asset_met_api(objectID):
    url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{objectID}"
    response = requests.get(url)
    #print(response.json())
    return response.json()
    """ try:
      return response.json()['results']  # Assuming the response is binary data (e.g., an image)
    except:
      return response.json() """
    

# SCRAPER LOGIC
print("****************************************************")
print("PLEASE NOTE: This scraper only works with Met Musuem search URLs. To use it, please perform a search on https://www.metmuseum.org/art/collection/search , applying any filters you desire. Once you have completed your search, copy the URL, start the scraper, and paste the URL here.")
print("****************************************************")
url = input("Paste your url here:> ")
print("Started Scraping...")
search_params = refactor_params(parse_url(url))
objectIDs = search_met_api(search_params)

current_datetime = datetime.now()
save_dir = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
os.makedirs(save_dir, exist_ok=True)

j = 0
for objectID in objectIDs:
    asset = asset_met_api(objectID)
    #"{title} ; {artist} ; Medium {medium}  Culture {culture} Publisher {publisher} Date {date}"
    title = None
    artist = None
    medium = None
    culture = None
    publisher = None
    date = None

    if asset.get('primaryImage'):
        img_download_url = asset['primaryImage']
        image_name = f"{j + 1}"
        j = j + 1
        if asset['primaryImage'][-4] == '.':
            image_name = image_name + asset['primaryImage'][-4:]
        else:
            image_name = image_name + asset['primaryImage'][-5:]

        try: #Image not found
            urllib.request.urlretrieve(img_download_url, save_dir+"//"+image_name)
        except Exception as e:
            continue
    else:
        continue

    if asset.get('title'):
        title = str(asset['title']) + " ;"
        #print(title)

    if asset.get('artistDisplayName'):
        artist = str(asset['artistDisplayName']) + " ;"
        #print(artist)

    if asset.get('medium'):
        medium = "Medium " + str(asset['medium'])
        #print(medium)

    if asset.get('culture'):
        culture = "Culture " + str(asset['culture'])
        #print(culture)
    

    if asset.get('constituents'):
        constituents = asset['constituents']

        for constituent in constituents:
            if str(constituent["role"]) == "Publisher":
                publisher = "Publisher " + str(constituent['name'])
                #print(publisher)
    
                break
    
        
    if asset.get('objectDate'):
        date = "Date " + str(asset['objectDate'])
        #print(date)



    variables = ['title', 'artist', 'medium', 'culture', 'publisher', 'date']
    values = [title, artist, medium, culture, publisher, date]

    # Filter out null values
    filtered_values = [val for var, val in zip(variables, values) if val is not None]

    # Join the non-null values into a string
    image_description = ' '.join(filtered_values)

    print(image_description)

    image_file_path = save_dir + "\\" + image_name

    current_directory = os.getcwd()

    exiftool_file_name = 'exiftool.exe'

    exiftool_file_path = os.path.join(current_directory, exiftool_file_name)

    exiftool_command = [
        exiftool_file_path,
        '-m',
        '-L',
        f'-Headline={image_description}',
        f'-Description={image_description}',
        f'-CreatorWebsite={asset["objectURL"]}',
        f'{image_file_path}']

    process = subprocess.Popen(args=exiftool_command)

    process.wait()

    un_path = f'{image_file_path}_original'

    if os.path.exists(un_path):
        os.unlink(un_path)
    else:
        pass
        continue
print(f"All data has been scraped along with the metadata edited")
input("Press Anything to close the scraper...")