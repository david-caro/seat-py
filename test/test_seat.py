#!/usr/bin/env python
# encoding: utf-8
import time
import unittest
import seat


DATABASE = 'seat_554e4b55e8cc57f39f16f335b0a63825'
USER = 'admin'
PASSWORD = 'admin'


class testSeat(unittest.TestCase):
    """Test REST wrapper"""
    def setUp(self):
        self.doc = {'_id': '554e4b55e8cc57f39f16f335b0a63825'}
        self.database = seat.Seat(DATABASE, USER, PASSWORD)
        self.database.put()

    def tearDown(self):
        self.database.delete()

    def test_database_exists(self):
        """Database exists"""
        response = 'seat_554e4b55e8cc57f39f16f335b0a63825'
        self.assertEqual(self.database.get()['db_name'], response)

    def test_document_get(self):
        """GET document"""
        self.test_document_put()
        response = {'_rev': '1-967a00dff5e02add41819138abb3284d', '_id': '554e4b55e8cc57f39f16f335b0a63825'}
        self.assertEqual(self.database.get('554e4b55e8cc57f39f16f335b0a63825'), response)

    def test_document_put(self):
        """PUT document"""
        response = {'rev': '1-967a00dff5e02add41819138abb3284d', 'ok': True, 'id': '554e4b55e8cc57f39f16f335b0a63825'}
        self.assertEqual(self.database.put(self.doc), response)

    def test_document_delete(self):
        """DELETE document"""
        self.test_document_put()
        response = {'rev': '2-eec205a9d413992850a6e32678485900', 'ok': True, 'id': '554e4b55e8cc57f39f16f335b0a63825'}
        self.doc['_rev'] = '1-967a00dff5e02add41819138abb3284d'
        self.assertEqual(self.database.delete(self.doc), response)

    def test_document_update(self):
        """Update existing document"""
        self.test_document_put()
        response = {'rev': '2-0cd83c73e5f99f0b1b518057f7257e69', 'ok': True, 'id': '554e4b55e8cc57f39f16f335b0a63825'}
        document = self.database.get('554e4b55e8cc57f39f16f335b0a63825')
        document['test'] = 'test-554e4b55e8cc57f39f16f335b0a63825'
        self.assertEqual(self.database.put(document), response)

    def test_view_create(self):
        pass

    def test_view_query(self):
        pass

if __name__ == '__main__':
    unittest.main()
