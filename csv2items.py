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
src_sections = [
    'Пуфы круглые на металлических ножках',
    'Пуфы прямоугольные',
    'Пуфы круглые на деревянных ножках',
    'Пуфы круглые',
    'Банкетки',
    'Прочее',
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
        if row['Раздел (уровень 2)'] in src_sections:
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
                        [(pmurl, image, gallery_str)] = re.findall(
                            r'\npmurl:\s*([\S\s]*?)\nimage:\s*([\S\s]*?)\ngallery:([\S\s]*?)\nnew:',
                            dest_file_content,
                        )
                    except ValueError:
                        print(f'  WARNING: cannot get existing images data for {dest_file_path}')
                    try:
                        [(youla_str)] = re.findall(
                            r'\nyoula:\s*([\S\s]*?)\n---',
                            dest_file_content,
                        )
                    except ValueError:
                        print(f'  WARNING: cannot get existing youla value for {dest_file_path}')

            # Build new destination content
            dest_file_content = f"""---
hru: {row['Символьный код']}
title: {row['Название']}
price: {int(float(row['Цена']))}
section: {row['Раздел (уровень 2)']}
color: {row['Цвет']}
shape: {row['Форма']}
width: {row['Ширина, cм']}
depth: {row['Глубина, cм']}
height: {row['Высота, cм']}
material: {row['Материал обивки']}
legs: {row['Материал ножек']}
martindale: {row['Тест Мартиндейла']}
density: {row['Плотность ткани, г/м2']}
weight: {row['Вес, кг']}
pmurl: {pmurl}
image: {image}
gallery:{gallery_str or ' '}
new: {'true' if (row['Новинка'] == 'да') else 'false'}
active: {'true' if (row['Активен'] == 'да') else 'false'}
youla: {youla_str}
---

"""
            if row['Описание']:
                dest_file_content = dest_file_content + row['Описание'].replace('<br />', '') + '\n'

            # Write destination file
            with io.open(dest_file_path, 'w', encoding='utf8') as f:
                print(f'- write {dest_file_path}')
                f.write(dest_file_content)
