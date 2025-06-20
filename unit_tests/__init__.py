# Copyright 2025 Canonical Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
from unittest import mock


sys.modules["charmhelpers.contrib.openstack.utils"] = mock.MagicMock()
sys.modules["charmhelpers.contrib.network.ip"] = mock.MagicMock()

# Mock charmhelpers functions with side effects.
import charms_openstack.test_mocks  # noqa

charms_openstack.test_mocks.mock_charmhelpers()
