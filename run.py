#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse

import settings


test_ui_plan = [
    os.path.join('test_ui', 'test_megaruss.py'),
    '--browser=chrome'
]

load_plan = {
    'locustfile': os.path.join('load_test', 'auth.py'),
    'host': settings.BASE_URL,
    'num_requests': 10,
    'num_clients': 1,
    'hatch_rate': 1
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test launcher')
    parser.add_argument('-u', '--ui', action='store_true',
                        default=False, required=False,
                        help='run UI tests', dest='ui')
    parser.add_argument('-l', '--load', action='store_true',
                        default=False, required=False,
                        help='run load tests', dest='load')
    args = parser.parse_args()

    # UI tests
    if args.ui:
        import pytest
        pytest.main(args=test_ui_plan)

    # API tests
    #
    # This code can be used for collecting and running API tests, based on
    # unittest library. Test plan must have specified format:
    # test_api_plan = [
    #     'test_suite.TestCaseExample'
    # ]
    # TestCaseExample must be imported inside __init__.py of test_suite module
    #
    # import unittest
    # loader = unittest.TestLoader()
    # plan = loader.loadTestsFromNames(test_plan)
    # runner = unittest.TextTestRunner(
    #     stream=sys.stdout,
    #     descriptions=True,
    #     verbosity=2
    # )
    # runner.run(plan)

    # Load test
    if args.load:
        import invokust
        locust_settings = invokust.create_settings(**load_plan)
        load_test = invokust.LocustLoadTest(locust_settings)
        load_test.run()
        load_test.stats()

    if len(sys.argv) < 2:
        print('Nothing to run')
        parser.print_usage()
