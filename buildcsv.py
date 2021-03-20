from datetime import datetime
from pdgrab import grab, csv

filename_prefix = 'items-%s' % datetime.now().strftime('%Y%m%d%H%M')
items = grab.get_items()
csv.write_files(filename_prefix, items)
