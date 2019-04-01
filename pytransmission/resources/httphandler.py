#!/usr/bin/python3
# -*- coding: utf-8 -*-

from urllib.request import Request, build_opener, HTTPPasswordMgrWithDefaultRealm, HTTPBasicAuthHandler, \
    HTTPDigestAuthHandler


class HttpHandler:
    """
    The default HTTP handler to communicate to Transmission daemon
    """
    def __init__(self):
        self.http_opener = build_opener()

    def set_authentication(self, uri, login, password):
        password_manager = HTTPPasswordMgrWithDefaultRealm()
        password_manager.add_password(realm=None, uri=uri, user=login, passwd=password)
        self.http_opener = build_opener(HTTPBasicAuthHandler(password_manager), HTTPDigestAuthHandler(password_manager))

    def request(self, url, query, headers, timeout):
        request = Request(url, query.encode('utf-8'), headers)
        response = self.http_opener.open(request, timeout=timeout)
        return response.read().decode('utf-8')
