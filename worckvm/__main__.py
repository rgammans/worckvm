import argparse
from functools import cached_property
import worckvm.config as config
import pkgutil
import pathlib
import logging
import copy
import contextlib


logger = logging.getLogger(__name__)


DEFAULT_CONFIG_FILE = 'matrix.yml'

def _available_modes():
    modules = {}
    for module in pkgutil.iter_modules([pathlib.Path(__file__).parent]):
        if module.name.endswith('_app'):
            logger.debug(f"loading {module.name}")
            try:
                appmod = __import__('worckvm.' + module.name, fromlist=['worckvm'])
                modules[module.name[:-4]] = appmod
            except ImportError as e:
                logger.warning(f"\tfailed to load {module.name}:{e}")
    return modules

Modes = _available_modes()
logger.info(f"Available modes {Modes.keys()}")

def get_parser():
    parser = argparse.ArgumentParser(description='A KVM Switch fabric manager')
    parser.add_argument('--drivers', help='Python modules containing drivers', action='append', default=['worckvm.drivers.mock'])
    parser.add_argument('--matrix-def', help='The YAML file which describes the matrix', default=DEFAULT_CONFIG_FILE)
    subparser = parser.add_subparsers(dest='mode', help='API mode to use')
    default_tags = [action.dest for action in parser._actions]
    for name, module in Modes.items():
        p = subparser.add_parser(name, help=module.__doc__)
        module.set_options(p)
    
    return default_tags, parser


def load_drivers(drivers):
    for driver in drivers:
      __import__(driver)


def get_matrix(args):
    with open(args.matrix_def) as f:
        return config.loads(f.read())


def start_app(main_opts, args):
    # copy the argslist and remove anything for the root context
    # so the app only gets their requests kwargs
    app_args = copy.copy(args.__dict__)
    for opt in main_opts:
        with contextlib.suppress(KeyError):
            del app_args[opt]
    Modes[args.mode].run(**app_args)


if __name__ == '__main__':
    main_opts, parser = get_parser()
    args = parser.parse_args()
    print(args)
    load_drivers(args.drivers)
    get_matrix(args)
    start_app(main_opts, args)
