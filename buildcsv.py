from datetime import datetime
from pdgrab import grab, csv

filename = 'items-%s.csv' % datetime.now().strftime('%Y%m%d%H%M')
items = grab.get_items()
csv.write_file(filename, items)
