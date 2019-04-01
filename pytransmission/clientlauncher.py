#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from resources.client import Client
from config import *

client = Client(ADDRESS, PORT, LOGIN, PASSWORD)

print('Connected to {0}:{1}'.format(ADDRESS, PORT))

torrents = client.get_torrents()
print('List of torrent ({0}):'.format(len(torrents)))
for torrent in torrents.values():
    print(torrent)
