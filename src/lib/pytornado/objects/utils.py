#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
# Copyright 2017-2019 Airinnova AB and the PyTornado authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ----------------------------------------------------------------------

# Authors:
# * Alessandro Gastaldi
# * Aaron Dettmann

"""
Miscellaneous data structures for PyTornado.

Developed for Airinnova AB, Stockholm, Sweden.
"""


from collections import OrderedDict, MutableMapping


class FixedNamespace(object):
    """
    Immutable SIMPLENAMESPACE variant.

    Functions as a RECORD- or STRUCT-like object.
    Attributes of FIXEDNAMESPACE are accessed by dot notation: 'name.attr'.

    __MUTABLE controls how attributes are created and modified:

        * When TRUE, assigning a value to an undefined attribute creates it.
        * When FALSE, this instead raises an AttributeError.

    __MUTABLE is TRUE by default. _FREEZE sets __MUTABLE to FALSE.

    [1] https://docs.python.org/3.5/library/types.html
    """

    __mutable = True

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __setattr__(self, key, value):
        if not self.__mutable and not hasattr(self, key):
            raise AttributeError(f"Immutable instance of FixedNamespace does not have attribute '{key}'.")

        object.__setattr__(self, key, value)

    def __repr__(self):
        keys = sorted(self.__dict__)
        items = ("{}={!r}".format(k, self.__dict__[k]) for k in keys)
        return "{}:\n ( {} )".format(type(self).__name__, ",\n ".join(items))

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def _freeze(self):
        """Make current instance of FIXEDNAMESPACE immutable."""

        self.__mutable = False

    def _unfreeze(self):
        """Make current instance of FIXEDNAMESPACE mutable."""

        self.__mutable = True


class FixedOrderedDict(MutableMapping):
    """
    Immutable ORDEREDDICT[1] variant, based on MUTABLEMAPPING[2].

    Works as a dictionary with ordered key-value pairs.
    Entries of FIXEDORDEREDDICT are accessed by key: 'obj[key]'.

    __MUTABLE controls how key-value pairs are created and modified:
    * When TRUE, assigning a value to an undefined key creates a new entry.
    * When FALSE, this instead raises an KeyError.

    __MUTABLE is TRUE by default. _FREEZE sets __MUTABLE to FALSE.

    [1] collections.OrderedDict
    [2] collections.MutableMapping
    """

    __mutable = True

    def __init__(self, *args):
        self._dictionary = OrderedDict(*args)

    def __getitem__(self, key):
        return self._dictionary[key]

    def __setitem__(self, key, value):
        if not self.__mutable and key not in self._dictionary:
            raise KeyError(f"Instance of FixedOrderedDict does not have item '{key}'.")

        self._dictionary[key] = value

    def __delitem__(self, key):
        raise NotImplementedError("Cannot delete item of instance of FixedOrderedDict.")

    def __iter__(self):
        return iter(self._dictionary)

    def __repr__(self):
        items = ("{}={!r}".format(k, v) for k, v in self._dictionary.items())
        return "{}({})".format(type(self).__name__, ", ".join(items))

    def __len__(self):
        return len(self._dictionary)

    def _freeze(self):
        """Add item to instance of FIXEDORDEREDDICT, with DEFAULT value."""

        self.__mutable = False


def check_dict(template_dict, test_dict):
    """
    Check that a test dictionary looks like a template dictionary

    Args:
        :template_dict: Template dictionary
        :test_dict: Test dictionary

    The template dictionary must have a specific structure as outlined below:

    .. code:: python

        template_dict = {
            'test_key1': ('default_value1', str),
            'test_key2': (1792, (int, float)),
        }

    The values have to be tuples with some default value and the expected
    types of the values. The follwing dictionary would pass the test:

    .. code:: python

        test_dict = {
            'test_key1': 'some_string',
            'test_key2': 1111,
        }

    However, the follwing dictionary does not have the correct form and an
    error will be raised.

    .. code:: python

        test_dict = {
            'test_key1': 'this is okay...',
            'test_key2': '... but a string is now allowed here',
        }

    Raises:
        :TypeError: If types of test and template dictionary don't match
    """

    # TODO: handle None better!!!

    for key, (value, dtype) in template_dict.items():
        dtype = (dtype,) if not isinstance(dtype, tuple) else dtype

        if None not in dtype:
            if not isinstance(test_dict[key], dtype):
                err_msg = f"""
                Unexpected data type for key '{key}'.
                Expected {dtype}, got {type(test_dict[key])}.
                """
                raise TypeError(err_msg)

        if dtype[0] is dict:
            check_dict(value, test_dict[key])


