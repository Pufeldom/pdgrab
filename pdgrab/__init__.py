import re
import urllib.request
import urllib.error


def fetch(url, encoding='utf-8', tolerate404=False):
    print('- fetch ' + url)
    try:
        response = urllib.request.urlopen(url)
    except urllib.error.HTTPError:
        if tolerate404:
            print('ERROR! url %s not found (404)' % url)
            return None
        else:
            raise
    return response.read().decode(encoding)


def selector(tag, attrs=None):
    sel = tag
    if attrs:
        for attr_name, attr_value in attrs:
            if attr_name == 'class':
                for class_name in attr_value.split():
                    sel = sel + '.' + class_name
            else:
                sel = sel + '[' + attr_name + ']'
    return sel


def slugify(title):
    slug = title.lower()
    chars = {
        'а': 'a',
        'б': 'b',
        'в': 'v',
        'г': 'g',
        'д': 'd',
        'е': 'e',
        'ё': 'ye',
        'ж': 'zh',
        'з': 'z',
        'и': 'i',
        'й': 'y',
        'к': 'k',
        'л': 'l',
        'м': 'm',
        'н': 'n',
        'о': 'o',
        'п': 'p',
        'р': 'r',
        'с': 's',
        'т': 't',
        'у': 'u',
        'ф': 'f',
        'х': 'kh',
        'ц': 'ts',
        'ч': 'ch',
        'ш': 'sh',
        'щ': 'shch',
        'ы': 'y',
        'э': 'e',
        'ю': 'yu',
        'я': 'ya',
    }
    for find, replace in chars.items():
        slug = slug.replace(find, replace)
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')

    return slug
