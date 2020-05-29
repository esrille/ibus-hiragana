# ibus-hiragana - Hiragana IME for IBus
#
# Copyright (c) 2017-2020 Esrille Inc.
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

# EngineHiragana.__modifiers bits
ShiftL_Bit = 0x01
ShiftR_Bit = 0x02
ControlL_Bit = 0x04
ControlR_Bit = 0x08
AltL_Bit = 0x10
AltR_Bit = 0x20
Space_Bit = 0x40
Prefix_Bit = 0x80

Dual_ShiftL_Bit = ShiftL_Bit << 8
Dual_ShiftR_Bit = ShiftR_Bit << 8
Dual_ControlR_Bit = ControlR_Bit << 8
Dual_AltR_Bit = AltR_Bit << 8
Dual_Space_Bit = Space_Bit << 8
Dual_Bits = Dual_Space_Bit | Dual_ShiftL_Bit | Dual_ShiftR_Bit | Dual_ControlR_Bit | Dual_AltR_Bit

Not_Dual_ShiftL_Bit = ShiftL_Bit << 16
Not_Dual_ShiftR_Bit = ShiftR_Bit << 16
Not_Dual_ControlR_Bit = ControlR_Bit << 16
Not_Dual_AltR_Bit = AltR_Bit << 16
Not_Dual_Space_Bit = Space_Bit << 16
