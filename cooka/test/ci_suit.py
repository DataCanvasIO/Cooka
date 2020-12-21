# -*- encoding: utf-8 -*-
import unittest

suit = unittest.TestSuite()
tests = unittest.defaultTestLoader.discover(start_dir='.')

runner = unittest.TextTestRunner()
runner.run(tests)
