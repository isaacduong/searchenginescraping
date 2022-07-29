import requests
import json

from utils.proxy import renew_proxy
from fake_useragent import UserAgent
import logging

logging.basicConfig(level=logging.INFO)


class AuCoScraper(object):
    """python class to retrieve amazon, google and ebay autocomplete search engines"""

    def __init__(self):

        self.headers = {"User-agent": UserAgent().random}
        self.AMZ_URL = "https://completion.amazon.com/api/2017/suggestions?limit=11&prefix=%s&suggestion-type=WIDGET&suggestion-type=KEYWORD&page-type=Gateway&alias=aps&site-variant=desktop&version=3&event=onKeyPress&wc=&lop=en_US&fb=1&session-id=143-4895932-0278113&request-id=TB3SH3MPVR7626HQE0Y4&mid=ATVPDKIKX0DER&plain-mid=1&client-info=amazon-search-ui"
        self.GOOGLE_URL = "https://clients1.google.com/complete/search"  # ?client=youtube&hl=en&gl=sg&gs_rn=64&gs_ri=youtube&tok=h3yTGb1h3-yuCBwsAaQpxQ&ds=yt&cp=3&gs_id=2u&q=jaz&callback=google.sbox.p50&gs_gbg=0l0MjG05RWnWBe9WcipQbsy'
        self.EBAY_URL = "https://www.ebay.com/autosug?kwd=%s&_jgr=1&sId=%s&_ch=0&_store=1&_help=1&callback=0"

    def lookup_amz_keywords(self, seed_keyword: str):
        """
        this function returns a list of keywords that are most searched for by amazon customers based on the seed keyword
        Parameters
        ----------
        seed_keyword: keyword to be used to look up in the autocomplete search engine for suggesting keywords

        Returns
        -------
        list containing the keywords generated from the amazon autocomplete search engine

        """

        response = requests.get(
            self.AMZ_URL % seed_keyword,
            headers=self.headers,
            proxies=renew_proxy(),
            timeout=10,
        )

        if response.status_code == 200:
            suggestedSearches = json.loads(response.text)["suggestions"]
            keyword_list = []
            for s in suggestedSearches:
                keyword_list.append(s["value"])

            return list(set(keyword_list))
        else:
            return []

    def lookup_ebay_keywords(self, seed_keyword: str, geo: str = "US"):
        """
        this function returns a list of keywords that are most searched for by ebay customers based on the seed keyword
        Parameters
        ----------
        seed_keyword: keyword to be used to look up in the autocomplete search engine for suggesting keywords
        geo: abbreviation of country name to be used to look up in the autocomplete search engine

        Returns
        -------
        list containing the keywords generated from ebay autocomplete search engine

        """
        countrycode = {
            "US": 0,
            "DE": 77,
            "FR": 71,
            "UK": 3,
            "CA": 2,
            "ES": 186,
            "IT": 101,
            "us": 0,
            "de": 77,
            "fr": 71,
            "uk": 3,
            "ca": 2,
            "es": 186,
            "it": 101,
        }

        response = requests.get(
            self.EBAY_URL % (seed_keyword, countrycode.get(geo, 0)),
            proxies=renew_proxy(),
            timeout=10,
        )
        if response.status_code == 200:

            suggestedSearches = json.loads(response.text)["res"]["sug"]
            return suggestedSearches
        else:
            return []

    # https://www.google.de/complete/search?q=ch&cp=2&client=gws-wiz&xssi=t&hl=en-AT&authuser=0&psi=ug9QYvOVJbmVxc8Pj-eD2AM.1649414074771&pq=youtube%20auto%20suggestion&dpr=2
    # http://suggestqueries.google.com/complete/search?client=firefox&hl=en&gl=DE&ds=sh&q=massage
    # https://clients1.google.com/complete/search?client=youtube&hl=en&gl=sg&gs_rn=64&gs_ri=youtube&tok=h3yTGb1h3-yuCBwsAaQpxQ&ds=yt&cp=3&gs_id=2u&q=jaz&callback=google.sbox.p50&gs_gbg=0l0MjG05RWnWBe9WcipQbsy
    def lookup_google_keywords(
        self, seed_keyword, language="en", country="US", context="sh"
    ):
        """
        this function returns a list of keywords that are most searched for by google users based on the seed keyword

        Parameters
        ----------
        seed_keyword: keyword to be used to look up in the autocomplete search engine for suggesting keywords
        language: string containing the language code to be used to look up in the autocomplete search engine
                 "de","en",...
        country: string containing the country code to be used to look up in the autocomplete search engine
                 "DE","US",...
        context: string containing the context to be used to look up in the autocomplete search engine
                 "sh" for product  or "yt" for youtube

        Returns
        -------
        list containing the keywords generated from google autocomplete search engine

        """

        PARAMS = {
            "client": "youtube",
            "hl": language,
            "q": seed_keyword,
            "gl": country,
            "ds": context,
        }

        response = requests.get(
            self.GOOGLE_URL,
            params=PARAMS,
            headers=self.headers,
            proxies=renew_proxy(),
            timeout=10,
        )
        if response.status_code == 200:
            keywords = []
            keywords_outer_list = json.loads(
                response.content.decode("utf-8")
                .replace("window.google.ac.h(", "")
                .replace(")", "")
            )[1]
            for li in keywords_outer_list:
                keywords.append(li[0])
            return keywords
        else:
            return []
