#!/usr/bin/env python
# encoding: utf-8
"""
Seat-Python (0.2.4)
Python CouchDB Wrapper
https://github.com/stackd/seat-py

DOCUMENTATION
----------------------------------------
see README.md

LICENSE
----------------------------------------
MIT/X11, see LICENSE

DEPENDENCIES
----------------------------------------
Python 2.x.x

"""
import os
import re
import urlparse
import urllib
import string
import base64
import httplib
import hashlib
import yaml
try:
    import simplejson as json
except ImportError:
    import json

__author__ = 'Fredrick Galoso'
__version__ = '0.2.4'


class Seat(object):

    HOST = 'localhost'
    PORT = '5984'
    USER_AGENT = 'Seat-Python (0.2.4)'

    def __init__(self, database='', username=None, password=None):
        if re.match(r'^http\://|^https://', database):
            uri = urlparse.urlparse(database)
            database = uri.path[1:]
            username = uri.username
            password = uri.password
            self.HOST = uri.hostname
            self.PORT = str(uri.port)
        self._username = username
        self._password = password
        if username == None and password == None:
            self.resource = httplib.HTTPConnection(self.HOST, self.PORT)
            self.headers = {'Content-Type': 'application/json', 'User-Agent': self.USER_AGENT}
        else:
            self.resource = httplib.HTTPConnection(self.HOST, self.PORT)
            auth = string.strip(base64.b64encode('%s:%s' % (username, password)))
            self.headers = {'Content-Type': 'application/json', 'User-Agent': self.USER_AGENT, 'Authorization': 'Basic %s' % auth}
        self.database = database

        self.Utils = Utils(self)
        self.Cache = Cache(self)

    def __connect(self):
        username = self._username
        password = self._password
        if username == None and password == None:
            self.resource = httplib.HTTPConnection(self.HOST, self.PORT)
            self.headers = {'Content-Type': 'application/json', 'User-Agent': self.USER_AGENT}
        else:
            self.resource = httplib.HTTPConnection(self.HOST, self.PORT)
            auth = string.strip(base64.b64encode('%s:%s' % (username, password)))
            self.headers = {'Content-Type': 'application/json', 'User-Agent': self.USER_AGENT, 'Authorization': 'Basic %s' % auth}

    def __send(self, method, args):
        """Private class method to handle most HTTP requests."""
        self.__connect()

        if (args == None):
            self.resource.request(method, '/' + self.database, None, self.headers)
            request = self.resource.getresponse()
            result = json.loads(request.read())
            self.resource.close()
            return result
        elif (args != None):
            self.resource.request(method, '/' + self.database + '/' + str(args), None, self.headers)
            request = self.resource.getresponse()
            result = json.loads(request.read())
            self.resource.close()
            return result

    def get(self, doc=None):
        """Given no arguments, will return status of the database as <type 'dict'>, else it will return a document given an _id.
        """
        return self.__send('GET', doc)

    def post(self, path=None):
        """Calls a variety of CouchDB functions such as _compact."""
        return self.__send('POST', path)

    def put(self, doc=None):
        """Given no arguments, this method will create a new database as instantiated; else it is the primary method to update or create a document.
            Creating a new database:
                db = Seat('new_database')
                db.put()
            Create a document within an existing database:
                db = Seat('existing_database')
            Define a document as a dictionary:
                doc = {'_id':'users.kennypowers', 'type':'user', 'username':'kennypowers'}
            Update database with new document:
                db.put(doc)
        """
        self.__connect()

        if type(doc).__name__ == 'dict':
            self.resource.request('PUT', '/' + self.database + '/' + str(doc['_id']), json.dumps(doc), self.headers)
            request = self.resource.getresponse()
            result = json.loads(request.read())
            self.resource.close()
            return result
        else:
            return self.__send('PUT', doc)

    def delete(self, doc=None):
        """Given no arguments, this method will delete the entire database. Otherwise, it will delete a document given an _id and _rev.
            Deleting an entire database:
                db = Seat('existing_database')
                db.delete()
            Delete an existing document:
                db = Seat('existing_database')
                doc = db.get({'_id':'users.kennypowers'})
                db.delete(doc)
        """
        self.__connect()

        if type(doc).__name__ == 'dict':
            self.resource.request('DELETE', '/' + self.database + '/' + str(doc['_id']) + '/?rev=' + str(doc['_rev']), None, self.headers)
            request = self.resource.getresponse()
            result = json.loads(request.read())
            self.resource.close()
            return result
        else:
            return self.__send('DELETE', doc)

    def view(self, ddoc, view, **kwargs):
        """Returns view based on design document, view, and key.
            db = Seat('existing_database')
            db.view('user', 'by_first_name', 'Kenny')
        """
        self.__connect()

        uri = '/%s/_design/%s/_view/%s' % (self.database, ddoc, view)
        for index, key in enumerate(kwargs):
            if index == 0:
                uri += '?%s=%s' % (key,
                        urllib.quote(kwargs[key].replace(' ', ''),
                    '/:,'))
            else:
                uri += '&%s=%s' % (key,
                        urllib.quote(kwargs[key].replace(' ', ''),
                    '/:,'))

        self.resource.request('GET', uri, None, self.headers)
        request = self.resource.getresponse()
        result = json.loads(request.read())['rows']
        self.resource.close()
        return result


