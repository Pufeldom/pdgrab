import re
from html.parser import HTMLParser
from abc import ABC
from pdgrab import selector, fetch
from pdgrab.item import PdgrabRawItem, PdgrabItem


def get_items(base_url, section_prefix, sections, skipped_section_titles):
    """Collect items from Mtf source
    Args:
        base_url (str) Base URI used for sections and pictures (e.g. 'https://mtf-sib.ru')
        section_prefix (str) Additional URI prefix added to every section URL (e.g. '/product-category/katalog-tkanej/')
        sections (list of str) List of URIs for each section (e.g. ['veljur/grand', 'rogozhka/kiton'])
        skipped_section_titles (list of str) List of titles for sections to be skipped (e.g. ['Ducati', 'Atlas'])
    Returns:
        list of PdgrabItem
    """
    items = []
    for section_uri in sections:
        url = base_url + section_prefix + section_uri + '/'
        result = MtfPageResult(url, base_url)

        if result.items:
            section = result.title.strip()
            for item in result.items:

                # Skip items with no pic
                if item.large_pic is None:
                    continue

                # Skip undesired sections
                if item.section in skipped_section_titles:
                    continue

                items.append(PdgrabItem(
                    title=item.title,
                    is_available=item.is_available,
                    small_pic=item.small_pic.strip(),
                    large_pic=item.large_pic.strip(),
                    section=section,
                    subsection=item.section,
                    dest_id=item.dest_id,
                ))

    return items


class MtfPageResult:
    def __init__(self, url, base_url, ignore_pages=False):
        content = fetch(url, tolerate404=True)
        if content is None:
            self.title = None
            self.items = []
        else:
            parser = MtfPageParser()
            parser.feed(content)
            self.title = parser.parent_title
            self.items = parser.items

            if parser.links and not ignore_pages:
                for link in parser.links:
                    link_url = link
                    result = MtfPageResult(link_url, base_url, ignore_pages=True)
                    self.items = self.items + result.items


class MtfPageParser(HTMLParser, ABC):
    def __init__(self):
        super().__init__()
        self.parent_title = None
        self.title = None
        self.links = []
        self.items = []

        self._current_item = None
        self._read_item_title = False
        self._read_title = False
        self._read_parent_title = False

        self._breadcrumbs_nesting = None
        self._content_nesting = None
        self._links_nesting = None
        self._item_nesting = None

    def handle_starttag(self, tag, attrs):
        sel = selector(tag, attrs)
        attrib = dict(attrs)

        if sel == 'div.breadcrumbs[typeof][vocab]':
            if self._breadcrumbs_nesting is None:
                self._breadcrumbs_nesting = 0
        elif sel == 'div[id].site-content':
            if self._content_nesting is None:
                self._content_nesting = 0
        elif sel == 'ul.page-numbers':
            if (self._content_nesting is not None) and (self._links_nesting is None):
                self._links_nesting = 0
        elif sel.startswith('li.product.type-product.'):
            if (self._content_nesting is not None) and (self._item_nesting is None):
                self._item_nesting = 0
                self._current_item = PdgrabRawItem()
                self._current_item.section = self.title
                self._current_item.is_available = False
                self._current_item.dest_id = 'm' + re.sub(r'^.+ post-(\d+) .+$', r'\1', attrib['class'])

        if (self._breadcrumbs_nesting == 3) and (sel == 'span[property]') and (not self._read_parent_title):
            self._read_parent_title = True
        if (self._content_nesting == 5) and (sel == 'h1.entry-title.page-title') and (self.title is None) and (not self._read_title):
            self.title = ''
            self._read_title = True
        if (self._links_nesting == 2) and (sel == 'a.page-numbers[href]'):
            self.links.append(attrib['href'])
        if (self._item_nesting == 4) and (sel == 'h2.woocommerce-loop-product__title') and (not self._read_item_title):
            self._read_item_title = True
        if (self._item_nesting == 4) and (sel == 'span.woocommerce-Price-amount.amount'):
            self._current_item.is_available = True

        if (self._breadcrumbs_nesting is not None) and (tag != 'meta'):
            self._breadcrumbs_nesting = self._breadcrumbs_nesting + 1
        if self._content_nesting is not None:
            self._content_nesting = self._content_nesting + 1
        if self._links_nesting is not None:
            self._links_nesting = self._links_nesting + 1
        if self._item_nesting is not None:
            self._item_nesting = self._item_nesting + 1

    def handle_startendtag(self, tag, attrs):
        sel = selector(tag, attrs)
        attrib = dict(attrs)
        if (self._item_nesting == 4) and sel.startswith('img[width][height][src]'):
            self._current_item.small_pic = attrib['src']
            self._current_item.large_pic = re.sub(r'-300x300(\..+)$', r'\1', attrib['src'])

    def handle_data(self, data):
        if self._read_parent_title:
            self.parent_title = data.strip()
        if self._read_title:
            self.title = self.title + data
        if self._read_item_title:
            self._current_item.title = data.strip()

    def handle_endtag(self, tag):
        sel = tag

        if self._read_parent_title and (sel == 'span'):
            self._read_parent_title = False
        if self._read_title and (sel == 'h1'):
            self._read_title = False
        if self._read_item_title and (sel == 'h2'):
            self._read_item_title = False

        if self._breadcrumbs_nesting is not None:
            self._breadcrumbs_nesting = self._breadcrumbs_nesting - 1
            if self._breadcrumbs_nesting == 0:
                if sel == 'div':
                    self._breadcrumbs_nesting = None
                else:
                    raise Exception('Wrong html structure - div.breadcrumbs not properly closed')
        if self._content_nesting is not None:
            self._content_nesting = self._content_nesting - 1
            if self._content_nesting == 0:
                if sel == 'div':
                    self._content_nesting = None
                else:
                    raise Exception('Wrong html structure - div#content not properly closed')
        if self._links_nesting is not None:
            self._links_nesting = self._links_nesting - 1
            if self._links_nesting == 0:
                if sel == 'ul':
                    self._links_nesting = None
                else:
                    raise Exception('Wrong html structure - ul.page-numbers not properly closed')
        if self._item_nesting is not None:
            self._item_nesting = self._item_nesting - 1
            if self._item_nesting == 0:
                if sel == 'li':
                    self.items.append(self._current_item)
                    self._item_nesting = None
                else:
                    raise Exception('Wrong html structure - li.product.type-product not properly closed')
