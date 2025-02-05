from dateparser import parse as parse_date
from bs4 import BeautifulSoup
from datetime import datetime
import feedparser
import requests
import urllib

class GoogleNews:
    def __init__(self, lang = 'en', country = 'US'):
        '''
        Initialize a NewsFeed object with the specified language and country.

        Parameters:
            lang (str): The language code for the news feed. Default is 'en' (English).
            country (str): The country code for the news feed. Default is 'US' (US).

        Attributes:
            lang (str): The language code for the news feed.
            country (str): The country code for the news feed.
            BASE_URL (str): The base URL for fetching news RSS feeds.
        '''
        self.lang = lang.lower()
        self.country = country.upper()
        self.BASE_URL = 'https://news.google.com/rss'

    def __top_news_parser(self, text):
        '''
        Parse the HTML text to extract top news articles.

        Parameters:
            text (str): The HTML text of the top news section.

        Returns:
            list: A list of dictionaries, each representing a top news article with keys 'url', 'title', and 'publisher'.
        '''
        try:
            _bs4_html = BeautifulSoup(text, "html.parser")
            _lis = _bs4_html.find_all('li')
            _sub_articles = []
            for li in _lis:
                try:
                    _sub_articles.append({"url": li.a['href'], "title": li.a.text, "publisher": li.font.text})
                except:
                    pass
            return _sub_articles
        except:
            return text

    def __ceid(self):
        '''
        Generate the ceid parameter for the URL.

        Returns:
            str: The ceid parameter containing country and language information.
        '''
        return '?ceid={}:{}&hl={}&gl={}'.format(self.country,self.lang,self.lang,self.country)

    def __add_sub_articles(self, entries):
        '''
        Add sub-articles to the news entries if available.

        This method adds sub-articles to the news entries in the provided list, if a 'summary' key is present in the entry dictionary. Sub-articles are parsed using the __top_news_parser method.

        Parameters:
            entries (list): A list of dictionaries representing news entries.

        Returns:
            list: A modified list of news entries with sub-articles added.
        '''
        for i, val in enumerate(entries):
            if 'summary' in entries[i].keys():
                entries[i]['sub_articles'] = self.__top_news_parser(entries[i]['summary'])
            else:
                entries[i]['sub_articles'] = None
        return entries

    def __parse_feed(self, feed_url):
        '''
        Parse the RSS feed from the provided URL.

        This method sends a GET request to the provided feed URL, parses the response using the feedparser library, and extracts relevant information including feed metadata and entries.

        Parameters:
            feed_url (str): The URL of the RSS feed to be parsed.

        Returns:
            dict: A dictionary containing feed metadata and entries.

        Raises:
            Exception: If the provided feed URL is not available.
        '''
        _r = requests.get(feed_url)

        if 'https://news.google.com/rss/unsupported' in _r.url:
            raise Exception('This feed is not available')

        _d = feedparser.parse(_r.text)

        if len(_d['entries']) == 0:
            _d = feedparser.parse(feed_url)

        return dict((k, _d[k]) for k in ('feed', 'entries'))

    def __search_helper(self, query):
        '''
        Encode the search query for use in URL.

        This method encodes the provided search query using urllib.parse.quote_plus to prepare it for use in a URL.

        Parameters:
            query (str): The search query to be encoded.

        Returns:
            str: The encoded search query.
        '''
        return urllib.parse.quote_plus(query)

    def __from_to_helper(self, validate=None):
        '''
        Format the date for use in URL.

        This method parses the provided date string using parse_date and formats it as 'YYYY-MM-DD' for use in a URL.

        Parameters:
            validate (str): The date string to be formatted. If None, the current date is used.

        Returns:
            str: The formatted date.

        Raises:
            Exception: If the provided date string cannot be parsed.
        '''
        try:
            validate = parse_date(validate).strftime('%Y-%m-%d')
            return str(validate)
        except:
            raise Exception('Could not parse your date')
        
    def __create_news_list(self, query, data):
        '''
        Create a list of news items from the provided data.

        Parameters:
            data (dict): A dictionary containing news data.

        Returns:
            list: A list of news items, each represented as a list containing the title, source URL, and link URL.
        '''
        _list = []
        _temp_list = []

        for i,j in enumerate(data['entries']):
            _date_format = datetime.strptime(data['entries'][i]['published'], "%a, %d %b %Y %H:%M:%S %Z")
            _date_format.strftime("%d/%m/%Y %H:%M:%S")
            _title = data['entries'][i]['title'].rsplit(' - ',1)[0].strip()
            _temp_list.append(_title)
            _temp_list.append(str(_date_format))
            _temp_list.append(query)
            _temp_list.append(data['entries'][i]['source']['href'])
            _temp_list.append(data['entries'][i]['links'][0]['href'])
            _list.append(_temp_list.copy())
            _temp_list.clear()

        return _list

    def search(self, query: str, search: str,helper = True, when = None, from_ = None, to_ = None):
        '''
        Search for news articles based on the provided query.

        This method constructs a search query based on the parameters provided, including the search query itself, optional time constraints ('when', 'from_', 'to_'), and whether to encode the query for URL ('helper').

        Parameters:
            query (str): The search query.
            helper (bool): Whether to encode the query for use in URL. Default is True.
            when (str): Optional time constraint for the search query.
            from_ (str): Optional start date for the time constraint.
            to_ (str): Optional end date for the time constraint.

        Returns:
            dict: A dictionary containing search results, including feed metadata and entries.
        '''
        if when:
            query += ' when:' + when

        if from_ and not when:
            from_ = self.__from_to_helper(validate=from_)
            query += ' after:' + from_

        if to_ and not when:
            to_ = self.__from_to_helper(validate=to_)
            query += ' before:' + to_

        if helper == True:
            query = self.__search_helper(query)

        _search_ceid = self.__ceid()
        _search_ceid = _search_ceid.replace('?', '&')

        _d = self.__parse_feed(self.BASE_URL + '/search?q={}'.format(query) + _search_ceid)
        _d['entries'] = self.__add_sub_articles(_d['entries'])
        _list = self.__create_news_list(search,_d)
        return _list