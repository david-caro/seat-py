#!/usr/bin/env python
# encoding: utf-8
"""
Seat-Python (0.2.1)
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
import string
import base64
import httplib
import json
import hashlib
import yaml

__author__ = 'Fredrick Galoso'
__version__ = '0.2.1'
        
class Seat(object):
    
    HOST = 'localhost'
    PORT = '5984'
    USER_AGENT = 'Seat-Python (0.2.1)'
    
    def __init__(self, database = '', username = None, password = None):
        if re.match(r'^http\://|^https://', database):
            uri = urlparse.urlparse(database)
            database = uri.path[1:]
            username = uri.username
            password = uri.password
            self.HOST = uri.hostname
            self.PORT = str(uri.port)
        if username == None and password == None:
            self.resource = httplib.HTTPConnection(self.HOST+u':'+self.PORT)
            self.headers = {'Content-Type' : 'application/json', 'User-Agent' : self.USER_AGENT}
        else:
            self.resource = httplib.HTTPConnection(self.HOST+u':'+self.PORT)
            self.headers = {'Content-Type' : 'application/json', 'User-Agent' : self.USER_AGENT, 'Authorization' : 'Basic '+string.strip(base64.encodestring(username+':'+password))}
        self.database = database
        
        self.Utils = Utils(self)
        self.Cache = Cache(self)
            
    def __send(self, method, args):
        """Private class method to handle most HTTP requests."""
        if (args == None):
            self.resource.request(method, u'/'+self.database, None, self.headers)
            request = self.resource.getresponse()
            return json.loads(request.read())
        elif (args != None):
            self.resource.request(method, u'/'+self.database+u'/'+str(args), None, self.headers)
            request = self.resource.getresponse()
            return json.loads(request.read())
            
    def get(self, doc = None):
        """Given no arguments, will return status of the database as <type 'dict'>, else it will return a document given an _id.
        """
        return self.__send(u'GET', doc)
        
    def post(self, path = None):
        """Calls a variety of CouchDB functions such as _compact."""
        return self.__send(u'POST', path)
        
    def put(self, doc = None):
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
        if type(doc).__name__ == 'dict':
            self.resource.request(u'PUT', u'/'+self.database+u'/'+str(doc['_id']), json.dumps(doc), self.headers)
            request = self.resource.getresponse() 
            return json.loads(request.read())
        else:
            return self.__send(u'PUT', doc)
            
    def delete(self, doc = None):
        """Given no arguments, this method will delete the entire database. Otherwise, it will delete a document given an _id and _rev.
            Deleting an entire database:
                db = Seat('existing_database')
                db.delete()
            Delete an existing document:
                db = Seat('existing_database')
                doc = db.get({'_id':'users.kennypowers'})
                db.delete(doc)
        """
        if type(doc).__name__ == 'dict':
            self.resource.request(u'DELETE', '/'+self.database+'/'+str(doc['_id'])+u'/?rev='+str(doc['_rev']), None, self.headers)
            request = self.resource.getresponse()
            return json.loads(request.read())
        else:
            return self.__send(u'DELETE', doc)
    
    def view(self, ddoc, view, key = None, args = None):
        """Returns view based on design document, view, and key.
            db = Seat('existing_database')
            db.view('user', 'by_first_name', 'Kenny')
        """
        if key != None:
            uri = '/%s/_design/%s/_view/%s?key=%s' % (self.database, ddoc, view, json.dumps(key))
        else:
            uri = '/%s/_design/%s/_view/%s' % (self.database, ddoc, view)
            
        self.resource.request(u'GET', uri, None, self.headers)
        request = self.resource.getresponse()
        return json.loads(request.read())['rows']
        
class Utils(object):
    """Utilities for updating views and data validation."""
    def __init__(self, seat, path = None):
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
        self['_id'] = self.__class__.__name__ + '.' +hashlib.sha1(str(self)).hexdigest()
        
    def exists(self):
        response = self.database.get(self['_id'])
        if ('error' in response):
            return False
        else:
            return True
    
    def save(self):
        response = self.database.put(dict(self))
        if ('error' in response and response['error'] == 'conflict'):
            #Verify that contents of the object have not changed
            contents = {}
            for key in self:
                if key != '_id':
                    contents[key] = self[key]
            self['_id'] = self.__class__.__name__ + '.' +hashlib.sha1(str(contents)).hexdigest()
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