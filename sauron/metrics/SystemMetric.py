#! /usr/bin/env python
#
# Copyright (c) 2011 SEOmoz
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import psutil
import datetime
from sauron import logger
from sauron.metrics import Metric, MetricException

class SystemMetric(Metric):
    def values(self):
        try:
            loadavg1, loadavg5, loadavg15 = os.getloadavg()
        except OSError:
            loadavg1, loadavg5, loadavg15 = 0, 0, 0

        try:
            phys = psutil.virtual_memory()
            swap = psutil.swap_memory()
            return {'results': {
                    'physical': (phys.percent, 'Percent'),
                    'swap': (swap.percent, 'Percent'),
                    'loadavg1': (loadavg1, 'Count'),
                    'loadavg5': (loadavg5, 'Count'),
                    'loadavg15': (loadavg15, 'Count'),
                }
            }
        except OSError as e:
            raise MetricException(e)
        except psutil.AccessDenied as e:
            raise MetricException('Access denied in psutil')
