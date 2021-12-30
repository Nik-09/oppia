# coding: utf-8
#
# Copyright 2021 The Oppia Authors. All Rights Reserved.
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

"""Tests for domain objects related to translations."""

from __future__ import annotations

from core import utils
from core.domain import translation_domain
from core.tests import test_utils


class TranslatableObject1(translation_domain.BaseTranslatableObject):
    """Dummy translatable object for testing of BasetranslatableObject class."""

    def __init__(
        self,
        param1: str,
        param2: TranslatableObject2
    ) -> None:
        self.param1 = param1
        self.param2 = param2

    def _register_all_translatable_fields(self) -> None:
        self._register_translatable_field(
            translation_domain.TRANSLATABLE_CONTENT_FORMAT_UNICODE_STRING,
            'content_id_1',
            self.param1)
        self._register_translatable_object(self.param2)


class TranslatableObject2(translation_domain.BaseTranslatableObject):
    """Dummy translatable object for testing of BasetranslatableObject class."""

    def __init__(
        self,
        param3: str
    ) -> None:
        self.param3 = param3

    def _register_all_translatable_fields(self) -> None:
        self._register_translatable_field(
            translation_domain.TRANSLATABLE_CONTENT_FORMAT_UNICODE_STRING,
            'content_id_2',
            self.param3)


class TranslatableObject3(translation_domain.BaseTranslatableObject):
    """Dummy translatable object for testing of BasetranslatableObject class."""

    def __init__(
        self,
        param1: str,
        param2: str
    ) -> None:
        self.param1 = param1
        self.param2 = param2

    def _register_all_translatable_fields(self) -> None:
        self._register_translatable_field(
            translation_domain.TRANSLATABLE_CONTENT_FORMAT_UNICODE_STRING,
            'content_id_2',
            self.param1)
        self._register_translatable_field(
            translation_domain.TRANSLATABLE_CONTENT_FORMAT_UNICODE_STRING,
            'content_id_2',
            self.param2)


class TranslatableObject4(translation_domain.BaseTranslatableObject):
    """Dummy translatable object for testing of BasetranslatableObject class."""

    def __init__(
        self,
        param1: str,
        param2: str
    ) -> None:
        self.param1 = param1
        self.param2 = param2


class TranslatableObject5(translation_domain.BaseTranslatableObject):
    """Dummy translatable object for testing of BasetranslatableObject class."""

    def __init__(
        self,
        param1: str,
        param2: str,
        param3: str,
        param4: str
    ) -> None:
        self.param1 = param1
        self.param2 = param2
        self.param3 = param3
        self.param4 = param4

    def _register_all_translatable_fields(self) -> None:
        self._register_translatable_field(
            translation_domain.TRANSLATABLE_CONTENT_FORMAT_UNICODE_STRING,
            'content_id_1',
            self.param1)
        self._register_translatable_field(
            translation_domain.TRANSLATABLE_CONTENT_FORMAT_UNICODE_STRING,
            'content_id_2',
            self.param2)
        self._register_translatable_field(
            translation_domain.TRANSLATABLE_CONTENT_FORMAT_UNICODE_STRING,
            'content_id_3',
            self.param3)
        self._register_translatable_field(
            translation_domain.TRANSLATABLE_CONTENT_FORMAT_UNICODE_STRING,
            'content_id_4',
            self.param4)


class BaseTranslatableObjectUnitTest(test_utils.GenericTestBase):
    """Test class for BaseTranslatableObject."""

    def setUp(self) -> None:
        super(BaseTranslatableObjectUnitTest, self).setUp()
        self.translatable_object1 = TranslatableObject1(
            'My name is jhon.', TranslatableObject2('My name is jack.'))

    def test_get_all_translatable_content_returns_correct_items(self) -> None:
        expected_contents = [
            'My name is jhon.',
            'My name is jack.'
        ]
        translatable_contents = (
            self.translatable_object1.get_translatable_fields())

        self.assertItemsEqual(expected_contents, [ # type: ignore[no-untyped-call]
            translatable_content.content
            for translatable_content in translatable_contents.values()
        ])

    def test_contents_having_same_content_id_raises_exception(self) -> None:
        translatable_object = TranslatableObject3(
            'My name is jack.', 'My name is jhon.')

        with self.assertRaisesRegexp( # type: ignore[no-untyped-call]
            Exception, 'Already registered as a translatable content.'):
            translatable_object.get_translatable_fields()

    def test_unregistered_translatable_object_raises_exception(self) -> None:
        translatable_object = TranslatableObject4(
            'My name is jack.', 'My name is jhon.')

        error_msg = (
            'Translatable object is not registered, '
            'by using `_register_all_translatable_fields` method.')
        with self.assertRaisesRegexp(Exception, error_msg): # type: ignore[no-untyped-call]
            translatable_object.get_translatable_fields()

    def test_get_all_contents_which_needs_translations_method(self) -> None:
        translation_dict = {
            'content_id_3': translation_domain.TranslatedContent(
                'My name is Nikhil.', True)
        }
        entity_translations = translation_domain.EntityTranslations(
            'exp_id', 'exploration', 1, 'en', translation_dict)

        translatable_object = TranslatableObject5(
            'My name is jack.', 'My name is jhon.', 'My name is Nikhil.', '')
        contents_which_need_translation = (
            translatable_object.get_all_contents_which_needs_translations(
                entity_translations))

        expected_list_of_contents_which_need_translataion = [
            'My name is jack.',
            'My name is jhon.',
            'My name is Nikhil.'
        ]
        list_of_contents_which_need_translataion = [
            translatable_item.content
            for translatable_item in contents_which_need_translation
        ]
        self.assertItemsEqual( # type: ignore[no-untyped-call]
            expected_list_of_contents_which_need_translataion,
            list_of_contents_which_need_translataion)


