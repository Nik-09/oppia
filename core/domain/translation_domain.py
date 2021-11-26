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



class TranslatableItem:
    """Value object representing item that can be translated."""

    DATA_FORMAT_HTML = 'html'
    DATA_FORMAT_UNICODE_STRING = 'unicode'
    DATA_FORMAT_SET_OF_NORMALIZED_STRING = 'set_of_normalized_string'
    DATA_FORMAT_SET_OF_UNICODE_STRING = 'set_of_unicode_string'
    CONTENT_TYPE_CONTENT = 'content'
    CONTENT_TYPE_INTERACTION = 'interaction'
    CONTENT_TYPE_RULE = 'rule'
    CONTENT_TYPE_FEEDBACK = 'feedback'
    CONTENT_TYPE_HINT = 'hint'
    CONTENT_TYPE_SOLUTION = 'solution'

    def __init__(
            self, content, data_format, content_type, interaction_id=None,
            rule_type=None):
        """Initializes a TranslatableItem domain object.

        Args:
            content: str|list(str). The translatable content text.
            data_format: str. The data format of the translatable content.
            content_type: str. One of `Content`, `Interaction`, ‘Rule`,
                `Feedback`, `Hint`, `Solution`.
            interaction_id: str|None. Interaction ID, e.g. `TextInput`, if the
                content corresponds to an InteractionInstance, else None.
            rule_type: str|None. Rule type if content_type == `Rule`, e.g.
                “Equals”, “IsSubsetOf”, “Contains” else None.
        """
        self.content = content
        self.data_format = data_format
        self.content_type = content_type
        self.interaction_id = interaction_id
        self.rule_type = rule_type

    def to_dict(self):
        """Returns a dict representing this TranslatableItem domain object.

        Returns:
            dict. A dict, mapping all fields of TranslatableItem instance.
        """
        return {
            'content': self.content,
            'data_format': self.data_format,
            'content_type': self.content_type,
            'interaction_id': self.interaction_id,
            'rule_type': self.rule_type
        }


class Voiceover:
    """Value object representing an voiceover."""

    def to_dict(self):
        """Returns a dict representing this Voiceover domain object.

        Returns:
            dict. A dict, mapping all fields of Voiceover instance.
        """
        return {
            'filename': self.filename,
            'file_size_bytes': self.file_size_bytes,
            'needs_update': self.needs_update,
            'duration_secs': self.duration_secs
        }

    @classmethod
    def from_dict(cls, voiceover_dict):
        """Return a Voiceover domain object from a dict.

        Args:
            voiceover_dict: dict. The dict representation of
                Voiceover object.

        Returns:
            Voiceover. The corresponding Voiceover domain object.
        """
        return cls(
            voiceover_dict['filename'],
            voiceover_dict['file_size_bytes'],
            voiceover_dict['needs_update'],
            voiceover_dict['duration_secs'])

    def __init__(self, filename, file_size_bytes, needs_update, duration_secs):
        """Initializes a Voiceover domain object.

        Args:
            filename: str. The corresponding voiceover file path.
            file_size_bytes: int. The file size, in bytes. Used to display
                potential bandwidth usage to the learner before they download
                the file.
            needs_update: bool. Whether voiceover is marked for needing review.
            duration_secs: float. The duration in seconds for the voiceover
                recording.
        """
        # str. The corresponding audio file path, e.g.
        # "content-en-2-h7sjp8s.mp3".
        self.filename = filename
        # int. The file size, in bytes. Used to display potential bandwidth
        # usage to the learner before they download the file.
        self.file_size_bytes = file_size_bytes
        # bool. Whether audio is marked for needing review.
        self.needs_update = needs_update
        # float. The duration in seconds for the voiceover recording.
        self.duration_secs = duration_secs

    def validate(self):
        """Validates properties of the Voiceover.

        Raises:
            ValidationError. One or more attributes of the Voiceover are
                invalid.
        """
        if not isinstance(self.filename, str):
            raise utils.ValidationError(
                'Expected audio filename to be a string, received %s' %
                self.filename)
        dot_index = self.filename.rfind('.')
        if dot_index in (-1, 0):
            raise utils.ValidationError(
                'Invalid audio filename: %s' % self.filename)
        extension = self.filename[dot_index + 1:]
        if extension not in feconf.ACCEPTED_AUDIO_EXTENSIONS:
            raise utils.ValidationError(
                'Invalid audio filename: it should have one of '
                'the following extensions: %s. Received: %s' % (
                    list(feconf.ACCEPTED_AUDIO_EXTENSIONS.keys()),
                    self.filename))

        if not isinstance(self.file_size_bytes, int):
            raise utils.ValidationError(
                'Expected file size to be an int, received %s' %
                self.file_size_bytes)
        if self.file_size_bytes <= 0:
            raise utils.ValidationError(
                'Invalid file size: %s' % self.file_size_bytes)

        if not isinstance(self.needs_update, bool):
            raise utils.ValidationError(
                'Expected needs_update to be a bool, received %s' %
                self.needs_update)
        if not isinstance(self.duration_secs, float):
            raise utils.ValidationError(
                'Expected duration_secs to be a float, received %s' %
                self.duration_secs)
        if self.duration_secs < 0:
            raise utils.ValidationError(
                'Expected duration_secs to be positive number, '
                'or zero if not yet specified %s' %
                self.duration_secs)




