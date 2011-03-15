#!/usr/bin/env python
# encoding: utf-8
import time
import unittest
import seat


DATABASE = 'seat_554e4b55e8cc57f39f16f335b0a63825'
USER = 'admin'
PASSWORD = 'admin'


class Test(seat.Object):
    database = seat.Seat(DATABASE, USER, PASSWORD)


class testObject(unittest.TestCase):
    "Test ORM"
    def setUp(self):
        self.object = Test(
                        string='test-554e4b55e8cc57f39f16f335b0a63825',
                        integer=123,
                        float=3.14159265,
                        array=['thing 1', 'thing 2', 'thing 3'],
                        tuple=('string', 123, 3.14159265),
                        dictionary={'this 1': 'that 1', 'this 2': 'that 2'},
                        tuples_in_array=[('string', 123, 3.14159265), ('string', 456, 3.14159265)],
                        arrays_in_tupple=(['thing 1', 'thing 2', 'thing 3'], ['thing 4', 'thing 5', 'thing 6']),
                        complex_nested_mixed_data_types=(
                            {
                                'tuples_in_array_in_dictionary_in_tupple': [('string', 123, 3.14159265), ('string', 456, 3.14159265)]
                            },
                            [0, 1, 2, {'three': 3}, (4, 5, 6, (7, 8, [9, 10], {'eleven': 11}))]
                        )
                    )
        self.object.database.put()

    def tearDown(self):
        self.object.database.delete()

    def test_object_save(self):
        """Save object"""
        self.assertEqual(self.object.save(), None)

    def test_object_exists(self):
        """Object exists"""
        self.assertEqual(self.object.exists(), False)
        self.test_object_save()
        self.assertEqual(self.object.exists(), True)

    def test_object_get(self):
        """Get object"""
        try:
            self.object.get()
        except seat.SeatError:
            pass
        else:
            fail('Expected SeatError (HTTP 404 - Document not found)')
        self.test_object_save()
        response = {
                        'arrays_in_tupple': [
                            [
                                'thing 1',
                                'thing 2',
                                'thing 3'
                            ],
                            [
                                'thing 4',
                                'thing 5',
                                'thing 6'
                            ]
                        ],
                        'string': 'test-554e4b55e8cc57f39f16f335b0a63825',
                        'dictionary': {
                            'this 2': 'that 2',
                            'this 1': 'that 1'
                        },
                        'tuple': [
                            'string',
                            123,
                            3.1415926500000002
                        ],
                        '_rev': '1-977712a18ea22346bc616baaacc218ba',
                        'float': 3.1415926500000002,
                        'complex_nested_mixed_data_types': [
                            {
                                'tuples_in_array_in_dictionary_in_tupple': [
                                    [
                                        'string',
                                        123,
                                        3.1415926500000002
                                    ],
                                    [
                                        'string',
                                        456,
                                        3.1415926500000002
                                    ]
                                ]
                            },
                            [
                                0,
                                1,
                                2,
                                {
                                    'three': 3
                                },
                                [
                                    4,
                                    5,
                                    6,
                                    [
                                        7,
                                        8,
                                        [
                                            9,
                                            10
                                        ],
                                        {
                                            'eleven': 11
                                        }
                                    ]
                                ]
                            ]
                        ],
                        'tuples_in_array': [
                            [
                                'string',
                                123,
                                3.1415926500000002
                            ],
                            [
                                'string',
                                456,
                                3.1415926500000002
                            ]
                        ],
                        'integer': 123,
                        'array': [
                            'thing 1',
                            'thing 2',
                            'thing 3'
                        ],
                        '_id': 'Test.7369eb7c552d68c87a302a3ca2392c2a02cd8f2b'
        }
        self.assertEqual(self.object.get(), response)

    def test_object_update(self):
        """Update object"""
        self.test_object_save()
        response = {
            'rev': '2-9277bb48d6bcd1f081e7db222f89b5d3',
            'ok': True,
            'id': 'Test.7369eb7c552d68c87a302a3ca2392c2a02cd8f2b'
        }
        self.object['attribute'] = 'another attribute'
        self.assertEqual(self.object.update(), response)

    def test_object_delete(self):
        """Delete object"""
        self.test_object_save()
        response = {
            'rev': '2-842ba4a6a140e56f7bc722359807d1da',
            'ok': True,
            'id': 'Test.7369eb7c552d68c87a302a3ca2392c2a02cd8f2b'
        }
        self.assertEqual(self.object.delete(), response)

    def test_create_from_existing_object(self):
        """Create object from existing object"""
        self.test_object_save()
        response = {
            'rev': '1-a727e7b27c5f8c796294b728bfd60820',
            'ok': True,
            'id': 'Test.272f675318ba4cab76e20ef8e020576f62813a61'
        }
        self.object['attribute'] = 'another attribute'
        self.assertEqual(self.object.save(), response)

    def test_get_object_from_existing(self):
        """Return object from existing document"""
        self.test_create_from_existing_object()
        self.assertEqual(self.object.get('Test.272f675318ba4cab76e20ef8e020576f62813a61')['attribute'], 'another attribute')
        self.assertEqual(self.object.get('Test.272f675318ba4cab76e20ef8e020576f62813a61')['_rev'], '1-a727e7b27c5f8c796294b728bfd60820')
        self.assertEqual(type(self.object.get('Test.272f675318ba4cab76e20ef8e020576f62813a61')), type(self.object))

if __name__ == '__main__':
    unittest.main()
