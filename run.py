#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import unittest

from test_plan import plan


if __name__ == '__main__':
    loader = unittest.TestLoader()
    plan = loader.loadTestsFromNames(plan)
    runner = unittest.TextTestRunner(
        stream=sys.stdout,
        descriptions=True,
        verbosity=2
    )
    runner.run(plan)
