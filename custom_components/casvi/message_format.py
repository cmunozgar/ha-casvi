"""Retain message structure as inert nodes, never pass through source HTML."""
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit
import re

TAGS = {'p','div','br','strong','b','em','i','u','s','ul','ol','li','blockquote','h1','h2','h3','h4','a'}
VOID = {'br','img','hr','input','meta','link','wbr','area','base','col','embed','param','source','track'}


class MessageStructure(HTMLParser):
    def __init__(self):
        super().__init__()
        self.nodes = []
        self.stack = []
        self.hidden = 0

    def target(self):
        return next((node['children'] for _,node,_ in reversed(self.stack) if node is not None), self.nodes)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        style = attrs.get('style','')
        hidden = tag in {'script','style','iframe','object','svg','form'} or 'hidden' in attrs or bool(re.search(r'display\s*:\s*none|visibility\s*:\s*hidden',style,re.I))
        node = None
        if not self.hidden and not hidden:
            if tag in TAGS:
                node = {'tag':tag,'children':[]}
                if tag == 'a':
                    try:
                        url = urljoin('https://intranet.casvi.es/',attrs.get('href',''))
                        parsed = urlsplit(url)
                        if attrs.get('href') and parsed.scheme in {'http','https'} and parsed.hostname and not parsed.username:
                            node['href'] = url
                    except ValueError:
                        pass
                self.target().append(node)
            elif tag == 'span' and re.search(r'text-decoration(?:-line)?\s*:[^;]*underline',style,re.I):
                node = {'tag':'u','children':[]}
                self.target().append(node)
        if tag not in VOID:
            self.stack.append((tag,node,hidden))
            self.hidden += int(hidden)

    def handle_endtag(self, tag):
        for index in range(len(self.stack)-1,-1,-1):
            if self.stack[index][0] == tag:
                self.hidden -= sum(hidden for _,_,hidden in self.stack[index:])
                del self.stack[index:]
                break

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag,attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_data(self, text):
        if not self.hidden:
            self.target().append({'text':re.sub(r'\s+',' ',text)})


def message_nodes(html):
    parser = MessageStructure()
    parser.feed(str(html or '').replace('\\r\\n','\n'))
    return parser.nodes
