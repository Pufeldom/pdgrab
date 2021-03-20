import csv
from importlib import import_module
from pdgrab import config


def write_files(file_path_prefix, items):
    """Get given param value, or all params from config section
    Args:
        file_path_prefix (str) Prefix of destination file path ('_<TARGET_NAME>.csv' will be appended to that value)
        items (list of PdgrabItem) List of catalog items to output
    """

    targets = config.get_param('csv', 'targets', True)
    for target_name in targets:
        target_module = import_module(__name__ + '_' + target_name)  # provide 'pdgrab.csv_<TARGET_NAME>'
        target_delimiter = target_module.DELIMITER
        target_cols = config.get_section('csv' + '_' + target_name)
        target_file_path = file_path_prefix + '-' + target_name + '.csv'
        print('- write ' + target_file_path)
        with open(target_file_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(
                csvfile, fieldnames=target_cols.keys(), dialect=csv.unix_dialect, delimiter=target_delimiter,
                quoting=csv.QUOTE_MINIMAL,
            )
            writer.writeheader()
            for item in items:
                values = {k: target_module.get_value(v, item) for k, v in target_cols.items()}
                writer.writerow(values)
