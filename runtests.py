#!/usr/bin/env python
import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner

__author__ = 'pahaz'
# based on http://djbook.ru/rel1.8/topics/testing/advanced.html#using-the-django-test-runner-to-test-reusable-applications
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, '__data__')
VENV_DIR = os.path.join(DATA_DIR, 'venv')


def detect_test_apps():
    for dir_ in os.listdir(BASE_DIR):
        test_dir = (os.path.join(BASE_DIR, dir_, 'tests'))
        if not os.path.isdir(test_dir):
            continue

        init_file = os.path.join(test_dir, '__init__.py')
        test_settings_file = os.path.join(test_dir, 'test_settings.py')
        models_file = os.path.join(test_dir, 'models.py')
        tests_file = os.path.join(test_dir, 'tests.py')
        files = [init_file, test_settings_file, models_file, tests_file]
        if all(map(os.path.isfile, files)):
            yield dir_


if __name__ == "__main__":
    for app in detect_test_apps():
        print(' * Test * : ' + app)
        os.environ['DJANGO_SETTINGS_MODULE'] = app + '.tests.test_settings'
        django.setup()
        TestRunner = get_runner(settings)
        test_runner = TestRunner()
        failures = test_runner.run_tests([app + ".tests"])
        if failures:
            sys.exit(bool(failures))
