#!/usr/bin/python3
# -*- coding: utf-8 -*-

from resources.torrent import Torrent
from resources.torrent import TORRENT_STATUS
from datetime import date


class TorrentMatcher:
    """
    Abstract matcher class for torrent filtering
    """

    def match(self, torrent):
        """
        Verify if a torrent object match certain values
        :param torrent: the torrent instance to match
        :return: True is the torrent match
        """
        raise NotImplementedError("Bad matcher, not implemented")


class StatusTorrentMatcher(TorrentMatcher):
    """
    Matcher uses torrent's status
    """

    def __init__(self, status='stopped'):
        self.status = status

    def match(self, torrent):
        if not isinstance(torrent, Torrent):
            raise ValueError("The torrent argument must be a Torrent instance")
        if self.status not in TORRENT_STATUS.values():
            raise ValueError("The status '%s' is not a valid value" % self.status)
        return self.status == torrent.status


class RatioTorrentMatcher(TorrentMatcher):
    """
    Matcher uses torrent's upload ratio
    """

    def __init__(self, ratio=1.2):
        self.ratio = ratio

    def match(self, torrent):
        if not isinstance(torrent, Torrent):
            raise ValueError("The torrent argument must be a Torrent instance")
        if not isinstance(self.ratio, float):
            raise ValueError("The ratio must be a float")
        return self.ratio <= torrent.upload_ratio


class AddedDateTorrentMatcher(TorrentMatcher):
    """
    Matcher uses torrent's added date
    """

    def __init__(self, added_date=date.today()):
        self.added_date = added_date

    def match(self, torrent):
        if not isinstance(torrent, Torrent):
            raise ValueError("The torrent argument must be a Torrent instance")
        if not isinstance(self.added_date, date):
            raise ValueError("The ratio must be a date")
        return self.added_date >= torrent.added_date
