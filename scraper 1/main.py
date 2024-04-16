import requests
import pandas as pd
from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse, parse_qs
import urllib
from PIL import Image
from io import BytesIO
import os
from datetime import datetime
import time
import warnings
from bs4.builder import XMLParsedAsHTMLWarning
import warnings
warnings.filterwarnings('ignore', category=XMLParsedAsHTMLWarning)



Image.MAX_IMAGE_PIXELS = None

access_token = "I removed the access token for obvious reasons 😄"



def round_to_nearest_thousand(number):
    # Divide the number by 1000, round it to the nearest integer, and multiply by 1000
    rounded_number = round(number / 1000) * 1000
    return rounded_number

def round_to_nearest_hundred(number):
    # Divide the number by 100, round it to the nearest integer, and multiply by 100
    rounded_number = round(number / 100) * 100
    return rounded_number

def get_number_of_articles(url):
  headers = {
    "Authorization": f"Bearer {access_token}",
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
  }
  response = requests.get(url=url, headers=headers)
  soup = bs(response.text, 'html.parser')
  results_info_div = soup.find('div', class_='results-info')
  try:
    strong_tags = results_info_div.find_all('strong')
  except:
    try:
      noOfArticles = int(input("Sorry Human 🤖, I'm  unable to get the number of articles from the page. Pls tell me the number of articles:> "))
      return noOfArticles
    except ValueError:
      noOfArticles = int(input("Sorry Human 🤖, Pls tell me the number of articles without the Comma, Decimal Point, or any other Punctation:> "))
      return noOfArticles


  noOfArticles = str(strong_tags[1].text).replace(',','')
  if len(noOfArticles) > 3:
    noOfArticles = round_to_nearest_thousand(int(noOfArticles))
  if 3 > len(str(noOfArticles)) > 2:
    noOfArticles = round_to_nearest_hundred(int(noOfArticles))

  return(str(noOfArticles))

def get_list_of_articles(search_params):
   headers = {
    "Authorization": f"Bearer {access_token}",
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
  }
   articles = []
   commons_api_url = "https://commons.wikimedia.org/w/api.php"
   response = requests.get(url=commons_api_url, params=search_params, headers=headers)

   if response.status_code == 200:
      search_results = response.json()
      #print(search_results)
      try:
        search_results = search_results['query']['search']
        for result in search_results:
          articles.append(result['title'])
      except Exception as e:
        return "coco"
      return articles
   else:
      return [f'{response.status_code}']

def get_main_list(no_of_articles, search_params): # 10,000 requests with get_list_of_articles
  main_list = []
  coco = 0
  loop_iterator = round(int(no_of_articles)/ 500)# single request limit is 500
  for i in range(0, loop_iterator+1):
    search_params['sroffset'] = coco
    loop_list = get_list_of_articles(search_params=search_params)
    if loop_list != "coco":
      for article in loop_list:
        main_list.append(article)
      coco = coco + 500
  main_list = main_list[0: int(no_of_articles)]
  return main_list

def get_excel_data(image_url):
    response = requests.get(url=image_url)
    soup = bs(response.content, 'html.parser')
    description = ""
    source = ""
    date = ""
    place = ""
    table_data = soup.find('table', class_='fileinfotpl-type-information')

    # Error handling
    if table_data is None:
        table_data = soup.find('table', class_='fileinfotpl-type-artwork')

    try:
        table_rows = table_data.find_all('tr')
        for table_row in table_rows:
            # Description
            if table_row.find('td', id="fileinfotpl_desc"):
                try:
                    description = table_row.find('div', class_="en").text.encode('utf-8').decode('utf-8')
                except:
                    description = table_row.find('td', id="fileinfotpl_desc").find_next_sibling().text.encode('utf-8').decode('utf-8')
            # Date
            elif table_row.find('td', id="fileinfotpl_date"):
                date = table_row.find('td', id="fileinfotpl_date").find_next_sibling().text.encode('utf-8').decode('utf-8')
            # Source
            elif table_row.find('td', id='fileinfotpl_src'):
                source = table_row.find('td', id='fileinfotpl_src').find_next_sibling().text.replace('\n', '').encode('utf-8').decode('utf-8')

    except:
        table_data = soup.find('table', class_="wikitable filehistory")
        try:
            table_rows = table_data.find_all('tr')
        except AttributeError:
            return None, None, None, None
        needed_data = table_rows[1].find_all('td')

        description = needed_data[-1].text.encode('utf-8').decode('utf-8')
        date = needed_data[1].text.encode('utf-8').decode('utf-8')

    # Place

    all_divs = soup.find_all('div', class_="description en")
    try:
        i_tag = all_divs[0].find('i')
    except:
        i_tag = None
    try:
        place = i_tag.find_all('a')[1].text.encode('utf-8').decode('utf-8')
    except:
        place = ''

    description = description.strip()
    source = source.strip()
    date = date.strip()
    place = place.strip()

    return description, place, date, source

