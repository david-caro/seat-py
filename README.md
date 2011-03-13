#Seat-Python (0.2.2)
Python [CouchDB][1] wrapper: elegant, lightweight REST interface to CouchDB datastore and ORM capable

##License
MIT/X11 - See [LICENSE][2]

[1]: http://couchdb.apache.org/
[2]: http://github.com/stackd/seat-py/blob/master/LICENSE
  
##Motivation

> Apache CouchDB has started. Time to relax.

Working with CouchDB and Python should be equally effortless, elegant, and unobtrusive.

###Why Seat-Python?

* Simple and straightforward - Less schematizing and just pure Python
* Lightweight - From its source code to usability, Seat-Python excels at lightly wrapping Python to CouchDB
* Clean - Syntax emphasizes functionality, readability, and productivity
  
##Getting Started

**Overview**

Seat-Python is a full featured, lightweight, and extensible Python library for CouchDB. The *seat* module is divided into the following classes:

* Seat - REST wrapper for CouchDB
* Utils - Utilities for managing/updating views, as well data validation tools [*work in progress*]
* Cache - Redis caching layer for awesome performance [*coming soon*]
* Object - Bare-metal object-relational mapping, much like ActiveRecord for Ruby on Rails, except Pythonic and powered by CouchDB

**Dependencies**

* [PyYAML][3]

[3]: http://pyyaml.org/wiki/PyYAML

**Installation**
    
    $ git clone https://github.com/stackd/seat-py.git
    $ cd seat-py
    $ python setup.py install

Seat-Python can also be installed with [make][4].

    $ make install
    
**Verifying and testing**

After installing the library or when making contributions to the codebase, *make* can also automate the testing process and run all Seat-Python unit tests.

    $ make test
    
