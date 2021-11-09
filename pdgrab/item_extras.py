import os
from collections import namedtuple
from pdgrab import config

MATERIALS_DIR = '_materials'
MATERIALS_FILE_EXT = '.html'
COLORS = config.get_section('color')

MaterialData = namedtuple('MaterialData', ('martindale', 'density'))


def _read_materials():
    """Read materials data from jekyll files, providing collected result
    Returns:
        dict of MaterialData
    """
    materials = {}

    # Process files in materials dir
    for entry in os.listdir(MATERIALS_DIR):
        file_path = os.path.join(MATERIALS_DIR, entry)
        if not os.path.isfile(file_path):
            continue
        file_basename, file_ext = os.path.splitext(entry)
        if file_ext != MATERIALS_FILE_EXT:
            continue

        # Read and parse file content
        print(f'- read {file_path}')
        fh = open(file_path, encoding='utf-8')
        file_data = _read_jekyll_data(fh)

        # Create materials item
        materials[file_basename.lower()] = MaterialData(
            martindale=file_data.get('martindale'),
            density=file_data.get('density'),
        )

    return materials


def _read_jekyll_data(fh):
    """Extract and parse front matter from jekyll file
    Todo:
        Only plain values are processed for now (no arrays, no objects)
    Args:
        fh (io.TextIOWrapper) Opened file handler
    Returns:
        dict of (NoneType or bool or float or int or str)
    """
    jekyll_data = {}

    # Read file line-by-line
    is_in_frontmatter = False
    while True:
        line = fh.readline()
        if not line:
            # File end reached
            break
        elif line.rstrip() == '---':
            if not is_in_frontmatter:
                # Enter front matter
                is_in_frontmatter = True
                continue
            else:
                # Exit front matter
                break

        # Read values from front matter
        if is_in_frontmatter:
            try:
                (prop, value_raw) = tuple(map(lambda x: x.strip(), line.split(':', maxsplit=2)))
            except ValueError:
                continue
            jekyll_data[prop] = _process_yaml_value(value_raw)

    return jekyll_data


def _process_yaml_value(value_raw):
    """Process raw yaml value
    Todo:
        Only plain values are processed for now (no arrays, no objects)
    Args:
        value_raw (str) Raw string value as read from file
    Returns:
        NoneType or bool or float or int or str
    """
    if not len(value_raw):
        return None
    elif value_raw == 'null':
        return None
    elif value_raw == 'true':
        return True
    elif value_raw == 'false':
        return False
    elif '.' in value_raw:
        try:
            return float(value_raw)
        except ValueError:
            return value_raw
    else:
        try:
            return int(value_raw)
        except ValueError:
            return value_raw


class PdgrabItemExtras:
    def __init__(self, material_data, color=None):
        if color:
            try:
                self.color_code = '#' + COLORS[color]
                self.color = color
            except KeyError:
                raise PdgrabItemExtrasUnknownColorException(f'Unknown color {color}')
        else:
            self.color_code = '#FFFFFF'
            self.color = 'Другой'

        self.martindale = material_data.martindale
        self.density = material_data.density


class PdgrabItemExtrasProvider:
    def __init__(self):
        self._color_marks = config.get_section('color_marks')
        self._materials = _read_materials()
        self._empty_material = MaterialData(martindale=None, density=None)

    def get_extras(self, title, material=None):
        material_key = material.lower() if material else None
        material_data = self._materials.get(material_key) or self._empty_material

        matched_mark = None
        detected_color = None
        for mark, color in self._color_marks.items():
            if mark in title:
                matched_mark = mark
                detected_color = color
                break
        if detected_color is None:
            print(f'WARNING! cannot detect color for item title: {title}')

        try:
            return PdgrabItemExtras(material_data=material_data, color=detected_color)
        except PdgrabItemExtrasUnknownColorException:
            print(
                f'WARNING! unknown color "{detected_color}" defined for mark "{matched_mark}"',
                f'(matched for item title: "{title}")',
            )
            return PdgrabItemExtras(material_data=material_data)


class PdgrabItemExtrasUnknownColorException(Exception):
    """Color name not found in 'colors' section of config"""