class EntityTranslationsUnitTests(test_utils.GenericTestBase):
    """Test class for EntityTranslations."""

    def test_successfully_creates_entity_translations_object(self) -> None:
        translation_dict = {
            'content_id_1': translation_domain.TranslatedContent(
                'My name is Nikhil.', False)
        }
        entity_translations = translation_domain.EntityTranslations(
            'exp_id', 'exploration', 1, 'en', translation_dict)

        self.assertEqual(entity_translations.entity_id, 'exp_id')
        self.assertEqual(entity_translations.entity_type, 'exploration')
        self.assertEqual(entity_translations.entity_version, 1)
        self.assertEqual(entity_translations.language_code, 'en')
        self.assertEqual(
            entity_translations.translations['content_id_1'].content,
            'My name is Nikhil.')
        self.assertEqual(
            entity_translations.translations['content_id_1'].needs_update,
            False)


class TranslatableContentUnitTests(test_utils.GenericTestBase):
    """Test class for TranslatableContent."""

    def test_creation_of_object(self) -> None:
        translatable_content = translation_domain.TranslatableContent(
            'content_id_1',
            'My name is Jhon.',
            translation_domain.TRANSLATABLE_CONTENT_FORMAT_HTML
        )

        self.assertEqual(translatable_content.content_id, 'content_id_1')
        self.assertEqual(translatable_content.content, 'My name is Jhon.')
        self.assertEqual(
            translatable_content.type,
            translation_domain.TRANSLATABLE_CONTENT_FORMAT_HTML)

    def test_from_dict_method_of_translatable_content_class(self) -> None:
        translatable_content = (
                translation_domain.TranslatableContent.from_dict({
                'content_id': 'content_id_1',
                'content': 'My name is Jhon.',
                'type': translation_domain.TRANSLATABLE_CONTENT_FORMAT_HTML
            })
        )

        self.assertEqual(translatable_content.content_id, 'content_id_1')
        self.assertEqual(translatable_content.content, 'My name is Jhon.')
        self.assertEqual(
            translatable_content.type,
            translation_domain.TRANSLATABLE_CONTENT_FORMAT_HTML)

    def test_to_dict_method_of_translatable_content_class(self) -> None:
        translatable_content_dict = {
            'content_id': 'content_id_1',
            'content': 'My name is Jhon.',
            'type': translation_domain.TRANSLATABLE_CONTENT_FORMAT_HTML
        }
        translatable_content = translation_domain.TranslatableContent(
            'content_id_1',
            'My name is Jhon.',
            translation_domain.TRANSLATABLE_CONTENT_FORMAT_HTML
        )

        self.assertEqual(
            translatable_content.to_dict(),
            translatable_content_dict
        )


class TranslatedContentUnitTests(test_utils.GenericTestBase):
    """Test class for TranslatedContent."""

    def test_successfully_creates_translated_content_object(self) -> None:
        translated_content = translation_domain.TranslatedContent(
            'My name is Nikhil.', False)

        self.assertEqual(translated_content.content, 'My name is Nikhil.')
        self.assertEqual(translated_content.needs_update, False)

    def test_from_dict_method_of_translated_content_class(self) -> None:
        translated_content_dict = {
            'content': 'My name is Nikhil.',
            'needs_update': False
        }
        translated_content = translation_domain.TranslatedContent.from_dict(
            translated_content_dict)

        self.assertEqual(translated_content.content, 'My name is Nikhil.')
        self.assertEqual(translated_content.needs_update, False)

    def test_to_dict_method_of_translated_content_class(self) -> None:
        translated_content = translation_domain.TranslatedContent(
            'My name is Nikhil.', False)
        translated_content_dict = {
            'content': 'My name is Nikhil.',
            'needs_update': False
        }

        self.assertEqual(translated_content.to_dict(), translated_content_dict)


class MachineTranslationTests(test_utils.GenericTestBase):
    """Tests for the MachineTranslation domain object."""

    translation: translation_domain.MachineTranslation

    def setUp(self) -> None:
        """Setup for MachineTranslation domain object tests."""
        super(MachineTranslationTests, self).setUp()
        self._init_translation()

    def _init_translation(self) -> None:
        """Initialize self.translation with valid default values."""
        self.translation = translation_domain.MachineTranslation(
            'en', 'es', 'hello world', 'hola mundo')
        self.translation.validate()

    def test_validate_with_invalid_source_language_code_raises(self) -> None:
        self.translation.source_language_code = 'ABC'
        expected_error_message = (
            'Invalid source language code: ABC')
        with self.assertRaisesRegexp( # type: ignore[no-untyped-call]
            utils.ValidationError, expected_error_message):
            self.translation.validate()

    def test_validate_with_invalid_target_language_code_raises(self) -> None:
        self.translation.target_language_code = 'ABC'
        expected_error_message = (
            'Invalid target language code: ABC')
        with self.assertRaisesRegexp( # type: ignore[no-untyped-call]
            utils.ValidationError, expected_error_message):
            self.translation.validate()

    def test_validate_with_same_source_target_language_codes_raises(
        self
    ) -> None:
        self.translation.target_language_code = 'en'
        self.translation.source_language_code = 'en'
        expected_error_message = (
            'Expected source_language_code to be different from '
            'target_language_code: "en" = "en"')
        with self.assertRaisesRegexp( # type: ignore[no-untyped-call]
            utils.ValidationError, expected_error_message):
            self.translation.validate()

    def test_to_dict(self) -> None:
        self.assertEqual(
            self.translation.to_dict(),
            {
                'source_language_code': 'en',
                'target_language_code': 'es',
                'source_text': 'hello world',
                'translated_text': 'hola mundo'
            }
        )
