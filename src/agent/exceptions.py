# ------------------------------------------------------------------------------
# Copyright 2021 Mohammad Reza Golsorkhi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------
# name: exceptions.py
# Description: custom Exception
# Version: 0.1.1
# Author: Mohammad Reza Golsorkhi
# ------------------------------------------------------------------------------


class InvalidOption(Exception):
    """
    Custom exception which is used to trigger the clean exit
    of all running threads and the main program.
    """
    pass


class JobNotRunning(Exception):
    """
    FunctionJob Not Running
    """
    pass


class DuplicateName(Exception):
    """
    DuplicateName
    """
    pass
