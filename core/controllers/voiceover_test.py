# Copyright 2024 The Oppia Authors. All Rights Reserved.
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

"""Tests for the voiceover admin page."""

from __future__ import annotations

from core import feconf
from core.domain import user_services
from core.domain import voiceover_services
from core.tests import test_utils

from typing import Dict

MYPY = False
if MYPY: # pragma: no cover
    from mypy_imports import voiceover_models


class VoiceoverAdminPageTests(test_utils.GenericTestBase):
    """Checks the voiceover admin page functionality and its rendering."""

    def test_get_voiceover_admin_data(self) -> None:
        self.signup(self.CURRICULUM_ADMIN_EMAIL, self.CURRICULUM_ADMIN_USERNAME)
        self.set_curriculum_admins([self.CURRICULUM_ADMIN_USERNAME])
        self.login(self.CURRICULUM_ADMIN_EMAIL, is_super_admin=True)

        language_accent_master_list: Dict[str, Dict[str, str]] = (
            voiceover_services.get_language_accent_master_list())

        language_codes_mapping: Dict[str, Dict[str, bool]] = (
            voiceover_services.get_all_language_accent_codes_for_voiceovers())

        json_response = self.get_json(feconf.VOICEOVER_ADMIN_DATA_HANDLER_URL)

        self.assertDictEqual(
            json_response['language_accent_master_list'],
            language_accent_master_list)
        self.assertDictEqual(
            json_response['language_codes_mapping'],
            language_codes_mapping)

        self.logout()


class VoiceoverLanguageCodesMappingHandlerTests(test_utils.GenericTestBase):
    """The class validates language accent codes mapping field should
    update correctly.
    """

    def test_put_language_accent_codes_mapping_correctly(self) -> None:
        self.signup(self.CURRICULUM_ADMIN_EMAIL, self.CURRICULUM_ADMIN_USERNAME)
        self.set_curriculum_admins([self.CURRICULUM_ADMIN_USERNAME])
        self.login(self.CURRICULUM_ADMIN_EMAIL, is_super_admin=True)
        csrf_token = self.get_new_csrf_token()

        initial_language_codes_mapping: Dict[str, Dict[str, bool]] = (
            voiceover_services.get_all_language_accent_codes_for_voiceovers())
        self.assertDictEqual(
            initial_language_codes_mapping, {})
        expected_language_codes_mapping = {
            'en': {
                'en-US': True
            },
            'hi': {
                'hi-IN': False
            }
        }
        payload = {
            'language_codes_mapping': expected_language_codes_mapping
        }

        self.put_json(
            feconf.VOICEOVER_LANGUAGE_CODES_MAPPING_HANDLER_URL,
            payload, csrf_token=csrf_token)

        language_codes_mapping: Dict[str, Dict[str, bool]] = (
            voiceover_services.get_all_language_accent_codes_for_voiceovers())
        self.assertDictEqual(
            language_codes_mapping, expected_language_codes_mapping)

        self.logout()

    def test_invalid_language_accent_codes_mapping_raise_error(self) -> None:
        self.signup(self.CURRICULUM_ADMIN_EMAIL, self.CURRICULUM_ADMIN_USERNAME)
        self.set_curriculum_admins([self.CURRICULUM_ADMIN_USERNAME])
        self.login(self.CURRICULUM_ADMIN_EMAIL, is_super_admin=True)
        csrf_token = self.get_new_csrf_token()

        invalid_language_codes_mapping = {
            'en': 'en-US'
        }
        payload = {
            'language_codes_mapping': invalid_language_codes_mapping
        }

        response_dict = self.put_json(
            feconf.VOICEOVER_LANGUAGE_CODES_MAPPING_HANDLER_URL,
            payload, csrf_token=csrf_token, expected_status_int=400)
        self.assertEqual(
            response_dict['error'],
            'Schema validation for \'language_codes_mapping\' failed: '
            'Expected dict, received en-US')

        self.logout()