# TODO: Remove WrittenTranslation.
class WrittenTranslation:
    """Value object representing a written translation for a content.

    Here, "content" could mean a string or a list of strings. The latter arises,
    for example, in the case where we are checking for equality of a learner's
    answer against a given set of strings. In such cases, the number of strings
    in the translation of the original object may not be the same as the number
    of strings in the original object.
    """

    DATA_FORMAT_HTML = 'html'
    DATA_FORMAT_UNICODE_STRING = 'unicode'
    DATA_FORMAT_SET_OF_NORMALIZED_STRING = 'set_of_normalized_string'
    DATA_FORMAT_SET_OF_UNICODE_STRING = 'set_of_unicode_string'

    DATA_FORMAT_TO_TRANSLATABLE_OBJ_TYPE = {
        DATA_FORMAT_HTML: 'TranslatableHtml',
        DATA_FORMAT_UNICODE_STRING: 'TranslatableUnicodeString',
        DATA_FORMAT_SET_OF_NORMALIZED_STRING: (
            'TranslatableSetOfNormalizedString'),
        DATA_FORMAT_SET_OF_UNICODE_STRING: 'TranslatableSetOfUnicodeString',
    }

    @classmethod
    def is_data_format_list(cls, data_format):
        """Checks whether the content of translation with given format is of
        a list type.

        Args:
            data_format: str. The format of the translation.

        Returns:
            bool. Whether the content of translation is a list.
        """
        return data_format in (
            cls.DATA_FORMAT_SET_OF_NORMALIZED_STRING,
            cls.DATA_FORMAT_SET_OF_UNICODE_STRING
        )

    def __init__(self, data_format, translation, needs_update):
        """Initializes a WrittenTranslation domain object.

        Args:
            data_format: str. One of the keys in
                DATA_FORMAT_TO_TRANSLATABLE_OBJ_TYPE. Indicates the
                type of the field (html, unicode, etc.).
            translation: str|list(str). A user-submitted string or list of
                strings that matches the given data format.
            needs_update: bool. Whether the translation is marked as needing
                review.
        """
        self.data_format = data_format
        self.translation = translation
        self.needs_update = needs_update

    def to_dict(self):
        """Returns a dict representing this WrittenTranslation domain object.

        Returns:
            dict. A dict, mapping all fields of WrittenTranslation instance.
        """
        return {
            'data_format': self.data_format,
            'translation': self.translation,
            'needs_update': self.needs_update,
        }

    @classmethod
    def from_dict(cls, written_translation_dict):
        """Return a WrittenTranslation domain object from a dict.

        Args:
            written_translation_dict: dict. The dict representation of
                WrittenTranslation object.

        Returns:
            WrittenTranslation. The corresponding WrittenTranslation domain
            object.
        """
        return cls(
            written_translation_dict['data_format'],
            written_translation_dict['translation'],
            written_translation_dict['needs_update'])

    def validate(self):
        """Validates properties of the WrittenTranslation, normalizing the
        translation if needed.

        Raises:
            ValidationError. One or more attributes of the WrittenTranslation
                are invalid.
        """
        if self.data_format not in (
                self.DATA_FORMAT_TO_TRANSLATABLE_OBJ_TYPE):
            raise utils.ValidationError(
                'Invalid data_format: %s' % self.data_format)

        translatable_class_name = (
            self.DATA_FORMAT_TO_TRANSLATABLE_OBJ_TYPE[self.data_format])
        translatable_obj_class = (
            translatable_object_registry.Registry.get_object_class(
                translatable_class_name))
        self.translation = translatable_obj_class.normalize_value(
            self.translation)

        if not isinstance(self.needs_update, bool):
            raise utils.ValidationError(
                'Expected needs_update to be a bool, received %s' %
                self.needs_update)

