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

"""Methods to generate automatic voiceovers for exploration data."""


from __future__ import annotations

import collections
import itertools
import logging

from core import feconf
from core.platform import models

MYPY = False
if MYPY: # pragma: no cover
    from mypy_imports import voiceover_models
    from mypy_imports import question_models
    from mypy_imports import skill_models
    from mypy_imports import topic_models
    from mypy_imports import user_models

(voiceover_models, ) = (
    models.Registry.import_models([
        models.Names.VOICEOVER
    ])
)


def normalize_html_text(html_content: str) -> str:
    """This method processes HTML text to make it suitable for speech synthesis.
    It decodes HTML entities and parses the tags to normalize the content for
    better readability and auditory presentation.

    Args:
        html_content: str. The html content which needs to be normalized.

    Returns:
        str. The normalized string which is suitable for speech synthesis.
    """
    pass


def convert_raw_wav_to_raw_mp3_format(raw_wav_bytes: str) -> str:
    """Converts raw WAV audio format to raw MP3 audio format.

    Args:
        raw_wav_bytes: str. The raw WAV audio content.

    Returns:
        str. The raw MP3 audio content.
    """
    pass

