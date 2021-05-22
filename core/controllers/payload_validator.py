# coding: utf-8

# Copyright 2014 The Oppia Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Controllers for the editor view."""

from __future__ import absolute_import  # pylint: disable=import-only-modules
from __future__ import unicode_literals  # pylint: disable=import-only-modules

import schema_utils

def validate(handler_args, handler_args_schema, strict_validation):
    """Docstring."""
    errors = []
    required_args = []
    default_present = False
    for arg_key, arg_schema in handler_args_schema.items():
        optional = False
        if 'optional' in arg_schema:
            optional = arg_schema['optional']
            del arg_schema['optional']
            assert isinstance((optional, bool), (
                'Expected optional to be a boolean value, found %s' % optional))

        if arg_key not in handler_args:
            if optional:
                continue
            elif 'default' in arg_schema:
                value = arg_schema['default']
                del arg_schema['default']
                default_present = True

        if not optional:
            required_args.append(arg_key)

        if not default_present:
            value = handler_args[arg_key]
        try:
            normalized_value = schema_utils.normalize_against_schema(
                value, arg_schema, apply_custom_validator=True)
        except Exception as e:
            errors.append(
                'Schema validation for \'%s\' failed: %s' % (arg_key, e))

    missing_args = set(required_args) - set(handler_args.keys())
    if strict_validation:
        extra_args = set(handler_args.keys()) - set(arg_schema.keys())

    if missing_args:
        errors.append('Missing args: %s' % ', '.join(missing_args))

    if extra_args:
        errors.append('Found extra params: %s' % ', '.join(extra_args))
    return errors
