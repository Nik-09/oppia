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

"""Domain objects related to translations."""

from __future__ import annotations

from core import utils

from typing import Dict, DefaultDict

import collections
from core.domain import html_cleaner



TRANSLATABLE_CONTENT_FORMAT_HTML = 'html'
TRANSLATABLE_CONTENT_FORMAT_UNICODE_STRING = 'unicode'
TRANSLATABLE_CONTENT_FORMAT_SET_OF_NORMALIZED_STRING = (
    'set_of_normalized_string')
TRANSLATABLE_CONTENT_FORMAT_SET_OF_UNICODE_STRING = 'set_of_unicode_string'
TRANSLATABLE_CONTENT_FORMAT_OBJECT = 'object'

class BaseTranslatableObject:
    """Base class for all translatable object."""
    _translatable_contents: DefaultDict(str, TranslatableContent) = (
        collections.defaultdict(list))

    def _register_all_translatable_fields(self) -> None:
        """Base method to register translatable fields.

        Raises:
            NotImplementedError. The derived child class must implement the
                necessary logic to register all translatable fields in an
                entity.
        """
        raise NotImplementedError

    def _register_translatable_field(
        self,
        field_type: str,
        translatable_field: BaseTranslatableObject | TranslatableContent
    ) -> None:
        """Base method to register a translatable field in an entity.
        """
        content_hash = {}
        if field_type == TRANSLATABLE_CONTENT_FORMAT_OBJECT:
            translatable_fields = translatable_field.get_translatable_fields()
            for content_type, contents in translatable_fields.items():
                self._translatable_contents[content_type] += (contents)
            return

        if not isinstance(translatable_field, TranslatableContent):
            raise Exception(
                "Expected TranslatableContent, found %s" % translatable_field)

        if field_type != translatable_field.type:
            raise Exception("Expected field type to be %s but found %s" % (
                field_type, translatable_field.type))

        if translatable_field.hash in content_hash:
            return

        if translatable_field.value != '':
            self._translatable_contents[field_type].append(translatable_field)
            content_hash[translatable_field.hash] = True

    def get_translatable_fields(self) -> None:
        """Base method to get all the translatable fields for an entity.

        Returns:
            list(TranslatableContent). Returns the list of translatable fields
                for an entity.
        """
        self._translatable_contents = collections.defaultdict(list)
        self._register_all_translatable_fields()
        return self._translatable_contents

    def get_all_content_which_needs_translations(
        self,
        entityTranslations: EntityTranslations
    ) -> list():
        """Base method to return all translatable objects which need either
        translations or their existing translations needs update.

        Returns:
            list(TranslatableContent). Returns the list of TranslatableContent.
        """
        # Contents which need translations.
        contents_which_need_translation = []
        entity_translations_dict = entityTranslations.translations

        for translatable_content in self.get_translatable_fields().values():
            translatable_content_hash = translatable_content.hash

            if not translatable_content_hash in entity_translations_dict:
                contents_which_need_translation.append(translatable_content)
                continue
            if entity_translations_dict[translatable_content_hash].needs_update:
                contents_which_need_translation.append(translatable_content)

        return contents_which_need_translation

    def validate_translatable_contents(self):
        """Base method to validate BaseTranalatableObject."""
        pass


class EntityTranslations:
    """The EntityTranslation presents an EntityTranslationsModel for a given
    entity in a given language.
    """

    def __init__(
        self,
        entity_translation_id: str,
        entity_type: str,
        entity_id: str,
        language_code: str,
        translations: Dict(str, TranslatedContent)
    ):
        """Initializes the EntityTranslations domain object."""
        self.id = entity_translation_id
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.language_code = language_code
        self.translations = translations


