from urllib.parse import urljoin, urlparse

import nltk
import requests
from bs4 import BeautifulSoup as bs
from tqdm import tqdm

# nltk.download('punkt')
from urllib.request import urlopen as uReq
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
import base64


class WikiScraper:

    def __init__(self, searchString):
        self.searchString = searchString

    @staticmethod
    def wiki_get_text(searchString):
        """"
        Get intro string of wiki page.
        """
        try:

            try:

                wiki_url = "https://en.wikipedia.org/wiki/" + searchString
                uClient = uReq(wiki_url)
                wikiPage = uClient.read()
                uClient.close()
            except Exception as error:
                print(f"{error=} while searching for {searchString}, try again")
            try:

                wiki_html = bs(wikiPage, "html.parser")
                wiki_para = wiki_html.findAll("p")
                wiki_summary = map(lambda x: x.get_text(), wiki_para)
                text = []
                for i in wiki_summary:
                    text.append(i)

            except Exception as e:
                print(f"error {e}, try again")

            parser = PlaintextParser.from_string(text[:5], Tokenizer("english"))
            summarizer = LexRankSummarizer()
            summ = summarizer(parser.document, 5)
            # summary1 = [str(i) for i in summ]
            summary = [str(i) for i in summ]
            summary1 = [i.replace('\\n', '') for i in summary]
            return summary1
        except Exception as error:
            print(f"{error=} couldn't find text, try again")

    @staticmethod
    def is_valid(url):
        """
        Checks whether url is a valid URL.
        """
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)

    @staticmethod
    def get_all_images(searchString):
        """
        Returns all image URLs on a single `url`
        """
        try:

            url = "https://en.wikipedia.org/wiki/" + searchString
            soup = bs(requests.get(url).content, "html.parser")
            urls = []
            for img in tqdm(soup.find_all("img"), "Extracting images"):
                img_url = img.attrs.get("src")
                if not img_url:
                    # if img does not contain src attribute
                    continue
                # make the URL absolute by joining domain with the URL that is just extracted
                img_url = urljoin(url, img_url)
                try:
                    pos = img_url.index("?")
                    img_url = img_url[:pos]
                except ValueError:
                    pass
                # finally, if the url is valid
                if WikiScraper.is_valid(img_url):
                    urls.append(img_url)
            output = [i for i in urls if searchString in i]
            return output[:5]
        except Exception as error:
            print(f"{error=} couldn't find images, try again")

    @staticmethod
    def base64Encoder(url):
        return base64.b64encode(requests.get(url).content).decode("utf-8")

    @staticmethod
    def wiki_get_img(searchString):
        """
        Modify for storing in mongodb not locally
        """
        try:

            # get all images
            images = WikiScraper.get_all_images(searchString)
            # base64 encode
            lst1 = [WikiScraper.base64Encoder(img) for img in images]
            return lst1
        except Exception as e:
            print(f"Error {e=} getting images")

    @staticmethod
    def wiki_get_references(searchString):
        """
        Get references for search query
        """
        try:

            wiki_url = "https://en.wikipedia.org/wiki/" + searchString
            webs = requests.get(wiki_url)
            soup = bs(webs.content, 'html.parser')

            links = soup.find_all('a', class_='external text', rel='nofollow')
            map1 = map(str, links)
            result = []
            for link in map1:
                result.append(link[link.find('href=\"') + 6:link.find('rel=') - 2])
            return result[:5]
        except Exception as error:
            print(f"{error=}, couldn't finding references")

    @staticmethod
    def wiki_collection(searchString):
        """
        Get all info, return as dictionary
        name field included for db storage
        """
        try:
            Summary = WikiScraper.wiki_get_text(searchString)
            Images = WikiScraper.wiki_get_img(searchString)
            References = WikiScraper.wiki_get_references(searchString)

            wikiDict = {
                "Name": searchString,
                "Summary": Summary,
                "Images": Images,
                "References": References
            }
        except Exception as error:
            print(f"{error=} couldn't compile results, try again")
        return wikiDict