class VoiceArtistMetadataHandlerTests(test_utils.GenericTestBase):
    """The class validates functionality related to voice artist metadata model.
    """

    def setUp(self) -> None:
        super().setUp()
        self.signup(self.CURRICULUM_ADMIN_EMAIL, self.CURRICULUM_ADMIN_USERNAME)
        self.set_curriculum_admins([self.CURRICULUM_ADMIN_USERNAME])
        auth_id = 'someUser'
        self.voice_artist_username = 'username'
        user_settings = user_services.create_new_user(
            auth_id, 'user@example.com')
        self.voice_artist_id = user_settings.user_id
        user_services.set_username(
            self.voice_artist_id, self.voice_artist_username)

        self.voiceover1: voiceover_models.VoiceoverDict = {
            'filename': 'filename1.mp3',
            'file_size_bytes': 3000,
            'needs_update': False,
            'duration_secs': 6.1
        }
        self.voiceover2: voiceover_models.VoiceoverDict = {
            'filename': 'filename2.mp3',
            'file_size_bytes': 3500,
            'needs_update': False,
            'duration_secs': 5.9
        }
        self.voiceover3: voiceover_models.VoiceoverDict = {
            'filename': 'filename3.mp3',
            'file_size_bytes': 3500,
            'needs_update': False,
            'duration_secs': 5.0
        }

        self.voiceovers_and_contents_mapping: (
            voiceover_models.VoiceoversAndContentsMappingType) = {
            'en': {
                'language_accent_code': '',
                'exploration_id_to_content_ids': {
                    'exp_1': ['content_1', 'content_2', 'content_3']
                },
                'exploration_id_to_voiceovers': {
                    'exp_1': [
                        self.voiceover1,
                        self.voiceover2,
                        self.voiceover3
                    ]
                }
            }
        }

        voiceover_services.update_voice_artist_metadata(
            voice_artist_id=self.voice_artist_id,
            voiceovers_and_contents_mapping=(
                self.voiceovers_and_contents_mapping)
        )

    def test_get_voice_artist_data_for_voiceover_admin_page(self) -> None:
        self.login(self.CURRICULUM_ADMIN_EMAIL, is_super_admin=True)

        expected_voice_artist_id_to_language_mapping = {
            self.voice_artist_id: {
                'en': ''
            }
        }
        expected_voice_artist_id_to_voice_artist_name = {
            self.voice_artist_id: self.voice_artist_username
        }
        json_response = self.get_json(feconf.VOICE_ARTIST_METADATA_HANDLER)

        self.assertDictEqual(
            json_response['voice_artist_id_to_language_mapping'],
            expected_voice_artist_id_to_language_mapping
        )
        self.assertDictEqual(
            json_response['voice_artist_id_to_voice_artist_name'],
            expected_voice_artist_id_to_voice_artist_name
        )
        self.logout()

    def test_should_update_voice_artist_language_mapping(self) -> None:
        self.login(self.CURRICULUM_ADMIN_EMAIL, is_super_admin=True)
        csrf_token = self.get_new_csrf_token()

        initial_voice_artist_id_to_language_mapping = {
            self.voice_artist_id: {
                'en': ''
            }
        }
        voice_artist_id_to_language_mapping = (
            voiceover_services.get_all_voice_artist_language_accent_mapping())

        self.assertDictEqual(
            voice_artist_id_to_language_mapping,
            initial_voice_artist_id_to_language_mapping
        )

        payload = {
            'voice_artist_id': self.voice_artist_id,
            'language_code': 'en',
            'language_accent_code': 'en-US'
        }
        self.put_json(
            feconf.VOICE_ARTIST_METADATA_HANDLER,
            payload, csrf_token=csrf_token)

        final_voice_artist_id_to_language_mapping = {
            self.voice_artist_id: {
                'en': 'en-US'
            }
        }
        voice_artist_id_to_language_mapping = (
            voiceover_services.get_all_voice_artist_language_accent_mapping())

        self.assertDictEqual(
            voice_artist_id_to_language_mapping,
            final_voice_artist_id_to_language_mapping
        )
        self.logout()

    def test_get_exp_id_to_filenames_for_given_voice_artist(self) -> None:
        self.login(self.CURRICULUM_ADMIN_EMAIL, is_super_admin=True)

        handler_url = (
            '%s/%s/%s' % (
                feconf.GET_SAMPLE_VOICEOVERS_FOR_VOICE_ARTIST,
                self.voice_artist_id,
                'en')
        )

        expected_exp_id_to_filenames = {
            'exp_1': ['filename3.mp3', 'filename2.mp3', 'filename1.mp3']
        }

        json_response = self.get_json(handler_url)

        self.assertDictEqual(
            json_response['exploration_id_to_filenames'],
            expected_exp_id_to_filenames
        )
        self.logout()
