#!/usr/bin/python3
# -*- coding: utf-8 -*-

from datetime import date

TORRENT_STATUS = {
        0: 'stopped',
        1: 'check pending',
        2: 'checking',
        3: 'download pending',
        4: 'downloading',
        5: 'seed pending',
        6: 'seeding',
    }


def get_status(code):
    """
    Get the torrent status using status codes
    :param code: integer value
    :return: string representation of the status code
    """
    return TORRENT_STATUS[code]


def convert_byte_to_gigabyte(nb_byte):
    return nb_byte / 1000000


class Torrent:
    """
        Torrent class hold data returned by the Transmission daemon.
    """

    def __init__(self, data):
        if 'id' not in data:
            raise ValueError('Torrent requires an id')
        self.id = data['id']
        self.name = data['name']
        self.status_code = data['status']
        self.status = get_status(self.status_code)
        self.size = data['totalSize']
        self.download_dir = data['downloadDir']
        self.upload_ratio = data['uploadRatio']
        self.added_date = date.fromtimestamp(data['addedDate'])

    def __str__(self):
        size = convert_byte_to_gigabyte(self.size)
        return '%s %s (status : %s, size : %.2f mb, ratio : %s, date added : %s)' % (self.id, self.name, self.status,
                                                                                     size, self.upload_ratio,
                                                                                     self.added_date)
