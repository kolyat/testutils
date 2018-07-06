#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import settings


test_plan = [
    os.path.join('test_ui', 'test_megaruss.py')
]

load_plan = {
    'locustfile': os.path.join('load_test', 'auth.py'),
    'host': settings.BASE_URL,
    'num_requests': 10,
    'num_clients': 1,
    'hatch_rate': 1
}


if __name__ == '__main__':
    #
    # Functional tests
    #
    import pytest
    pytest.main(args=test_plan)

    # Alternative code
    # Test plan must have specified format:
    # test_plan = [
    #     'test_suite.TestCaseExample'
    # ]
    # TestCaseExample must be imported inside __init__.py of test_suite module
    #
    # import sys
    # import unittest
    # loader = unittest.TestLoader()
    # plan = loader.loadTestsFromNames(test_plan)
    # runner = unittest.TextTestRunner(
    #     stream=sys.stdout,
    #     descriptions=True,
    #     verbosity=2
    # )
    # runner.run(plan)

    #
    # Load test
    #
    # import invokust
    # locust_settings = invokust.create_settings(**load_plan)
    # load_test = invokust.LocustLoadTest(locust_settings)
    # load_test.run()
    # load_test.stats()
