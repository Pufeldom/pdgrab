import os
import sys
import io
import re

ITEMS_DIR = '_items'
ITEMS_FILE_EXT = '.html'
TITLE_RE = r'\ntitle:\s+([\S\s]+?)\n'
PRICE_RE = r'(\nprice:\s+)(\d+)(\s*?\n)'
NEGATE_CHAR = '^'

args = sys.argv[1:]
price_delta = int(args[0])
try:
    title_search = args[1].lower().strip()
except IndexError:
    title_search = None
if (title_search is not None) and title_search.startswith(NEGATE_CHAR):
    title_search_negate = True
    title_search = title_search[len(NEGATE_CHAR):].lstrip()
else:
    title_search_negate = False

for entry in os.listdir(ITEMS_DIR):
    file_path = os.path.join(ITEMS_DIR, entry)
    if not os.path.isfile(file_path):
        continue
    file_basename, file_ext = os.path.splitext(entry)
    if file_ext != ITEMS_FILE_EXT:
        continue

    price = None
    with io.open(file_path, 'r', encoding='utf8') as f:
        file_content = f.read()
        if title_search is not None:
            try:
                [title] = re.findall(TITLE_RE, file_content)
            except ValueError:
                print(f'WARNING: cannot get title for {file_basename}')
                continue
            title = title.strip().lower()
            if title_search_negate == (title_search in title):
                continue
        try:
            [(_before, price, _after)] = re.findall(PRICE_RE, file_content)
        except ValueError:
            print(f'WARNING: cannot get existing price for {file_basename}')
            continue

    price = int(price)
    new_price = price + price_delta
    file_content = re.sub(PRICE_RE, lambda m: m.group(1) + str(new_price) + m.group(3), file_content, 1)

    with io.open(file_path, 'w', encoding='utf8') as f:
        print(f'- update {file_basename} price: {price} -> {new_price}')
        f.write(file_content)
