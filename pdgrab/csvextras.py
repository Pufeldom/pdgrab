import os
from pdgrab.item import PdgrabItemExtras

MATERIALS_DIR = '_materials'
MATERIALS_FILE_EXT = '.html'


def get_extras():
    """Read items extras from jekyll files, providing collected result
    Returns:
        dict of PdgrabItemExtras
    """
    extras = {}

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
        fh = open(file_path)
        file_data = _read_jekyll_data(fh)

        # Create extras item
        extras[file_basename.lower()] = PdgrabItemExtras(
            martindale=file_data.get('martindale'),
            density=file_data.get('density'),
        )

    return extras


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
