import os
import configparser


CONFIG_FILE_NAME = 'pdgrab.ini'
"""str: Configuration file name
Config files are searched inside module directory
"""


def get(section, param=None, value_is_list=False):
    """Get given param value, or all params from config section
    Args:
        section (str) Config section name
        param (str=None) Parameter name from given section (if None, return all section params)
        value_is_list (bool=False) Provide parameter value as list
    Returns:
        (str or bool or int or float) or (dict of (str: str or bool or int or float))
    Example:
        from pdgrab import config
        config.get('mysection')         -> {'foo': 'bar', 'baz': 42, 'qux': True}
        config.get('mysection', 'foo')  -> 'bar'
    """
    if param is None:
        return get_section(section)
    else:
        return get_param(section, param, value_is_list)


def get_param(section, param, value_is_list=False):
    """Get given param value from config section
    Args:
        section (str) Config section name
        param (str) Section parameter name
        value_is_list (bool=False) Provide parameter value as list
    Returns:
        str or bool or int or float
    Raises:
        PdgrabConfigNoSectionException: Config section not found
        PdgrabConfigNoParamException: Config param not found in section
        PdgrabConfigUnknownException: Cannot get config param for some other reason
    """
    try:
        value = get_parser().get(section, param)
    except configparser.NoSectionError:
        raise PdgrabConfigNoSectionException('Config section "%s" not found' % section)
    except configparser.NoOptionError:
        raise PdgrabConfigNoParamException('Config param "%s" not found in section "%s"' % (param, section))
    except BaseException as ex:
        raise PdgrabConfigUnknownException('Cannot get config param value: %s' % ex)

    return value.split() if value_is_list else value


def get_section(section):
    """Get all params from config section as dict
    Args:
        section (str) Config section name
    Returns:
        dict of (str: str or bool or int or float): {'foo': 'bar', 'baz': 42, 'qux': True}
    Raises:
        PdgrabConfigNoSectionException: Config section not found
        PdgrabConfigUnknownException: Cannot get config section for some other reason
    """
    try:
        params = dict(get_parser().items(section))
    except configparser.NoSectionError:
        raise PdgrabConfigNoSectionException('Config section "%s" not found' % section)
    except BaseException as ex:
        raise PdgrabConfigUnknownException('Cannot get config section: %s' % ex)

    return params


def get_parser():
    """Read and merge configuration files, then return parser instance
    Returns:
        configparser.RawConfigParser
    Raises:
        PdgrabConfigFileException: Cannot read configuration file
    """
    parser = configparser.RawConfigParser()
    parser.optionxform = str  # prevent lowercase params

    try:
        parser.read(get_config_path(), encoding='utf-8')
    except BaseException as ex:
        raise PdgrabConfigFileException('Cannot read configuration file: %s' % ex)

    return parser


def get_config_path():
    """Get configuration file path (searched in module directory)"""
    return os.path.join(os.path.dirname(__file__), CONFIG_FILE_NAME)


class BasePdgrabConfigException(BaseException):
    """Base class for any config exception"""


class PdgrabConfigFileException(BasePdgrabConfigException):
    """Cannot read config file"""


class PdgrabConfigNoSectionException(BasePdgrabConfigException):
    """Config section not found"""


class PdgrabConfigNoParamException(BasePdgrabConfigException):
    """Parameter not found in given section"""


class PdgrabConfigUnknownException(BasePdgrabConfigException):
    """Something else went wrong"""