In addition, individual tests can be executed by make and are also in the *test/* directory.

    $ make test_seat
    $ make test_object
    
Finally, running tests through Python; CLI arguments are inherited from the [unittest][5] framework.

    $ python test/test_seat.py -v
    $ python test/test_object.py

[4]: http://www.gnu.org/software/make/
[5]: http://docs.python.org/library/unittest.html#command-line-interface

##Seat (REST wrapper) - Usage Basics

###Instantiate Seat

    from seat import Seat
    
**Without username/password**
    
    database = Seat('musicians')  # Assuming default host (localhost) and port (5984)
    database = Seat('http://couchdb.local:5986/musicians')  # Using nonstandard host and port
    
**With username/password**

    database = Seat('musicians', 'username', 'password')
    database = Seat('http://username:password@couchdb.local:5986/musicians')
    
*Note: By default, Seat does not check for the existence of the database you specify - instantiation merely maps the database to the Seat object.*

###Check existence of a database

    database.get()
    
If database does not exist, Seat will return:

    {'reason': 'no_db_file', 'error': 'not_found'}
    
###Create a new database

    database.put()
    
Return result:

    {'ok': True}
    
Now that our database exists, database.get() should return something like this:

    {'update_seq': 0, 'disk_size': 79, 'purge_seq': 0, 'doc_count': 0, 'compact_running': False, 'db_name': 'musicians', 'doc_del_count': 0, 'instance_start_time': '1298620518302926', 'committed_update_seq': 0, 'disk_format_version': 5}
    
###Working with documents

**Create a new document**

With a database created, let's put our first document in the database.

    document = {'_id': 'Musician.ericclapton', 'type': 'guitar', 'firstname': 'Eric', 'lastname': 'Clapton'}
    database.put(document)
    
Return result:
    
    {'rev': '1-6cb19bbd848c03eba28b070fbe18cd39', 'ok': True, 'id': 'Musician.ericclapton'}
    
**Retrieve, change, and update a document**

    musician = database.get('Musician.ericclapton')  # Retrieve
    musician['age'] = 65  # Add 'age' field
    database.put(musician)  # Update
    
Return result:

    {'rev': '3-206f96a9444614c72270422c2393af40', 'ok': True, 'id': 'Musician.ericclapton'}
    
**Deleting a document**

    musician = database.get('Musician.ericclapton')  # Retrieve
    database.delete(musician)  # Delete
    
Return result:

    {'rev': '4-49753b8dedfdd1a14091ae051a24277c', 'ok': True, 'id': 'Musician.ericclapton'}
    
###Using CouchDB views

The view() method allows for queries and reporting on CouchDB documents. 
It takes two required arguments, *design document* and *view name*, and an optional *key* argument. The ability to pass additional arguments, such as sorting (ascending or descending) is coming soon.

    database.view('musician', 'by_instrument', 'guitar')
    
Return result:

    """Result is returned as list item for each row returned by the view."""
    
    [
        {
            'value': 
                {
                    'lastname': 'Clapton', 
                    '_rev': '5-ed472711741b4e853909f25e3aa0342f',
                    '_id': 'Musician.ericclapton',
                    'type': 'guitar',
                    'firstname': 'Eric'
                },
            'id': 'Musician.ericclapton', 
            'key': 'guitar'
        }
    ]
    
##Object - Mapping objects to CouchDB documents

In addition to wrapping CouchDB's RESTful API to Python, Seat-Python extends this functionality with [object-relational mapping][4]. The ORM allows for seamless and simultaneous manipulation of Python objects and CouchDB documents.

[4]: http://en.wikipedia.org/wiki/Object-relational_mapping

###Creating a new Seat Object

Define a class to model a new object and map a database to store the object. For example, in an application dealing with musicians:
    
    import seat
    class Musician(seat.Object):
        database = seat.Seat('musicians')
        
Creating new CouchDB objects is as simple as instantiating the class and defining its attributes.

    musician = Musician(firstname = 'Geddy', lastname = 'Lee', type = 'bass', age = 57)
    
###Working with Objects in CouchDB

**Saving an object**

    musician.save()
    
This creates the following CouchDB document:

    {
       "_id": "Musician.a156031aa5c4b6e4691098cf4c3cb5876d800614",
       "_rev": "1-73af58fb4cb2eea2d967618a85320d35",
       "lastname": "Lee",
       "age": 57,
       "type": "bass",
       "firstname": "Geddy"
    }
    
*Note: By default, if an '_id' attribute is not defined at instantiation, seat.Object will create the _id as the class name and the sha1 checksum of the document contents.*

**Modifying and updating an object**

    musician['band'] = 'Rush'
    musician.update()
    
Return result:

    {'rev': '4-e76ded0e206460375bdf548e02381305', 'ok': True, 'id': 'Musician.a156031aa5c4b6e4691098cf4c3cb5876d800614'}
    
**Verifying the existence of an object in CouchDB**

    musician.exists()
    
Return result:

    True  # Boolean
    
**Retrieving an object from CouchDB**

    musician.get()

Return result:
    
    {
        'firstname': 'Geddy',
        'lastname': 'Lee',
        '_rev': '4-e76ded0e206460375bdf548e02381305',
        'band': 'Rush',
        '_id': 'Musician.a156031aa5c4b6e4691098cf4c3cb5876d800614',
        'type': 'bass',
        'age': 57
    }

**Creating objects from the existing object model**
    
A document _id argument can also be passed to the get() method and will return a new object based on your class.

    musician.get('Musician.ericclapton')
    
Return result:

    {
        'lastname': 'Clapton',
        '_rev': '5-ed472711741b4e853909f25e3aa0342f',
        '_id': 'Musician.ericclapton',
        'type': 'guitar',
        'firstname': 'Eric'
    }
    
This returns another instance of the Musician seat.Object that we defined earlier. 
Because of this, even documents that were not created with the ORM can behave just like any other seat.Object within an application.

For example:

    another_musician = musician.get('Musician.ericclapton')
    type(another_musician)  # <class '__main__.Musician'>
    another_musician.exists()  # True
    
**Saving a modified object as a new document**

Sometimes it's useful to maintain some of the same object attributes, but to differentiate them in CouchDB. 
For example, if we wanted to create a separate record for another band a musician was involved with:

    musician['band'] = 'Big Dirty Band'
    musician.save()
    
Return result:
    
    {'rev': '1-066db68a75a0a28f0ad704d5790cf26d', 'ok': True, 'id': 'Musician.5775a193023594f0d6b720bddecb1361796a67e7'}
    
This automatically created a new CouchDB document with a new '_id' and 'band' attribute:

    {
       "_id": "Musician.5775a193023594f0d6b720bddecb1361796a67e7",
       "_rev": "1-066db68a75a0a28f0ad704d5790cf26d",
       "band": "Big Dirty Band",
       "firstname": "Geddy",
       "lastname": "Lee",
       "age": 57,
       "type": "bass"
    }
    
**Deleting an object from CouchDB**

    musician.delete()
    
Return result:

    {'rev': '5-b46c7510030299850db0b6a0a5d5c746', 'ok': True, 'id': 'Musician.a156031aa5c4b6e4691098cf4c3cb5876d800614'}
    
Trying to retrieve that object from CouchDB will throw a SeatError:

    musician.exists()
    >> False
    musician.get()
    >> Traceback (most recent call last):
      File "/Library/Python/2.6/site-packages/seat.py", line 200, in get
        raise SeatError(404, 'Document not found.')
    seat.SeatError: Document not found.
    
###Seat-Python, future project milestones

Seat-Python is an ever evolving project. The following features/objectives are being worked on as of this writing (2011-03-08):

* Python 3 support
* Contribution guidelines and unit test suite
* CouchDB view management (via YAML)
* Fixing minor/rare httplib related issues

**Upcoming features:**

* Redis backed caching layer; super-fast document retrieval
