import re
from html.parser import HTMLParser
from abc import ABC
from pdgrab import selector, fetch
from pdgrab.item import PdgrabRawItem, PdgrabItem


def get_items(base_url, section_prefix, sections, skipped_section_titles):
    """Collect items from Torgsib source
    Args:
        base_url (str) Base URI used for sections and pictures (e.g. 'https://torg-sib.ru')
        section_prefix (str) Additional URI prefix added to every section URL (e.g. '/catalog/tkani/')
        sections (list of str) List of URIs for each section (e.g. ['velyur', 'rogozhka', 'flok'])
        skipped_section_titles (list of str) List of titles for sections to be skipped (e.g. ['Ducati', 'Atlas'])
    Returns:
        list of PdgrabItem
    """
    items = []
    for section_uri in sections:
        url = base_url + section_prefix + section_uri + '/'
        result = TorgsibPageResult(url, base_url)

        if result.items:
            section = result.title.strip()
            for item in result.items:

                # Skip items with no pic
                if item.large_pic is None:
                    continue

                # Skip undesired sections
                if item.section in skipped_section_titles:
                    continue

                # Drop unneeded title suffix
                title = item.title
                title_redundant_suffix = 'Мебельная ткань'
                if title.endswith(title_redundant_suffix):
                    title = title[:-len(title_redundant_suffix)]

                # Transform uppercase title head
                title_head = _find_uppercase_head(title)
                if title_head is not None:
                    title = title_head.title() + title[len(title_head):]

                # Strip redundant title whitespaces
                title = title.strip()
                title = re.sub(r'\s+', r' ', title)
                title = re.sub(r'(\S-)\s+', r'\1', title)

                # Detect item target section
                if title.startswith('Купон '):
                    target_section = 'Купоны'
                else:
                    target_section = section

                # Process picture URLs
                is_available = item.is_available and bool(item.small_pic)  # deactivate items with no picture
                small_pic = (base_url + item.small_pic.strip()) if (item.small_pic is not None) else None
                large_pic = (base_url + item.large_pic.strip()) if (item.large_pic is not None) else None

                items.append(PdgrabItem(
                    title=title,
                    is_available=is_available,
                    small_pic=small_pic,
                    large_pic=large_pic,
                    section=target_section,
                    subsection=item.section,
                    dest_id=item.dest_id,
                ))

    return items


def _find_uppercase_head(title):
    """Analyze title string for uppercase beginning to be case-transformed
    Args:
        title (str) Source title string
    Returns:
        str or None: If nothing appropriate found, returns None
    """
    title_head = min((
        title.split()[0],
        title.split('/')[0],
        title.split('-')[0],
    ), key=len)
    if len(title_head) < 3:
        return None
    elif title_head == title_head.upper():
        return title_head
    else:
        return None


class TorgsibPageResult:
    def __init__(self, url, base_url):
        content = fetch(url, tolerate404=True)
        if content is None:
            self.title = None
            self.items = []
        else:
            parser = TorgsibPageParser()
            parser.feed(content)
            self.title = parser.parent_title
            self.items = parser.items

            if parser.links:
                for link in parser.links:
                    link_url = base_url + link
                    result = TorgsibPageResult(link_url, base_url)
                    self.items = self.items + result.items


class TorgsibPageParser(HTMLParser, ABC):
    def __init__(self):
        super().__init__()
        self.parent_title = None
        self.title = None
        self.links = []
        self.items = []

        self._current_item = None
        self._read_item_qty = False
        self._read_title = False
        self._read_parent_title = False

        self._content_nesting = None
        self._menu_nesting = None
        self._links_nesting = None
        self._item_nesting = None

    def handle_starttag(self, tag, attrs):
        sel = selector(tag, attrs)
        attrib = dict(attrs)

        if sel == 'div.b-content':
            if self._content_nesting is None:
                self._content_nesting = 0
        elif sel == 'ul.b-catalog-menu__group-items':
            if (self._menu_nesting is None):
                self._menu_nesting = 0
        elif sel == 'ul':
            if (self._content_nesting is not None) and (self._links_nesting is None):
                self._links_nesting = 0
        elif sel == 'div.b-catalog-item[id]':
            if (self._content_nesting is not None) and (self._item_nesting is None):
                self._item_nesting = 0
                self._current_item = PdgrabRawItem()
                self._current_item.section = self.title
                self._current_item.dest_id = attrib['id'][4:].lower()

        if (self._content_nesting == 1) and (sel == 'h1') and (self.title is None) and (not self._read_title):
            self.title = ''
            self._read_title = True
        if (self._menu_nesting == 2) and (sel == 'a[href].b-catalog-menu__item__link.b-catalog-menu__item__link_hl'):
            self._read_parent_title = True
        if (self._links_nesting == 2) and (sel == 'a[href]'):
            self.links.append(attrib['href'])
        if (self._item_nesting == 1) and (sel == 'a[href].b-catalog-item__image.b-catalog-item__image_120x120.fancybox'):
            self._current_item.large_pic = attrib['href']
        if (self._item_nesting == 2) and (sel == 'strong.b-catalog-item__name[title]'):
            self._current_item.title = attrib['title']
        if (self._item_nesting == 2) and (sel == 'span.b-catalog-item__qty') and (not self._read_item_qty):
            self._read_item_qty = True

        if self._content_nesting is not None:
            self._content_nesting = self._content_nesting + 1
        if self._menu_nesting is not None:
            self._menu_nesting = self._menu_nesting + 1
        if self._links_nesting is not None:
            self._links_nesting = self._links_nesting + 1
        if self._item_nesting is not None:
            self._item_nesting = self._item_nesting + 1

    def handle_startendtag(self, tag, attrs):
        sel = selector(tag, attrs)
        attrib = dict(attrs)
        if (self._item_nesting == 2) and (sel == 'img[src][alt]'):
            self._current_item.small_pic = attrib['src']

    def handle_data(self, data):
        if self._read_parent_title:
            self.parent_title = data.strip()
        if self._read_title:
            self.title = self.title + data
        if self._read_item_qty:
            content = data.strip()
            if content == 'нет в наличии':
                self._current_item.is_available = False
            elif content.startswith('наличие:'):
                self._current_item.is_available = True

    def handle_endtag(self, tag):
        sel = tag

        if self._read_parent_title and (sel == 'a'):
            self._read_parent_title = False
        if self._read_title and (sel == 'h1'):
            self._read_title = False
        if self._read_item_qty and (sel == 'span'):
            self._read_item_qty = False

        if self._content_nesting is not None:
            self._content_nesting = self._content_nesting - 1
            if self._content_nesting == 0:
                if sel == 'div':
                    self._content_nesting = None
                else:
                    raise Exception('Wrong html structure - div.b-content not properly closed')
        if self._menu_nesting is not None:
            self._menu_nesting = self._menu_nesting - 1
            if self._menu_nesting == 0:
                if sel == 'ul':
                    self._links_nesting = None
                else:
                    raise Exception('Wrong html structure - ul.b-catalog-menu__group-items not properly closed')
        if self._links_nesting is not None:
            self._links_nesting = self._links_nesting - 1
            if self._links_nesting == 0:
                if sel == 'ul':
                    self._links_nesting = None
                else:
                    raise Exception('Wrong html structure - ul (section links list) not properly closed')
        if self._item_nesting is not None:
            self._item_nesting = self._item_nesting - 1
            if self._item_nesting == 0:
                if sel == 'div':
                    self.items.append(self._current_item)
                    self._item_nesting = None
                else:
                    raise Exception('Wrong html structure - div.b-catalog-item not properly closed')
