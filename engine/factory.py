# ibus-hiragana - Hiragana IME for IBus
#
# Copyright (c) 2024 Esrille Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

import gi
gi.require_version('IBus', '1.0')
from gi.repository import IBus

from engine import EngineHiragana

LOGGER = logging.getLogger(__name__)

ENGINE_PATH = '/com/esrille/IBus/engines/Hiragana/Engine/%d'


class EngineFactory(IBus.Factory):

    def __init__(self, bus: IBus.Bus, app) -> None:
        self._bus = bus
        self._app = app
        self._engine_id = 0
        super().__init__(connection=bus.get_connection(), object_path=IBus.PATH_FACTORY)

    def do_create_engine(self, engine_name: str) -> EngineHiragana:
        assert engine_name == 'hiragana', 'Invalid engine name'
        self._engine_id += 1
        return EngineHiragana(self._bus, ENGINE_PATH % self._engine_id, self._app)
