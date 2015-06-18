from __future__ import unicode_literals, print_function, generators, division
import os
import subprocess
import sys

__author__ = 'pahaz'
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, '__data__')
VENV_DIR = os.path.join(DATA_DIR, 'venv')


def mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)


def mkactivate(venv_path):
    if os.name == 'nt':
        return '"{0}"'.format(os.path.join(venv_path, 'Scripts', 'activate'))
    elif os.name == 'posix':
        bin_activate = os.path.join(venv_path, 'bin', 'activate')
        return 'source "{0}"'.format(bin_activate)
    else:
        raise RuntimeError('Unknown os.name. How-to activate?')


def mkvenv(venv_path):
    subprocess.check_call('virtualenv "{0}"'.format(venv_path), shell=True)


def run_in_venv(venv_path, command):
    activate = mkactivate(venv_path)
    subprocess.check_call('{0} && {1}'.format(activate, command),
                          shell=True)


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == 'active':
        print(mkactivate(VENV_DIR))
    else:
        mkdir(DATA_DIR)
        mkvenv(VENV_DIR)
        run_in_venv(VENV_DIR, 'pip install -r requirements.txt')