class Utils(object):
    """Utilities for updating views and data validation."""

    def __init__(self, seat, path=None):
        self.seat = seat
        self.path = path

    def push_views(self):
        if self.path == None:
            self.path = os.getcwd() + '/config/'
        for files in os.walk(self.path):
            for yaml_file in files[len(files) - 1]:
                if yaml_file.find('.yaml'):
                    view = file(self.path + yaml_file, 'r')
                    print(yaml.load(view))


class Cache(object):
    """Redis caching layer."""

    def __init__(self, seat):
        self.seat = seat
    pass


class Object(dict):
    """Bare-metal ORM awesomeness.
            Create a new object model to be saved in CouchDB:

            import seat
            class User(seat.Object):
                database = seat.Seat('musicians')
            user = User(firstname = 'Eric', lastname = 'Clapton', instrument = 'guitar', age = 65)
            user['firstname'] #Eric
            user.exists() #False
            user.save() #Saves user to database
            user.exists() #True
            user.delete() #Deletes user
            user.delete() #Throws SeatError(404) - Document not found.
    """

    def __init__(self, **kwargs):
        for key in kwargs:
            self[key] = kwargs[key]
        if '_id' not in kwargs:
            self['_id'] = self.__class__.__name__ + '.' + hashlib.sha1(str(self)).hexdigest()
            self.user_defined_id = False
        else:
            self['_id'] = kwargs['_id']
            self.user_defined_id = True

    def __hash(self):
        """SHA1 checksum object contents."""
        contents = {}
        for key in self:
            if key != '_id':
                contents[key] = self[key]
        return hashlib.sha1(str(contents)).hexdigest()

    def exists(self):
        response = self.database.get(self['_id'])
        if ('error' in response):
            return False
        else:
            return True

    def get(self, _id=None):
        if _id != None:
            request = self.database.get(_id)
            doc = self.__class__()
            for key in request:
                    doc[key] = request[key]
            return doc
        else:
            response = self.database.get(self['_id'])
            if ('error' in response):
                raise SeatError(404, 'Document not found.')
            else:
                return response

    def update(self):
        response = self.database.get(self['_id'])
        self['_rev'] = response['_rev']
        return self.database.put(dict(self))

    def save(self):
        response = self.database.put(dict(self))
        if ('error' in response and response['error'] == 'conflict' and not self.user_defined_id):
            #Verify that contents of the object have not changed
            self['_id'] = self.__class__.__name__ + '.' + self.__hash()
            return self.database.put(dict(self))

    def delete(self):
        try:
            if (self.exists):
                self['_rev'] = self.database.get(self['_id'])['_rev']
                response = self.database.delete(dict(self))
                return response
        except KeyError:
            raise SeatError(404, 'Document not found.')


class SeatError(Exception):

    def __init__(self, type, message):
            Exception.__init__(self, message)
            self.type = type
