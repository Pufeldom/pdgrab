import sys
import os
import io
import re
import csv


# Apply source file cli arg
try:
    src_file_path = sys.argv[1]
except IndexError:
    print('\n')
    print('ERROR: Source csv file not defined')
    print('Usage: python csv2items.py CSV_FILE_NAME.csv')
    print('\n')
    sys.exit(1)

# Configure other params
root_src_sections = [
    'Мебель',
    'Распродажа',
]
dest_dir = '_items/'

# Check source file
print(f'- read {src_file_path}')
if not os.path.isfile(src_file_path):
    print('\n')
    print(f'ERROR: Source csv file not found: {src_file_path}')
    print('\n')
    sys.exit(1)

# Parse source file
with open(src_file_path, newline='') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=';')
    for row in reader:
        if row['Раздел (уровень 2)'] in root_src_sections:
            dest_file_path = dest_dir + row['Внешний код'] + '.html'

            # Detect existing images data
            pmurl = None
            image = None
            gallery_str = None
            youla_str = 'false'
            if os.path.isfile(dest_file_path):
                print(f'- read {dest_file_path}')
                with io.open(dest_file_path, 'r', encoding='utf8') as f:
                    dest_file_content = f.read()
                    try:
                        [(legs_color, foam)] = re.findall(
                            r'\nlegs_color:\s*([\S\s]*?)\nfoam:\s*([\S\s]*?)\nmartindale:',
                            dest_file_content,
                        )
                    except ValueError:
                        print(f'  WARNING: cannot get existing legs_color/foam data for {dest_file_path}')
                    try:
                        [(pmurl, image, gallery_str)] = re.findall(
                            r'\npmurl:\s*([\S\s]*?)\nimage:\s*([\S\s]*?)\ngallery:([\S\s]*?)\nactive:',
                            dest_file_content,
                        )
                    except ValueError:
                        print(f'  WARNING: cannot get existing images data for {dest_file_path}')
                    try:
                        [(stock_str, youla_str)] = re.findall(
                            r'\nstock:\s*([\S\s]*?)\nyoula:\s*([\S\s]*?)\n---',
                            dest_file_content,
                        )
                    except ValueError:
                        print(f'  WARNING: cannot get existing stock/youla values for {dest_file_path}')

            # Build new destination content
            dest_file_content = f"""---
parent: 
hru: {row['Символьный код']}
title: {row['Название']}
price: {int(float(row['Цена']))}
section: {row['Раздел (уровень 3)']}
color: {row['Цвет']}
width: {row['Ширина, см']}
depth: {row['Глубина, см']}
height: {row['Высота, см']}
material: {row['Материал обивки']}
legs: {row['Материал ножек']}
legs_color: {legs_color}
foam: {foam}
martindale: {row['Тест Мартиндейла']}
density: {row['Плотность ткани, г/м2']}
weight: {row['Вес, кг']}
pmurl: {pmurl}
image: {image}
gallery:{gallery_str or ' '}
active: {'true' if (row['Активен'] == 'да') else 'false'}
stock: {stock_str}
youla: {youla_str}
---

"""
            if row['Описание']:
                dest_file_content = dest_file_content + row['Описание'].replace('<br />', '') + '\n'

            # Write destination file
            with io.open(dest_file_path, 'w', encoding='utf8', newline="") as f:
                print(f'- write {dest_file_path}')
                f.write(dest_file_content)
