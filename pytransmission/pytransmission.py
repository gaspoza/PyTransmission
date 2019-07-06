#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
from config import *
from resources.client import Client
from resources.torrent import TORRENT_STATUS
from resources.error import TransmissionError
from torrentmatcher import RatioTorrentMatcher, StatusTorrentMatcher, AddedDateTorrentMatcher
from datetime import datetime

LOGGER = logging.getLogger('__name__')
LOGGER.setLevel(logging.INFO)

# create console handler
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
ch.setFormatter(formatter)

LOGGER.addHandler(ch)


def get_torrents_from_args():
    filtered_torrents = {}
    torrents = client.get_torrents()
    if matchers:
        for torrent in torrents.values():
            if match(torrent):
                filtered_torrents[torrent.id] = torrent
        return filtered_torrents
    else:
        return torrents


def match(torrent):
    for matcher in matchers:
        if not matcher.match(torrent):
            return False
    return True


def list_torrents():
    torrents = get_torrents_from_args()
    print('Number of torrents: ', len(torrents))
    for torrent in torrents.values():
        print(torrent)
    return torrents


def move_torrent_data(torrent_ids, destination=DESTINATION_DIR):
    """
    Move torrent data
    :param torrent_ids: Torrent ids to be moved
    :param destination: destination path
    :return: None
    """
    if not isinstance(torrent_ids, list):
        raise TransmissionError("Method requires the argument as a list")
    client.move_torrent_data(torrent_ids, destination)


def move_torrents():
    torrents = get_torrents_from_args()
    ids = []
    for torrent in torrents.values():
        LOGGER.info("Add torrent for setting data destination folder: " + str(torrent))
        ids.append(torrent.id)
    move_torrent_data(ids)
    LOGGER.info("Done! %s torrents data moved" % len(ids))


def remove_torrent(torrent_ids):
    """
    Removing torrents from list
    :param torrent_ids: Torrent ids to be removed
    :return: None
    """
    if not isinstance(torrent_ids, list):
        raise TransmissionError("Method requires the argument as a list")
    client.remove_torrent(torrent_ids, False)


def clean_torrents():
    torrents = get_torrents_from_args()
    ids = []
    for torrent in torrents.values():
        LOGGER.info("Removing the torrent: " + str(torrent))
        ids.append(torrent.id)
    remove_torrent(ids)
    LOGGER.info("Done! %s torrents removed from list" % len(ids))


def move_and_clean_torrents():
    torrents = get_torrents_from_args()
    ids = []
    for torrent in torrents.values():
        ids.append(torrent.id)
    move_torrent_data(ids)
    remove_torrent(ids)
    LOGGER.info("Done! %s torrents data location changed and removed from list" % len(ids))


def mk_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)


LOGGING_LEVEL_MAP = {'info': logging.INFO,
                     'debug': logging.DEBUG,
                     'error': logging.ERROR}

FUNCTION_MAP = {'list': list_torrents,
                'move': move_torrents,
                'clean': clean_torrents,
                'organize': move_and_clean_torrents}

parser = argparse.ArgumentParser()
parser.add_argument('command', choices=FUNCTION_MAP.keys())
parser.add_argument("--hostname", help="set the hostname", default=ADDRESS)
parser.add_argument("--port", help="set the port", type=int, default=PORT)
parser.add_argument("-l", "--login", help="set the login", default=LOGIN)
parser.add_argument("-p", "--password", help="set the password", default=PASSWORD)
parser.add_argument("-v", "--verbosity", help="set logging level", choices=LOGGING_LEVEL_MAP.keys(), default='error')

# filtering
filter_group = parser.add_argument_group('Torrent filtering')
filter_group.add_argument("-fr", "--filter_ratio", type=float)
filter_group.add_argument("-fs", "--filter_status", choices=TORRENT_STATUS.values())
filter_group.add_argument("-fd", "--filter_date", type=mk_date)

args = parser.parse_args()
# args = parser.parse_args(['list'])
# args = parser.parse_args(['list', '-fs', 'stopped'])
# args = parser.parse_args(['organize', '-fs', 'stopped'])
# args = parser.parse_args(['organize', '-fd', '2017-07-01'])
# args = parser.parse_args(['organize', '-fs', 'stopped'])

client = Client(args.hostname, args.port, args.login, args.password)
logging.getLogger('pytransmission.client').setLevel(LOGGING_LEVEL_MAP[args.verbosity])

matchers = []
if args.filter_ratio:
    ratio = args.filter_ratio
    matchers.append(RatioTorrentMatcher(ratio))
if args.filter_status:
    status = args.filter_status
    matchers.append(StatusTorrentMatcher(status))
if args.filter_date:
    added_date = args.filter_date
    matchers.append(AddedDateTorrentMatcher(added_date))

func = FUNCTION_MAP[args.command]
func()
