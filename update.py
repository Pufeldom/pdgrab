import sys
import os
import io
import re
import csv

FM_SEP = '---\n'
FM_IDX = 1

# Preset params
usage_example = 'Usage: python update.py CSV_FILE_NAME.csv "ID column" param1 param2 (...)'
csv_delim = ','
dest_dir = '_items/'
dest_file_ext = '.html'

# Apply source file cli arg
try:
    src_file_path = sys.argv[1]
except IndexError:
    print('\n')
    print('ERROR: Source csv file not defined')
    print(usage_example)
    print('\n')
    sys.exit(1)

# Apply ID column name
try:
    id_column = sys.argv[2]
except IndexError:
    print('\n')
    print('ERROR: ID column not defined')
    print(usage_example)
    print('\n')
    sys.exit(1)

# Apply target params
target_params = sys.argv[3:]
if len(target_params) < 1:
    print('\n')
    print('ERROR: Target params not defined')
    print(usage_example)
    print('\n')
    sys.exit(1)

# Check source file
print(f'- read {src_file_path}')
if not os.path.isfile(src_file_path):
    print('\n')
    print(f'ERROR: Source csv file not found: {src_file_path}')
    print('\n')
    sys.exit(1)

# Read source csv file
with open(src_file_path, newline='') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=csv_delim)
    for row in reader:
        print('')
        item_id = row[id_column]
        dest_file_path = dest_dir + item_id + dest_file_ext

        # Read destination item file
        print(f'- read {dest_file_path}')
        try:
            with io.open(dest_file_path, 'r', encoding='utf8') as f:
                dest_file_content = f.read()
                content_parts = dest_file_content.split(FM_SEP)
                front_matter = content_parts[FM_IDX]
                front_matter_new = front_matter

                # Find and replace each destination param value
                for param in target_params:
                    param_value = row[param].strip()
                    param_re = fr'(^|\n)({param}):(.*?)\n'
                    if re.search(param_re, front_matter_new, flags=re.I) is not None:
                        front_matter_new = re.sub(param_re, fr'\1\2: {param_value}\n', front_matter_new, flags=re.I)
                    else:
                        print(f"  WARNING: '{param}' param not found {dest_file_path}, value will not be updated")

                # Write destination item file (if updated)
                if front_matter_new != front_matter:
                    content_parts[FM_IDX] = front_matter_new
                    dest_file_content = FM_SEP.join(content_parts)
                    with io.open(dest_file_path, 'w', encoding='utf8', newline="") as f:
                        print(f'- write {dest_file_path}')
                        f.write(dest_file_content)
                else:
                    print(f'- no change made for {dest_file_path}')
        except FileNotFoundError:
            print(f"  WARNING: file {dest_file_path} not found, skipping row for '{item_id}'")
