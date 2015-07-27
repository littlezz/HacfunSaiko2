from collections import namedtuple
import re
from urllib import parse
from bs4 import BeautifulSoup
import os.path
import requests
__author__ = 'zz'


island_netloc_table = {}
island_class_table = {}


DivInfo = namedtuple('DivInfo', ['content', 'link', 'response_num', 'image'])


class IslandNotDetectError(Exception):
    pass





class IslandMeta(type):

    def __init__(cls, name, bases, ns):
        if name != 'BaseIsland':
            island_name = ns.get('_island_name')
            island_netloc = ns.get('_island_netloc')
            assert island_name , 'Not define _island_name in {} class'.format(name)
            assert island_netloc , 'Not define _island_netloc in {} class'.format(name)

             # register island and netloc
            island_netloc_table.update({island_netloc: island_name})

            # register island class
            island_class_table.update({island_name: cls})

        super().__init__(name, bases, ns)


class BaseIsland(metaclass=IslandMeta):

    _island_name = ''
    _island_netloc = ''
    _island_scheme = 'http'
    _count_pattern = re.compile(r'\s(\d+)\s')
    json_data = False
    show_image = True

    def __init__(self, current_url, res):
        if not self.json_data:
            self.pd = BeautifulSoup(res.content)
        else:
            self.pd = res.json()

        self.current_url = current_url

    @property
    def root_url(self):
        return parse.urlunsplit((self._island_scheme, self._island_netloc, '', '', ''))

    def get_div_response_num(self, tip):
        """
        return response count
        """
        text = tip.text
        match = self._count_pattern.search(text)
        if match:
            return match.group(1)
        else:
            # may be the text is 'sega'
            return 0



    def get_tips(self, pd):
        """
        :param pd: a BeautifulSoup object or json object, determine by json_data
        return a list of  object that contain tips content
        """
        raise NotImplementedError

    def get_div_link(self, tip):
        """
        tip is a BeautifulSoup object contain response tip
        return the link href string, eg, 'http://xx.com', or /xx/xx.html """
        raise NotImplementedError

    def get_div_content(self, tip):
        """
        return content
        """
        raise NotImplementedError

    def get_div_image(self, tip):
        raise NotImplementedError

    def get_next_page(self):
        """
        return (url, page_num)
        """
        raise NotImplementedError

    def next_page_valid(self, next_page_url, page_num):
        raise NotImplementedError

    def next_page(self, max_page):
        """
        return next page url
        """
        url, page_num = self.get_next_page()
        if url and page_num <= max_page and self.next_page_valid(url, page_num):
            return url
        else:
            return None

    def island_split_page(self):
        """
        must return DivInfo object
        """
        result = []

        pd = self.pd
        tips = self.get_tips(pd)
        for tip in tips:
            response_num = int(self.get_div_response_num(tip))
            link = self.complete_link(self.get_div_link(tip))
            content = self.get_div_content(tip)
            image = self.get_div_image(tip) if self.show_image else ''
            image = self.complete_link(image)

            div = DivInfo(content=content, link=link, response_num=response_num, image=image)
            result.append(div)

        return result


    def complete_link(self, url):
        if not url:
            return ''
        return parse.urljoin(self.root_url, url)


class NextPageStaticHtmlMixin:
    _static_count_pattern = re.compile(r'(\d+)')

    def get_next_page(self):
        path = parse.urlparse(self.current_url).path
        basename = os.path.basename(path)
        # static html basename must be d.htm(l)
        current_page_num, suffix  = basename.split('.')

        if current_page_num == 'index':
            current_page_num = 0

        next_page_num = int(current_page_num) + 1
        next_basename = '.'.join((str(next_page_num), suffix))


        # In [73]: parse.urljoin('gg/h.html','gg.html')
        # Out[73]: 'gg/gg.html'
        return parse.urljoin(self.current_url, next_basename), next_page_num

    def next_page_valid(self, next_page_url, page_num):
        return requests.head(next_page_url).ok


class NextPageJsonParameterMixin:
    _has_next_page = True


    def get_max_page(self):
        return int(self.pd['page']['size'])

    def get_next_page(self):
        max_page = self.get_max_page()


        base_url, query = parse.splitquery(self.current_url)
        if not query:
            query='page=0'

        _, count = parse.parse_qsl(query)[0]
        count = int(count) + 1
        if count > max_page:
            self._has_next_page = False

        next_query = parse.urlencode({'page': count})
        url = base_url+ '?' + next_query
        return url, count


    def next_page_valid(self, url, page_num):
        return self._has_next_page