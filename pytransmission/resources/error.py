#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class TransmissionError(Exception):
    """
    This exception is raised when there has occurred an error related to
    communication with Transmission daemon. It is a subclass of Exception.
    """

    def __init__(self, message='', original=None):
        Exception.__init__(self)
        self.message = message
        self.original = original

    def __str__(self):
        if self.original:
            original_name = type(self.original).__name__
            return '%s Original exception: %s, "%s"' % (self.message, original_name, str(self.original))
        else:
            return self.message
