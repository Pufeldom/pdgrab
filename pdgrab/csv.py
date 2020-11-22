import csv
from pdgrab import config

COLS = config.get_section('csv')


def write_file(file_path, items):
    """Get given param value, or all params from config section
    Args:
        file_path (str) Destination file path
        items (list of PdgrabItem) List of catalog items to output
    """
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=COLS.keys(), dialect=csv.unix_dialect, delimiter=';')
        writer.writeheader()
        for item in items:
            values = {}
            for k, v in COLS.items():
                value = v
                value = value.replace('@dest_id', item.dest_id or '')
                value = value.replace('@is_available', 'да' if item.is_available else 'нет')
                value = value.replace('@title', item.title)
                value = value.replace('@slug', item.slug)
                value = value.replace('@section', item.section)
                value = value.replace('@subsection', item.subsection)
                value = value.replace('@small_pic', item.small_pic or '')
                value = value.replace('@large_pic', item.large_pic or '')
                values[k] = value
            writer.writerow(values)
    print('- write ' + file_path)
