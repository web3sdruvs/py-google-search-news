'''
News Web Scraping

Description:
This script performs news extraction using web scraping based on the search terms defined in the config.ini file.

Reference:
- The pygooglenews library from https://github.com/kotartemiy/pygooglenews was used as a reference in this project for copying the googlenews.py package. It is distributed under the MIT license.

Requirements:
- feedparser, BeautifulSoup, urllib, dateparser, requests, configparser, json, time, logging, openpyxl, and datetime

Usage:
- Before running the script, make sure to properly configure the search terms and exclusion words in the 'config.ini' file.
'''
from logging import info, error, basicConfig, INFO
from googlesearch import GoogleSearch
from googlenews import GoogleNews
from export import save_file
from config import Config
from pathlib import Path
from time import sleep
from sys import exit
import os

basicConfig(level=INFO, format='%(asctime)s - %(levelname)s - %(message)s')
info(f'Execution now')
info(f'Create file config: ConfigFile().get_file_config()')
config_file = 'config.ini'
config = Config(config_file)
value_black_list = config.get_black_list().split(',')
value_search = config.get_search().encode('latin-1').decode('utf-8').split(',')
value_exclude = config.get_exclude().encode('latin-1').decode('utf-8').split(',')
value_exclude.extend(value_black_list)
value_filter_period = config.get_period()
info(f'Start is script')

def dict_for_join(list, index=1):
  '''
  Creates a dictionary from a list of tuples, using the first element of each tuple as the key
  and the element at the specified index as the value.

  Args:
      lst (list): The list of tuples to convert into a dictionary.
      index (int, optional): The index of the element to be used as the value in the resulting dictionary.
          Defaults to 1.

  Returns:
      dict: A dictionary where keys are the first elements of tuples in the list, and values are
          the elements at the specified index.
  '''
  _dict_list = {_i[0]: _i[index] for _i in list}
  return _dict_list

def list_left_join(list, dict):
  '''
  Performs a left join operation on a list of tuples and a dictionary, appending values from the dictionary
  corresponding to the keys found in the tuples.

  Args:
      lst (list): The list of tuples to be joined with the dictionary.
      dictionary (dict): The dictionary to join with the list of tuples.

  Returns:
      list: A new list of tuples where each tuple from the original list is extended with a value
          from the dictionary corresponding to the key in the tuple. If the key is not found in the
          dictionary, None is appended.
  '''
  _list = [_i + [dict.get(_i[0], 'Not found')] for _i in list]
  return _list

def filter_contains_keyword(data):
    '''
    Check if the list of excluded keywords is not present in any of the items in the data list.

    Args:
        data (list): A list of strings to be checked.

    Returns:
        bool: True if none of the excluded keywords are found in any item of the data list, False otherwise.
    '''
    for _i in value_exclude:
        for _j in data:
          if _i in _j:
              return False
    return True

def filter_contains_duplicate(data):
  '''
  Filters out duplicate elements from a list of lists.

  Args:
  - data (list): The input list containing lists of elements.

  Returns:
  - list: A list with duplicate elements removed.
  '''
  _without_duplicate_list = list(map(tuple, data))
  _without_duplicate_list = list(set(_without_duplicate_list))
  _without_duplicate_list = list(map(list, _without_duplicate_list))
  return _without_duplicate_list

all_news_list = []
all_news_desc_list = []
retries = paused = count_value_search = 0

while retries < 5:
  retries += 1
  paused = 2 ** retries
  try:
    while True:
      info(f'Search now is: {value_search[count_value_search]}')
      desc_list = GoogleSearch().search(value_search[count_value_search], 'qdr:m')
      all_news_desc_list.extend(desc_list)
      news_list = GoogleNews().search(f'{value_search[count_value_search]} when:{value_filter_period}d',value_search[count_value_search])
      all_news_list.extend(news_list)
      sleep(0.500)
      retries = 0 #resets effort for each term successfully searched
      if len(value_search) == count_value_search + 1:
        break
      count_value_search += 1
    break
  except Exception as e:
    error(f'Retries in {paused} seconds -> {e}')
    sleep(paused)

all_news_desc_list = filter_contains_duplicate(all_news_desc_list)
all_news_desc_list = list(filter(filter_contains_keyword, all_news_desc_list))
desc_news_desc_dict = dict_for_join(all_news_desc_list, 1)
url_news_desc_dict = dict_for_join(all_news_desc_list, 2)
all_news_list = list_left_join(all_news_list, desc_news_desc_dict)
all_news_list = list_left_join(all_news_list, url_news_desc_dict)
all_news_list = list(filter(filter_contains_keyword, all_news_list))
save_file(all_news_list, type='xlsx')