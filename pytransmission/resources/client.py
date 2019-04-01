#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from .httphandler import HttpHandler
from .error import TransmissionError
from .torrent import Torrent
from urllib.parse import urlparse
from urllib.error import HTTPError, URLError
import logging
import json
import time


LOGGER = logging.getLogger('pytransmission.client')
LOGGER.setLevel(logging.ERROR)


class Client:
    """
    Client is the class handling the Transmission JSON-RPC client protocol.
    """

    def __init__(self, address='localhost', port=9091, user=None, password=None):
        self.address = address
        self.port = port
        self.user = user
        self.password = password

        self._setup_url()
        self._http_handler = HttpHandler()
        if password and password:
            LOGGER.debug('Setting up basic authentication')
            self._set_authentication()
        else:
            LOGGER.debug('No basic authentication setup')
        self._sequence = 0
        self.session_id = None
        self._query_timeout = 300.0

    def _setup_url(self):
        url = urlparse(self.address)
        if url.scheme == '':
            base_url = 'http://' + self.address + ':' + str(self.port)
            self.url = base_url + '/transmission/rpc'
        else:
            if url.port:
                self.url = url.scheme + '://' + url.hostname + ':' + str(url.port) + url.path
            else:
                self.url = url.scheme + '://' + url.hostname + url.path
            print('Using custom URL ' + self.url)

    def _set_authentication(self):
        """
        Setting up the basic authentication for querying transmission daemon
        """
        self._http_handler.set_authentication(self.url, self.user, self.password)

    def _http_query(self, query, timeout=None):
        """
        Query Transmission through HTTP.
        """
        headers = {'x-transmission-session-id': str(self.session_id)}
        request_count = 0
        if timeout is None:
            timeout = self._query_timeout
        while True:
            LOGGER.debug(json.dumps({'url': self.url, 'headers': headers,
                                     'query': query, 'timeout': timeout}, indent=2))
            try:
                result = self._http_handler.request(self.url, query, headers, timeout)
            except HTTPError as error:
                if error.code == 409:
                    LOGGER.info('Server responded with 409, trying to set session-id.')
                    if request_count > 1:
                        raise TransmissionError('Session ID negotiation failed.', error)
                    session_id = None
                    for key in list(error.headers.keys()):
                        if key.lower() == 'x-transmission-session-id':
                            session_id = error.headers[key]
                            self.session_id = session_id
                            headers = {'x-transmission-session-id': str(self.session_id)}
                    if session_id is None:
                        raise TransmissionError('Unknown conflict.', error)
                else:
                    print('The server couldn\'t fulfill the request.')
                    print('Error code: ', error.code)
                    raise TransmissionError('Request failed.', error)
            except URLError as error:
                print('We failed to reach a server.')
                print('Reason: ', error.reason)
            else:
                # everything is fine
                return result
            request_count += 1

    def _request(self, query, timeout=None):
        """
        Send json-rpc request to Transmission using http POST
        """

        start = time.time()
        http_data = self._http_query(query, timeout)
        elapsed = time.time() - start
        LOGGER.info('http request took %.3f s' % elapsed)

        try:
            data = json.loads(http_data)
        except ValueError as error:
            LOGGER.error('Error: ' + str(error))
            LOGGER.error('Request: \"%s\"' % query)
            LOGGER.error('HTTP data: \"%s\"' % http_data)
            raise

        LOGGER.debug(json.dumps(data, indent=2))
        if 'result' in data:
            if data['result'] != 'success':
                raise TransmissionError('Query failed with result \"%s\".' % (data['result']))
        else:
            raise TransmissionError('Query failed without result.')
        return data

    def get_torrents(self, arguments=None, timeout=None):
        """
        Get torrent list from Transmission daemon
        :param arguments: Fields for each torrent
        :param timeout:
        :return: a map of Torrent object with id as key
        """

        if not arguments:
            arguments = ['id', 'name', 'status', 'totalSize', 'uploadRatio', 'downloadDir', 'addedDate']
        elif not isinstance(arguments, dict):
            raise ValueError('request takes arguments as dict')

        self._sequence += 1
        query = json.dumps({'tag': self._sequence, 'method': 'torrent-get', 'arguments': {'fields': arguments}})
        json_data = self._request(query, timeout)

        results = {}
        for item in json_data['arguments']['torrents']:
            results[item['id']] = Torrent(item)
        return results

    def move_torrent_data(self, ids, location, timeout=None):
        """
        Move torrent data to the new location.
        :param ids: Ids of the torrents to be moved as an array
        :param location: the new location where the torrents should be moved
        :param timeout:
        """
        if len(ids) == 0:
            raise ValueError('request require ids')

        self._sequence += 1
        args = {'ids': ids, 'location': location, 'move': True}
        query = json.dumps({'tag': self._sequence, 'method': 'torrent-set-location', 'arguments': args})
        self._request(query, timeout)

    def remove_torrent(self, ids, delete_data=False, timeout=None):
        """
        Remove torrent(s) with provided id(s).
        Local data is removed if delete_data is True, otherwise not.
        :param ids: Ids of the torrents to be removed as an array
        :param delete_data: boolean value to keep or not data files
        :param timeout:
        """
        if not isinstance(delete_data, bool):
            raise ValueError('request takes boolean value for delete_data params')

        self._sequence += 1
        args = {'delete-local-data': 1 if bool(delete_data) else 0, 'ids': ids}
        query = json.dumps({'tag': self._sequence, 'method': 'torrent-remove', 'arguments': args})
        self._request(query, timeout)
