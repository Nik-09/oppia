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

"""Tests for MachineTranslation models."""

from __future__ import annotations

from core.platform import models
from core.tests import test_utils

MYPY = False
if MYPY: # pragma: no cover
    from mypy_imports import base_models
    from mypy_imports import translation_models

(base_models, translation_models) = models.Registry.import_models(
    [models.NAMES.base_model, models.NAMES.translation])


class EntityTranslationsModelTest(test_utils.GenericTestBase):
    def test_create_new_model(self) -> None:
        translated_content = {
            '123': {
                'content': 'Hello world!',
                'needs_update': False
            }
        }
        enitity_translation_model = (
            translation_models.EntityTranslationsModel.create_new(
                'exploration', 'exp_id', 1, 'hi', translated_content))
        self.assertEqual(enitity_translation_model.entity_type, 'exploration')
        self.assertEqual(enitity_translation_model.entity_id, 'exp_id')
        self.assertEqual(enitity_translation_model.entity_version, 1)
        self.assertEqual(enitity_translation_model.language_code, 'hi')
        self.assertEqual(
            enitity_translation_model.translations, translated_content)

    def test_get_method_returns_model(self) -> None:
        translated_content = {
            '123': {
                'content': 'Hello world!',
                'needs_update': False
            }
        }
        translation_models.EntityTranslationsModel.create_new(
            'exploration', 'exp_id', 1, 'hi', translated_content).put()
        enitity_translation_model = (
            translation_models.EntityTranslationsModel.get(
                'exploration', 'exp_id', 1, 'hi'))
        self.assertEqual(enitity_translation_model.entity_type, 'exploration')
        self.assertEqual(enitity_translation_model.entity_id, 'exp_id')
        self.assertEqual(enitity_translation_model.entity_version, 1)
        self.assertEqual(enitity_translation_model.language_code, 'hi')

    def test_get_all_for_entity_returns_models(self):
        translated_content1 = {
            '123': {
                'content': 'Hey I am Jhon.',
                'needs_update': False
            }
        }
        translation_models.EntityTranslationsModel.create_new(
            'exploration', 'exp_id', 1, 'en', translated_content1).put()
        translated_content2 = {
            '123': {
                'content': 'Hello world!',
                'needs_update': False
            }
        }
        translation_models.EntityTranslationsModel.create_new(
            'exploration', 'exp_id2', 2, 'hi', translated_content2).put()
        translated_content3 = {
            '123': {
                'conent': 'Hey I am Nikhil.',
                'needs_update': False
            }
        }
        translation_models.EntityTranslationsModel.create_new(
            'exploration', 'exp_id', 1, 'hi', translated_content3).put()

        enitity_translation_models = (
            translation_models.EntityTranslationsModel.get_all_for_entity(
                'exploration', 'exp_id', 1))
        self.assertEqual(len(enitity_translation_models), 2)

        enitity_translation_models = (
            translation_models.EntityTranslationsModel.get_all_for_entity(
                'exploration', 'exp_id2', 2))
        self.assertEqual(len(enitity_translation_models), 1)

    def test_get_export_policy_not_applicable(self) -> None:
        self.assertEqual(
            translation_models.EntityTranslationsModel.get_export_policy(),
            {
                'created_on': base_models.EXPORT_POLICY.NOT_APPLICABLE,
                'deleted': base_models.EXPORT_POLICY.NOT_APPLICABLE,
                'last_updated': base_models.EXPORT_POLICY.NOT_APPLICABLE,
                'entity_id': base_models.EXPORT_POLICY.NOT_APPLICABLE,
                'entity_type': base_models.EXPORT_POLICY.NOT_APPLICABLE,
                'entity_version': base_models.EXPORT_POLICY.NOT_APPLICABLE,
                'language_code': base_models.EXPORT_POLICY.NOT_APPLICABLE,
                'translations': base_models.EXPORT_POLICY.NOT_APPLICABLE
            }
        )

    def test_get_deletion_policy_not_applicable(self) -> None:
        self.assertEqual(
            translation_models.MachineTranslationModel.get_deletion_policy(),
            base_models.DELETION_POLICY.NOT_APPLICABLE)

    def test_get_model_association_to_user_not_corresponding_to_user(
        self
    ) -> None:
        self.assertEqual(
            (
                translation_models.EntityTranslationsModel
                .get_model_association_to_user()
            ),
            base_models.MODEL_ASSOCIATION_TO_USER.NOT_CORRESPONDING_TO_USER)


class MachineTranslationModelTests(test_utils.GenericTestBase):
    def test_create_model(self) -> None:
        model_id = translation_models.MachineTranslationModel.create(
            source_language_code='en',
            target_language_code='es',
            source_text='hello world',
            translated_text='hola mundo'
        )
        # Ruling out the possibility of None for mypy type checking.
        assert model_id is not None
        translation_model = (
            translation_models.MachineTranslationModel.get(model_id))
        # Ruling out the possibility of None for mypy type checking.
        assert translation_model is not None
        self.assertEqual(translation_model.translated_text, 'hola mundo')

    def test_create_model_with_same_source_target_language_codes_returns_none(
            self
    ) -> None:
        model_id = translation_models.MachineTranslationModel.create(
            source_language_code='en',
            target_language_code='en',
            source_text='hello world',
            translated_text='hello world'
        )
        self.assertIsNone(model_id)

    def test_get_machine_translation_with_existing_translation(self) -> None:
        translation_models.MachineTranslationModel.create(
            source_language_code='en',
            target_language_code='es',
            source_text='hello world',
            translated_text='hola mundo'
        )
        translation = (
            translation_models.MachineTranslationModel
            .get_machine_translation(
                source_language_code='en',
                target_language_code='es',
                source_text='hello world',
            )
        )
        self.assertIsNotNone(translation)
        # Ruling out the possibility of None for mypy type checking.
        assert translation is not None
        self.assertEqual(translation.translated_text, 'hola mundo')

    def test_get_machine_translation_with_no_existing_translation_returns_none(
            self
    ) -> None:
        translation = (
            translation_models.MachineTranslationModel
            .get_machine_translation(
                source_language_code='en',
                target_language_code='fr',
                source_text='hello world',
            )
        )
        self.assertIsNone(translation)

    def test_get_deletion_policy_not_applicable(self) -> None:
        self.assertEqual(
            translation_models.MachineTranslationModel.get_deletion_policy(),
            base_models.DELETION_POLICY.NOT_APPLICABLE)

    def test_get_model_association_to_user_not_corresponding_to_user(
            self
    ) -> None:
        self.assertEqual(
            (
                translation_models.MachineTranslationModel
                .get_model_association_to_user()
            ),
            base_models.MODEL_ASSOCIATION_TO_USER.NOT_CORRESPONDING_TO_USER)

    def test_get_export_policy_not_applicable(self) -> None:
        self.assertEqual(
            translation_models.MachineTranslationModel.get_export_policy(),
            {
                'created_on': base_models.EXPORT_POLICY.NOT_APPLICABLE,
                'deleted': base_models.EXPORT_POLICY.NOT_APPLICABLE,
                'hashed_source_text': base_models.EXPORT_POLICY.NOT_APPLICABLE,
                'last_updated': base_models.EXPORT_POLICY.NOT_APPLICABLE,
                'source_text': base_models.EXPORT_POLICY.NOT_APPLICABLE,
                'source_language_code':
                    base_models.EXPORT_POLICY.NOT_APPLICABLE,
                'target_language_code':
                    base_models.EXPORT_POLICY.NOT_APPLICABLE,
                'translated_text': base_models.EXPORT_POLICY.NOT_APPLICABLE
            }
        )
