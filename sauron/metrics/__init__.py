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
import sys
from sauron import logger

# Append our current path before this import
p = os.path.dirname(os.path.abspath(__file__))
if p not in sys.path:
    sys.path.insert(0, p)

class MetricException(Exception):
  def __init__(self, message):
    self.msg = message
  def __repr__(self):
    return repr(self.msg)
  def __str__(self):
    return str(self.msg)

class Metric(object):
  def __init__(self, name, serializer, interval, *args, **kwargs):
    self.name = name
    self.serializer = serializer
    self.interval = interval
    self.keys = []
    self.reconfig(self, *args, **kwargs)
    
  def reconfig(self, *args, **kwargs):
    '''for each unknown keyword argument make it available in self context'''
    for k in kwargs.keys():
      self.__setattr__(k, kwargs[k])

  def getValues(self):
    if self.keys:
      results = self.values()
      pruned = {}
      for k in self.keys:
        try:
          pruned[k] = results['results'][k]
        except KeyError:
          logger.warn('Key %s unavailable' % k)
      results['results'] = pruned
      return results
    else:
      return self.values()
    
  def values(self):
    return {
      'results': {
        'key': (0, 'Count')
      },
      'time': datetime.datetime.now()
    }

class ExternalMetricQueueConsumer(Metric):
  def values(self):
    try:
      res = {}
      while not self.queue.empty():
        name, value, unit, method = self.queue.get_nowait()
        if res.has_key(name):
          res[name][0] += value
          res[name][3] += 1
        else:
          res[name] = [value, unit, method, 1]
        self.queue.task_done()

      for k,v in res.iteritems():
        if v[2] == 'persecond':
          # argreate to value/s
          v[0] = float(v[0] / self.interval)
        elif v[2] == 'avg':
          v[0] = float(v[0] / v[3])
        res[k] = tuple([v[0], v[1]])
      if not res:
        logger.info('No data from external metric listener received')
      return {'results': res}
    except Exception as e:
      raise MetricException(e)