# TODO: Remove WrittenTranslations.
class WrittenTranslations:
    """Value object representing a content translations which stores
    translated contents of all state contents (like hints, feedback etc.) in
    different languages linked through their content_id.
    """

    def __init__(self, translations_mapping):
        """Initializes a WrittenTranslations domain object.

        Args:
            translations_mapping: dict. A dict mapping the content Ids
                to the dicts which is the map of abbreviated code of the
                languages to WrittenTranslation objects.
        """
        self.translations_mapping = translations_mapping

    def to_dict(self):
        """Returns a dict representing this WrittenTranslations domain object.

        Returns:
            dict. A dict, mapping all fields of WrittenTranslations instance.
        """
        translations_mapping = {}
        for (content_id, language_code_to_written_translation) in (
                self.translations_mapping.items()):
            translations_mapping[content_id] = {}
            for (language_code, written_translation) in (
                    language_code_to_written_translation.items()):
                translations_mapping[content_id][language_code] = (
                    written_translation.to_dict())
        written_translations_dict = {
            'translations_mapping': translations_mapping
        }

        return written_translations_dict

    @classmethod
    def from_dict(cls, written_translations_dict):
        """Return a WrittenTranslations domain object from a dict.

        Args:
            written_translations_dict: dict. The dict representation of
                WrittenTranslations object.

        Returns:
            WrittenTranslations. The corresponding WrittenTranslations domain
            object.
        """
        translations_mapping = {}
        for (content_id, language_code_to_written_translation) in (
                written_translations_dict['translations_mapping'].items()):
            translations_mapping[content_id] = {}
            for (language_code, written_translation) in (
                    language_code_to_written_translation.items()):
                translations_mapping[content_id][language_code] = (
                    WrittenTranslation.from_dict(written_translation))

        return cls(translations_mapping)

    def get_content_ids_that_are_correctly_translated(self, language_code):
        """Returns a list of content ids in which a correct translation is
        available in the given language.

        Args:
            language_code: str. The abbreviated code of the language.

        Returns:
            list(str). A list of content ids in which the translations are
            available in the given language.
        """
        correctly_translated_content_ids = []
        for content_id, translations in self.translations_mapping.items():
            if (
                language_code in translations and
                not translations[language_code].needs_update
            ):
                correctly_translated_content_ids.append(content_id)

        return correctly_translated_content_ids

    def add_translation(self, content_id, language_code, html):
        """Adds a translation for the given content id in a given language.

        Args:
            content_id: str. The id of the content.
            language_code: str. The language code of the translated html.
            html: str. The translated html.
        """
        written_translation = WrittenTranslation(
            WrittenTranslation.DATA_FORMAT_HTML, html, False)
        self.translations_mapping[content_id][language_code] = (
            written_translation)

    def mark_written_translation_as_needing_update(
            self, content_id, language_code):
        """Marks translation as needing update for the given content id and
        language code.

        Args:
            content_id: str. The id of the content.
            language_code: str. The language code.
        """
        self.translations_mapping[content_id][language_code].needs_update = (
            True
        )

    def mark_written_translations_as_needing_update(self, content_id):
        """Marks translation as needing update for the given content id in all
        languages.

        Args:
            content_id: str. The id of the content.
        """
        for (language_code, written_translation) in (
                self.translations_mapping[content_id].items()):
            written_translation.needs_update = True
            self.translations_mapping[content_id][language_code] = (
                written_translation)

    def validate(self, expected_content_id_list):
        """Validates properties of the WrittenTranslations.

        Args:
            expected_content_id_list: list(str). A list of content id which are
                expected to be inside they WrittenTranslations.

        Raises:
            ValidationError. One or more attributes of the WrittenTranslations
                are invalid.
        """
        if expected_content_id_list is not None:
            if not set(self.translations_mapping.keys()) == (
                    set(expected_content_id_list)):
                raise utils.ValidationError(
                    'Expected state written_translations to match the listed '
                    'content ids %s, found %s' % (
                        expected_content_id_list,
                        list(self.translations_mapping.keys()))
                    )

        for (content_id, language_code_to_written_translation) in (
                self.translations_mapping.items()):
            if not isinstance(content_id, str):
                raise utils.ValidationError(
                    'Expected content_id to be a string, received %s'
                    % content_id)
            if not isinstance(language_code_to_written_translation, dict):
                raise utils.ValidationError(
                    'Expected content_id value to be a dict, received %s'
                    % language_code_to_written_translation)
            for (language_code, written_translation) in (
                    language_code_to_written_translation.items()):
                if not isinstance(language_code, str):
                    raise utils.ValidationError(
                        'Expected language_code to be a string, received %s'
                        % language_code)
                # Currently, we assume written translations are used by the
                # voice-artist to voiceover the translated text so written
                # translations can be in supported audio/voiceover languages.
                allowed_language_codes = [language['id'] for language in (
                    constants.SUPPORTED_AUDIO_LANGUAGES)]
                if language_code not in allowed_language_codes:
                    raise utils.ValidationError(
                        'Invalid language_code: %s' % language_code)

                written_translation.validate()

    def get_content_ids_for_text_translation(self):
        """Returns a list of content_id available for text translation.

        Returns:
            list(str). A list of content id available for text translation.
        """
        return list(sorted(self.translations_mapping.keys()))

    def get_translated_content(self, content_id, language_code):
        """Returns the translated content for the given content_id in the given
        language.

        Args:
            content_id: str. The ID of the content.
            language_code: str. The language code for the translated content.

        Returns:
            str. The translated content for a given content id in a language.

        Raises:
            Exception. Translation doesn't exist in the given language.
            Exception. The given content id doesn't exist.
        """
        if content_id in self.translations_mapping:
            if language_code in self.translations_mapping[content_id]:
                return self.translations_mapping[
                    content_id][language_code].translation
            else:
                raise Exception(
                    'Translation for the given content_id %s does not exist in '
                    '%s language code' % (content_id, language_code))
        else:
            raise Exception('Invalid content_id: %s' % content_id)

    def add_content_id_for_translation(self, content_id):
        """Adds a content id as a key for the translation into the
        content_translation dict.

        Args:
            content_id: str. The id representing a subtitled html.

        Raises:
            Exception. The content id isn't a string.
        """
        if not isinstance(content_id, str):
            raise Exception(
                'Expected content_id to be a string, received %s' % content_id)
        if content_id in self.translations_mapping:
            raise Exception(
                'The content_id %s already exist.' % content_id)
        else:
            self.translations_mapping[content_id] = {}

    def delete_content_id_for_translation(self, content_id):
        """Deletes a content id from the content_translation dict.

        Args:
            content_id: str. The id representing a subtitled html.

        Raises:
            Exception. The content id isn't a string.
        """
        if not isinstance(content_id, str):
            raise Exception(
                'Expected content_id to be a string, received %s' % content_id)
        if content_id not in self.translations_mapping:
            raise Exception(
                'The content_id %s does not exist.' % content_id)
        else:
            self.translations_mapping.pop(content_id, None)

    def get_all_html_content_strings(self):
        """Gets all html content strings used in the WrittenTranslations.

        Returns:
            list(str). The list of html content strings.
        """
        html_string_list = []
        for translations in self.translations_mapping.values():
            for written_translation in translations.values():
                if (written_translation.data_format ==
                        WrittenTranslation.DATA_FORMAT_HTML):
                    html_string_list.append(written_translation.translation)
        return html_string_list

    @staticmethod
    def convert_html_in_written_translations(
            written_translations_dict, conversion_fn):
        """Checks for HTML fields in the written translations and converts it
        according to the conversion function.

        Args:
            written_translations_dict: dict. The written translations dict.
            conversion_fn: function. The function to be used for converting the
                HTML.

        Returns:
            dict. The converted written translations dict.
        """
        for content_id, language_code_to_written_translation in (
                written_translations_dict['translations_mapping'].items()):
            for language_code in (
                    language_code_to_written_translation.keys()):
                translation_dict = written_translations_dict[
                    'translations_mapping'][content_id][language_code]
                if 'data_format' in translation_dict:
                    if (translation_dict['data_format'] ==
                            WrittenTranslation.DATA_FORMAT_HTML):
                        written_translations_dict['translations_mapping'][
                            content_id][language_code]['translation'] = (
                                conversion_fn(written_translations_dict[
                                    'translations_mapping'][content_id][
                                        language_code]['translation'])
                            )
                elif 'html' in translation_dict:
                    # TODO(#11950): Delete this once old schema migration
                    # functions are deleted.
                    # This "elif" branch is needed because, in states schema
                    # v33, this function is called but the dict is still in the
                    # old format (that doesn't have a "data_format" key).
                    written_translations_dict['translations_mapping'][
                        content_id][language_code]['html'] = (
                            conversion_fn(translation_dict['html']))

        return written_translations_dict

