from bs4 import BeautifulSoup
from time import sleep
import urllib.parse
import requests

class GoogleSearch:
  def __init__(self):
    '''
    Initializes the WebScraper object.

    Attributes:
    - BASE_URL (str): The base URL for performing web searches.
    - HEADER (dict): The header containing user agent and other necessary information for making HTTP requests.
    '''
    self.BASE_URL = 'https://www.google.com/search'
    self.HEADER = {
          'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'Accept-Language': 'en-US,en;q=0.5',
          'Accept-Encoding': 'gzip, deflate',
          'Upgrade-Insecure-Requests': '1'
    }
    
  def __pages(self, query, tbs, _first_page=True):
    '''
    Retrieves search results from Google for multiple pages.

    Args:
    - query (str): The search query.
    - tbs (str): Time-based search parameter.

    Returns:
    - list: A list containing search results, where each result is a list with the title, description, and URL.
    '''
    _all_google_search_list = []
    _tmp_all_google_search_list = []
    _page = 0

    while True:
      _html_content = self.__top_search_parser(query, tbs, _page)     
      sleep(0.700)

      if len(_html_content) == 0:
        break
     
      for i in _html_content:
        _title = i.h3.text
        _desc = i.find(class_="BNeawe s3v9rd AP7Wnd").text
        _href = i.get('href')
        _parsed_href = urllib.parse.urlparse(_href)
        _real_url = urllib.parse.parse_qs(_parsed_href.query)['url'][0] if 'url' in urllib.parse.parse_qs(_parsed_href.query) else ''
        _tmp_all_google_search_list.append(_title)
        _tmp_all_google_search_list.append(_desc)
        _tmp_all_google_search_list.append(_real_url)
        _all_google_search_list.append(_tmp_all_google_search_list.copy())
        _tmp_all_google_search_list.clear()
        
      if _first_page:
        break

      _page += 10

    return _all_google_search_list

  def __top_search_parser(self, query, tbs, _page=0):
    '''
    Parses search results from the top search engine page.

    Args:
    - query (str): The search query.
    - tbs (str): Time-based search parameter.
    - _page (int, optional): Page number to start parsing from. Defaults to 0.

    Returns:
    - list: A list of BeautifulSoup elements containing search result links.
    '''
    _params = {
          "q":query,
          "tbm":"nws",
          "tbs":tbs,
          "start": _page,
          "hl": "en",
          "gl": "US"  
    }
    try:
      _text = requests.get(self.BASE_URL, headers = self.HEADER, params = _params)
      _text = _text.content
      _bs4_html = BeautifulSoup(_text, "html.parser")
      _a = _bs4_html.find_all('a', attrs={'data-ved': True})
    except Exception as _e:
      print(f'Error: {_e}')
      _a = list()
    return _a
  
  def search(self, query:str, tbs):
    '''
    Performs a search query on Google.

    Args:
    - query (str): The search query.
    - tbs (str): Time-based search parameter.

    Returns:
    - list: A list containing search results, where each result is a list with the title, description, and URL.
    '''
    query = query.replace(' ', '+').lower()
    if query is not None:
      _lista = self.__pages(query, tbs)
      return _lista
    else:
      print('Error query is None')
      return