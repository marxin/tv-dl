#!/usr/bin/env python3

__author__ = "Martin Liška"
__desc__ = "Stream.cz"
__url__ = r"http?://www\.stream\.cz/.+"

import re,os.path
import json
import itertools
from urllib.request import urlopen
from urllib.parse import urlencode
from os.path import basename
import logging
from pyquery import PyQuery

log = logging.getLogger()

def get_key(t):
  return t['format'] + '_' + t['quality']

class StreamEngine:
    def __init__(self, url):
        self.url = url
        self.page = urlopen(url).read().decode('utf-8')
        self.playlist = []
        self.get_playlist()

        if len(self.playlist) == 0:
            raise ValueError('Není k dispozici žádná kvalita videa.')

    def get_playlist(self):
      pq = PyQuery(self.page)
      l = list(filter(lambda x: x.startswith('Stream.Data.Episode.PRELOADED'), pq('script').map(lambda i, e: PyQuery(e).text())))
      if len(l) == 0:
        return
      content = l[0]
      content = re.sub('\);$', '', re.sub('^[^\(]+\(', '', content))
      data = json.loads(content)
      self.name = data['episode_url']

      self.playlist = []
      for i in data['instances']:
        videos = i['instances']
        self.playlist = self.playlist + list(map(lambda x: {'quality': x['quality'], 'format': x['type'].split('/')[1], 'url': x['source']}, videos))

    def qualities(self):
      return map(lambda x: (get_key(x), x['quality'] + ' ' +x['format']), self.playlist)

    def movies(self):
      return []

    def download(self, quality, movie):
      video = None
      if quality == None:
        video =self.playlist[0]
      else:
        video = next(x for x in self.playlist if get_key(x) == quality)

      return ('http', self.name + '.' + video['format'], { 'url': video['url'] })
