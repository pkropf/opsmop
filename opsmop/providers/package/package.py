# Copyright 2018 Michael DeHaan LLC, <michael@michaeldehaan.net>
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from opsmop.providers.provider import Provider

class Package(Provider):

    def _get_version(self):
        raise NotImplementedError()

    def plan(self):

        current_version = self._get_version()

        # FIXME: this can probably should advantage of the StrictVersion class to be smarter.
        if not current_version and self.absent:
            self.needs('uninstall')
        elif self.latest:
            self.needs('latest')
        elif self.version and self.version != current_version:
            self.needs('upgrade')
