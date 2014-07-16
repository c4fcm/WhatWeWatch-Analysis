import inspect
import os
import sys
import unittest

import numpy as np
import numpy.testing as nptest

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

import statistics
import stubs
import util

class StatisticsTest(unittest.TestCase):
    def setUp(self):
        self.video_data = util.VideoData(stubs.raw)
        self.spread_span = statistics.SpreadSpan(self.video_data)
    
    def test_span(self):
        self.assertEqual(self.spread_span.span_by_vid, stubs.span_by_vid)
        
    def test_spread(self):
        self.assertEqual(self.spread_span.spread_by_vid, stubs.spread_by_vid)
    
if __name__ == '__main__':
    unittest.main()
    