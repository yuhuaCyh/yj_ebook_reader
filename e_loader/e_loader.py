import re
from urllib.parse import urljoin
import web
from bs4 import BeautifulSoup


class ELoader:
    def __init__(self, dict_conf):
        self.dict_conf = dict_conf
        user_agent = ('Mozilla/5.0 (iPhone; CPU iPhone OS 11_2_6 like'
                      'Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko)'
                      'CriOS/65.0.3325.152 Mobile/15D100 Safari/604.1')

        self.headers = {'User-Agent': user_agent}
        # 'url': text
        self.cache = {}

    def reset_url(self, url):
        self.url = url
        for i in self.dict_conf['websites']:
            if i['url'] in url:
                self.conf = i
                break
        else:
            self.conf = None
        
    def get_criteria(self, dict_criteria):
        name = dict_criteria.get('name', None)
        attrs = dict_criteria.get('attrs', {})
        string_pattern = dict_criteria.get('string', None)
        string = None if string_pattern is None else re.compile(string_pattern)
        return name, attrs, string

    def get_url2next(self):
        next_tags = self.conf['next']
        for next_tag in next_tags:
            if 're_body' in next_tag:
                results = re.findall(re.compile(next_tag['re_body']), self.text)
                link = results[0]
                self.url = urljoin(self.url, link)
                print(self.url)
                return self.url
            name, attrs, string = self.get_criteria(next_tag)
            # print(text)
            results = self.soups.find_all(name, attrs=attrs, string=string)
            # print(results)
            if results:
                link = results[0]['href']
                # print(results)
                # 防止j s (此时一般就是没了)
                if '/' in link or '.' in link:
                    self.url = urljoin(self.url, link)
                    return self.url
        return None

    def encoding_page(self, url=None):
        if url is None:
            url = self.url
        headers = {**self.headers, **self.conf.get('headers', {})}
        if url in self.cache:
            text, encoding = self.cache[url]
            soups = BeautifulSoup(text, 'html.parser')
            self.encoding = encoding
            self.soups = soups
            self.text = text
            return soups
        rsp = web.get(url, headers=headers)
        rsp.encoding = self.conf.get('encoding', rsp.encoding)
        self.encoding = rsp.encoding
        text = rsp.text
        soups = BeautifulSoup(text, 'html.parser')
        # print(soups.prettify())
        self.cache[url] = (text, self.encoding)
        self.text = text
        self.soups = soups
        return soups
    
    def get_title(self):
        title_func = self.conf['title']
        if title_func:
            title = self.soups.find(title_func).string
        else:
            title = self.soups.find('title').string
        return str(title).strip()
