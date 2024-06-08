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
from core.constants import constants
from core.domain import caching_services
from core.domain import classroom_config_services
from core.domain import html_cleaner
from core.domain import opportunity_services
from core.domain import role_services
from core.domain import skill_domain
from core.domain import skill_fetchers
from core.domain import state_domain
from core.domain import suggestion_services
from core.domain import taskqueue_services
from core.domain import topic_domain
from core.domain import topic_fetchers
from core.domain import topic_services
from core.domain import user_services
from core.platform import models

from typing import (
    Callable, Dict, List, Literal, Optional, Set, Tuple, cast, overload)

MYPY = False
if MYPY: # pragma: no cover
    from mypy_imports import question_models
    from mypy_imports import skill_models
    from mypy_imports import topic_models
    from mypy_imports import user_models

(skill_models, user_models, question_models, topic_models) = (
    models.Registry.import_models([
        models.Names.SKILL, models.Names.USER, models.Names.QUESTION,
        models.Names.TOPIC]))