class TranslatableContent:
    """Represents the content of an object which can be translated into
    multiple languages.
    """
    MAX_LENGHT_FOR_CONTENT_HASH = 12

    def __init__(
        self,
        content_type: str,
        value: Any,
        content_hash: str
    ):
        self.type = content_type
        self.value = value
        self.hash = content_hash

    def to_dict(self):
        return {
            'type': self.type,
            'value': self.value,
            'hash': self.hash
        }

    @classmethod
    def create_new(cls, content_type: str, value: Any):
        return cls(
            content_type,
            value,
            utils.convert_to_hash(value, cls.MAX_LENGHT_FOR_CONTENT_HASH)
        )

    @classmethod
    def from_dict(cls, translatable_content_dict):
        return cls(
            translatable_content_dict['type'],
            translatable_content_dict['value'],
            translatable_content_dict['hash'])

    @classmethod
    def create_default_translatable_content(cls, content_type):
        return cls(content_type, '', '')

    def validate(self):
        if not isinstance(self.hash, str):
            raise utils.ValidationError(
                'Expected hash to be a string, received %s' % self.hash)
        if not isinstance(self.value, str):
            raise utils.ValidationError(
                'Invalid value of the content : %s' % self.value)

        if self.type == TRANSLATABLE_CONTENT_FORMAT_HTML:
            self.value = html_cleaner.clean(self.value)

    def __repr__(self):
        return ("(%s, %s, %s)") % (self.type, self.value, self.hash)



class TranslatedContent:
    """Represents the contents of translated object."""

    def __init__(
        self,
        content_type:str,
        value: Any,
        content_hash: str,
        needs_update:str = False
    ):
        self.type = content_type
        self.value = value
        self.hash = content_hash
        self.needs_update = needs_update

    def to_dict(self):
        return {
            'type': self.type,
            'value': self.value,
            'hash': self.hash,
            'needs_update': self.needs_update
        }

    @classmethod
    def from_dict(self, translated_content_dict):
        return cls(
            translated_content_dict['content_type'],
            translated_content_dict['value'],
            translated_content_dict['content_hash'],
            translated_content_dict['needs_update'])


class MachineTranslation:
    """Domain object for machine translation of exploration content."""

    def __init__(
        self,
        source_language_code: str,
        target_language_code: str,
        source_text: str,
        translated_text: str
    ) -> None:
        """Initializes a MachineTranslation domain object.

        Args:
            source_language_code: str. The language code for the source text
                language. Must be different from target_language_code.
            target_language_code: str. The language code for the target
                translation language. Must be different from
                source_language_code.
            source_text: str. The untranslated source text.
            translated_text: str. The machine generated translation of the
                source text into the target language.
        """
        self.source_language_code = source_language_code
        self.target_language_code = target_language_code
        self.source_text = source_text
        self.translated_text = translated_text

    def validate(self) -> None:
        """Validates properties of the MachineTranslation.

        Raises:
            ValidationError. One or more attributes of the MachineTranslation
                are invalid.
        """
        # TODO(#12341): Tidy up this logic once we have a canonical list of
        # language codes.
        if not utils.is_supported_audio_language_code(
                self.source_language_code
            ) and not utils.is_valid_language_code(
                self.source_language_code
            ):
            raise utils.ValidationError(
                'Invalid source language code: %s' % self.source_language_code)

        # TODO(#12341): Tidy up this logic once we have a canonical list of
        # language codes.
        if not utils.is_supported_audio_language_code(
                self.target_language_code
            ) and not utils.is_valid_language_code(
                self.target_language_code
            ):
            raise utils.ValidationError(
                'Invalid target language code: %s' % self.target_language_code)

        if self.source_language_code == self.target_language_code:
            raise utils.ValidationError(
                (
                    'Expected source_language_code to be different from '
                    'target_language_code: "%s" = "%s"') % (
                        self.source_language_code, self.target_language_code))

    def to_dict(self) -> Dict[str, str]:
        """Converts the MachineTranslation domain instance into a dictionary
        form with its keys as the attributes of this class.

        Returns:
            dict. A dictionary containing the MachineTranslation class
            information in a dictionary form.
        """
        return {
            'source_language_code': self.source_language_code,
            'target_language_code': self.target_language_code,
            'source_text': self.source_text,
            'translated_text': self.translated_text
        }