def get_default_dict(template_dict):
    """
    Return a default dict from a template dictionary

    Args:
        :template_dict: Template dictionary

    Returns:
        :default_dict: New dictionary with defaults generated from 'template_dict'

    The template dictionary must have a specific structure as outlined below:

    .. code:: python

        template_dict = {
            'test_key1': ('default_value1', str),
            'test_key2': (1792, (int, float)),
        }

    The 'default_dict' will look like this:

    .. code:: python

        default_dict = {
            'test_key1': 'default_value1',
            'test_key2': 1792,
        }
    """

    default_dict = {}
    for key, (value, _) in template_dict.items():
        # Treat non-empty dictionary recursively
        if isinstance(value, dict) and value:
            value = get_default_dict(template_dict=value)
        default_dict[key] = value
    return default_dict

# ============================================================================
# ============================================================================
# ============================================================================

import operator


OPERATORS = {
    '>': operator.gt,
    '<': operator.lt,
    '<=': operator.le,
    '>=': operator.ge,
}


class SchemaError(Exception):
    """Raised if the schema dictionary is ill-defined"""

    pass


def check_dict_against_schema(test_dict, schema_dict):
    """
    Check that a dictionary conforms to a schema dictionary

    This function will raise an error if the 'test_dict' is not in alignment
    with the 'schema_dict'

    Args:
        :schema_dict: Schema dictionary
        :test_dict: Dictionary to test against schema dictionary

    Raises:
        :ValueError: If test dictionary has value of wrong size
        :KeyError: If test dictionary does not have a required key
        :TypeError: If test dictionary has values of wrong type
        :SchemaError: If the schema itself is ill-defined
    """

    for key, form in schema_dict.items():

        # ----- Check that dictionary has required keys -----
        if key == '__REQUIRED_KEYS':
            check_keys_in_dict(form, test_dict)
            continue

        # ----- Basic type check -----
        expected_type = form.get('type', None)
        if expected_type is None:
            raise SchemaError("Type not defined")
        if not isinstance(test_dict[key], expected_type):
            err_msg = f"""
            Unexpected data type for key '{key}'.
            Expected {expected_type}, got {type(test_dict[key])}.
            """
            raise TypeError(err_msg)

        # ----- Test float/int -----
        if expected_type in (float, int):
            for check_key in OPERATORS.keys():
                check_value = form.get(check_key, None)
                if check_value is None:
                    continue
                expected_value = form.get(check_key, None)
                if expected_value is None:
                    raise SchemaError("Value not defined")

                if not OPERATORS[check_key](test_dict[key], expected_value):
                    err_msg = f"""
                    Test dictionary has wrong value for key '{key}'.
                    Expected {check_key}{expected_value}, but test value is '{test_dict[key]}'.
                    """
                    raise ValueError(err_msg)

        # ----- Test str -----
        if expected_type is str:
            min_len = form.get('min_len', None)
            if min_len is not None:
                if len(test_dict[key]) < min_len:
                    err_msg = f"""
                    String is too short.
                    """
                    raise ValueError(err_msg)

            max_len = form.get('max_len', None)
            if max_len is not None:
                if len(test_dict[key]) > max_len:
                    err_msg = f"""
                    String is too long.
                    """
                    raise ValueError(err_msg)


        # TODO: Test required keys
        # TODO: test nested dict


def check_keys_in_dict(required_keys, test_dict):
    """
    Check that required keys are in a test dictionary

    Args:
        :required_keys: List of keys required in the test dictionary
        :test_dict: Test dictionary

    Raises:
        :KeyError: If a required key is not found in the test dictionary
    """

    # TODO: check that required_keys is list of strings

    test_dict_keys = list(test_dict.keys())
    for required_key in required_keys:
        if not required_key in test_dict_keys:
            err_msg = f"""
            Key '{required_key}' is required, but not found in test dictionary
            """
            raise KeyError(err_msg)

# ============================================================================
# ============================================================================
# ============================================================================