def get_image_download_url(article_title):
    headers = {
    "Authorization": f"Bearer {access_token}",
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
  }
    # Replace spaces with underscores in the article title
    formatted_title = article_title.replace(' ', '_')

    # Define the URL
    url = f"https://commons.wikimedia.org/w/api.php?action=query&format=xml" + \
        f"&prop=imageinfo&iiprop=url&titles=File:{formatted_title}"

    # Make the request
    response = requests.get(url=url, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the XML response
        soup = bs(response.text,'lxml')
        # Find the URL attribute in the ii tag
        try:
          image_url = soup.find('ii')['url']
        except:
          image_url = None
        return image_url
    else:
        # Print an error message if the request failed
        print("Error:", response.status_code)
        return None

def get_main_image(wiki_link,article, save_dir, IMAGE_NUM):
  headers = {
    "Authorization": f"Bearer {access_token}",
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
  }
  Image.MAX_IMAGE_PIXELS = None
  cleanArticleName = article.replace(" ", "_").replace("File:", "")
  image_url = wiki_link + article.replace(" ", "_")  # this is actually an img description url
  image_name = str(IMAGE_NUM + 1)
  time.sleep(0.5)
  response = requests.get(url = image_url, headers = headers)
  soup = bs(response.text, 'html.parser')
  img_download_url = get_image_download_url(cleanArticleName)
  

  if img_download_url:
    try:
      image_name = image_name + img_download_url[-4:]
      urllib.request.urlretrieve(img_download_url, save_dir+"//"+image_name)
    except Exception as e:
      try:
        image_name = image_name + img_download_url[-5:]
        urllib.request.urlretrieve(img_download_url, save_dir+"//"+image_name)
      except Exception as e:
        image_name = ""

  description , place, date, source = get_excel_data(image_url)
  return image_url, image_name, description , place, date, source

def parse_wikimedia_url(url):
    parsed_url = urlparse(url)

    query_params = parse_qs(parsed_url.query)
    if not parsed_url.query: #is it a search link or one link
      return None, None

    # Extract search query
    search_query = query_params.get('search', [''])[0]

    # Extract namespaces
    namespaces = []
    for key, value in query_params.items():
        if key.startswith('ns') and value == ['1']:
            namespaces.append(key)



    search_params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": search_query,
        "srlimit": '500',  # Default limit to 500 if not provided
        "srnamespace": "|".join(namespaces),
    }

    return search_params, get_number_of_articles(url)


# MAIN APP LOGIC
columns = ['url','title', 'description', 'source', 'place', 'depicted place', 'image_name']
df = pd.DataFrame(columns=columns)


url_scraped = input("Paste your link here:> ")
print("Please wait...")
search_params, no_of_articles = parse_wikimedia_url(url_scraped)
current_datetime = datetime.now()
save_dir = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")



if search_params:
  main_list = get_main_list(no_of_articles, search_params)
  wiki_link = "https://commons.wikimedia.org/wiki/"
  save_dir = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
  os.makedirs(save_dir, exist_ok=True)

  for article in range(0, len(main_list)):
    image_url, image_name, description , place, date, source= get_main_image(wiki_link, main_list[article], save_dir, article)
    print("Scraping " + image_url +" ....")
    try:
      description = description.replace('English:', '') + " ca. " + date.replace('\n', ' ')
    except:
      description = ""


    new_row =  {'url': image_url,
      'title': main_list[article][5:],
      'description': description,
      'source': source,
      'place': place,
      'depicted place': place,
      'image_name': image_name}

    df = df._append(new_row, ignore_index=True)
    csv_file_path = f"{save_dir}/AllWikiData.csv"
    try:
        df.to_csv(csv_file_path, index=False)
        print(image_url + " data has been saved to:", csv_file_path)
    except PermissionError:
        print("Please close the 'AllWikiData.csv' file and Restart the scraper. You can't use the scraper and have 'AllWikiData.csv' open simultaneously")
else:
  wiki_link = "https://commons.wikimedia.org/wiki/"
  save_dir = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
  os.makedirs(save_dir, exist_ok=True)

  image_url = url_scraped
  print("Scraping " + image_url +" ....")
  url_parsed = urlparse(image_url)
  article = url_parsed[2][6:]

  image_url, image_name = get_main_image(wiki_link, article, save_dir, 1)
  description , place, date, source = get_excel_data(image_url)
  if description != None:

    try:
      description = description.replace('English:', '') + " ca. " + date.replace('\n', ' ')
    except:
      description = ""
    new_row =  {'url': image_url,
        'title': article[5:],
        'description': description,
        'source': source,
        'place': place,
        'depicted place': place,
        'image_name': image_name}

    df = df._append(new_row, ignore_index=True)
    csv_file_path = f"{save_dir}/AllWikiData.csv"
    try:
        df.to_csv(csv_file_path, index=False)
        print(image_url + " data has been saved to:", csv_file_path)
    except PermissionError:
        print("Please close the 'AllWikiData.csv' file and Restart the scraper. You can't use the scraper and have 'AllWikiData.csv' open simultaneously")
  else:
    print("Invalid Link, Please check the link and restart the scraper!")

