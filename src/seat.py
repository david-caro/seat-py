#!/usr/bin/env python
# encoding: utf-8
"""
Seat-Python (0.1.1)
Python CouchDB Wrapper
http://github.com/stackd/seat-py

DOCUMENTATION
----------------------------------------
see README.md

LICENSE
----------------------------------------
MIT, see LICENSE

DEPENDENCIES
----------------------------------------
Python 2.x.x

"""
import re
import urlparse
import string
import base64
import httplib
import json

class Seat(object):
    
    HOST = 'localhost'
    PORT = '5984'
    USER_AGENT = 'Seat-Python (0.1)'
    
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
            
    def __send(self, method, args):
        """
        Private class method to handle most HTTP requests.
        """
        if (args == None):
            self.resource.request(method, u'/'+self.database, None, self.headers)
            request = self.resource.getresponse()
            return json.loads(request.read())
        elif (args != None):
            self.resource.request(method, u'/'+self.database+u'/'+str(args), None, self.headers)
            request = self.resource.getresponse()
            return json.loads(request.read())
            
    def get(self, doc = None):
        """
        Given no arguments, will return status of the database as <type 'dict'>, else it will return a document given an _id.
        """
        return self.__send(u'GET', doc)
        
    def post(self, path = None):
        """
        Calls a variety of CouchDB functions such as _compact.
        """
        return self.__send(u'POST', path)
        
    def put(self, doc = None):
        """
        Given no arguments, this method will create a new database as instantiated; else it is the primary method to update or create a document.
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
        """
        Given no arguments, this method will delete the entire database. Otherwise, it will delete a document given an _id and _rev.
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
            
class SeatError(Exception):
    def __init__(self, type, message):
            Exception.__init__(self, message)
            self.type = type