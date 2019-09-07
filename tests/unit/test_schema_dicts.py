#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pytest import raises

from pytornado.objects.utils import check_dict_against_schema

SCHEMA_1 = {
    '__REQUIRED_KEYS': ['name', 'age'],
    'name': {
        'type': str,
        'min_len': 3,
        'max_len': 12,
    },
    'age': {
        'type': int,
        '>=': 0,
        '<': 120,
    }
}


def test_schema_dict():
    """
    Schema dicts
    """

    test = {
        'name': 'Aaron',
        'age': 22,
    }

    check_dict_against_schema(test, SCHEMA_1)

    test = {
        'name': 'Aaron',
        'age': 200,  # Value too large
    }

    with raises(ValueError):
        check_dict_against_schema(test, SCHEMA_1)

    test = {
        'name': 'Aaron',
        'age': -1,  # Value too small
    }

    with raises(ValueError):
        check_dict_against_schema(test, SCHEMA_1)

    test = {
        'name': 'Aaron',
    }

    with raises(KeyError):
        check_dict_against_schema(test, SCHEMA_1)

    test = {
        'name': 'Aaron NameTooLong',
        'age': 22,
    }

    with raises(ValueError):
        check_dict_against_schema(test, SCHEMA_1)

    test = {
        'name': 'A',  # Name too short
        'age': 22,
    }

    with raises(ValueError):
        check_dict_against_schema(test, SCHEMA_1)