# TODO: Remove RecordedVoiceovers.
class RecordedVoiceovers:
    """Value object representing a recorded voiceovers which stores voiceover of
    all state contents (like hints, feedback etc.) in different languages linked
    through their content_id.
    """

    def __init__(self, voiceovers_mapping):
        """Initializes a RecordedVoiceovers domain object.

        Args:
            voiceovers_mapping: dict. A dict mapping the content Ids
                to the dicts which is the map of abbreviated code of the
                languages to the Voiceover objects.
        """
        self.voiceovers_mapping = voiceovers_mapping

    def to_dict(self):
        """Returns a dict representing this RecordedVoiceovers domain object.

        Returns:
            dict. A dict, mapping all fields of RecordedVoiceovers instance.
        """
        voiceovers_mapping = {}
        for (content_id, language_code_to_voiceover) in (
                self.voiceovers_mapping.items()):
            voiceovers_mapping[content_id] = {}
            for (language_code, voiceover) in (
                    language_code_to_voiceover.items()):
                voiceovers_mapping[content_id][language_code] = (
                    voiceover.to_dict())
        recorded_voiceovers_dict = {
            'voiceovers_mapping': voiceovers_mapping
        }

        return recorded_voiceovers_dict

    @classmethod
    def from_dict(cls, recorded_voiceovers_dict):
        """Return a RecordedVoiceovers domain object from a dict.

        Args:
            recorded_voiceovers_dict: dict. The dict representation of
                RecordedVoiceovers object.

        Returns:
            RecordedVoiceovers. The corresponding RecordedVoiceovers domain
            object.
        """
        voiceovers_mapping = {}
        for (content_id, language_code_to_voiceover) in (
                recorded_voiceovers_dict['voiceovers_mapping'].items()):
            voiceovers_mapping[content_id] = {}
            for (language_code, voiceover) in (
                    language_code_to_voiceover.items()):
                voiceovers_mapping[content_id][language_code] = (
                    Voiceover.from_dict(voiceover))

        return cls(voiceovers_mapping)

    def validate(self, expected_content_id_list):
        """Validates properties of the RecordedVoiceovers.

        Args:
            expected_content_id_list: list(str). A list of content id which are
                expected to be inside the RecordedVoiceovers.

        Raises:
            ValidationError. One or more attributes of the RecordedVoiceovers
                are invalid.
        """
        if expected_content_id_list is not None:
            if not set(self.voiceovers_mapping.keys()) == (
                    set(expected_content_id_list)):
                raise utils.ValidationError(
                    'Expected state recorded_voiceovers to match the listed '
                    'content ids %s, found %s' % (
                        expected_content_id_list,
                        list(self.voiceovers_mapping.keys()))
                    )

        for (content_id, language_code_to_voiceover) in (
                self.voiceovers_mapping.items()):
            if not isinstance(content_id, str):
                raise utils.ValidationError(
                    'Expected content_id to be a string, received %s'
                    % content_id)
            if not isinstance(language_code_to_voiceover, dict):
                raise utils.ValidationError(
                    'Expected content_id value to be a dict, received %s'
                    % language_code_to_voiceover)
            for (language_code, voiceover) in (
                    language_code_to_voiceover.items()):
                if not isinstance(language_code, str):
                    raise utils.ValidationError(
                        'Expected language_code to be a string, received %s'
                        % language_code)
                allowed_language_codes = [language['id'] for language in (
                    constants.SUPPORTED_AUDIO_LANGUAGES)]
                if language_code not in allowed_language_codes:
                    raise utils.ValidationError(
                        'Invalid language_code: %s' % language_code)

                voiceover.validate()

    def get_content_ids_for_voiceovers(self):
        """Returns a list of content_id available for voiceover.

        Returns:
            list(str). A list of content id available for voiceover.
        """
        return list(self.voiceovers_mapping.keys())

    def strip_all_existing_voiceovers(self):
        """Strips all existing voiceovers from the voiceovers_mapping."""
        for content_id in self.voiceovers_mapping.keys():
            self.voiceovers_mapping[content_id] = {}

    def add_content_id_for_voiceover(self, content_id):
        """Adds a content id as a key for the voiceover into the
        voiceovers_mapping dict.

        Args:
            content_id: str. The id representing a subtitled html.

        Raises:
            Exception. The content id isn't a string.
            Exception. The content id already exist in the voiceovers_mapping
                dict.
        """
        if not isinstance(content_id, str):
            raise Exception(
                'Expected content_id to be a string, received %s' % content_id)
        if content_id in self.voiceovers_mapping:
            raise Exception(
                'The content_id %s already exist.' % content_id)

        self.voiceovers_mapping[content_id] = {}

    def delete_content_id_for_voiceover(self, content_id):
        """Deletes a content id from the voiceovers_mapping dict.

        Args:
            content_id: str. The id representing a subtitled html.

        Raises:
            Exception. The content id isn't a string.
            Exception. The content id does not exist in the voiceovers_mapping
                dict.
        """
        if not isinstance(content_id, str):
            raise Exception(
                'Expected content_id to be a string, received %s' % content_id)
        if content_id not in self.voiceovers_mapping:
            raise Exception(
                'The content_id %s does not exist.' % content_id)
        else:
            self.voiceovers_mapping.pop(content_id, None)
