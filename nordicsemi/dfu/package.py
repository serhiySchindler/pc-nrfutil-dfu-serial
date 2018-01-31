from __future__ import absolute_import
#
# Copyright (c) 2016 Nordic Semiconductor ASA
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#   1. Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
#   2. Redistributions in binary form must reproduce the above copyright notice, this
#   list of conditions and the following disclaimer in the documentation and/or
#   other materials provided with the distribution.
#
#   3. Neither the name of Nordic Semiconductor ASA nor the names of other
#   contributors to this software may be used to endorse or promote products
#   derived from this software without specific prior written permission.
#
#   4. This software must only be used in or with a processor manufactured by Nordic
#   Semiconductor ASA, or in or with a processor manufactured by a third party that
#   is used in combination with a processor manufactured by Nordic Semiconductor.
#
#   5. Any software provided in binary or object form under this license must not be
#   reverse engineered, decompiled, modified and/or disassembled.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# Python standard library
import os

# 3rd party libraries
from zipfile import ZipFile

# Nordic libraries
from nordicsemi.utility.exceptions import NordicSemiException
from nordicsemi.dfu.manifest import Manifest


class Package(object):
    """
        Packages and unpacks Nordic DFU packages. Nordic DFU packages are zip files that contains firmware and meta-information
        necessary for utilities to perform a DFU on nRF5X devices.

        The internal data model used in Package is a dictionary. The dictionary is expressed like this in
         json format:

         {
            "manifest": {
                "bootloader": {
                    "bin_file": "asdf.bin",
                    "dat_file": "asdf.dat",
                    "init_packet_data": {
                        "application_version": null,
                        "device_revision": null,
                        "device_type": 5,
                        "firmware_hash": "asdfasdkfjhasdkfjashfkjasfhaskjfhkjsdfhasjkhf",
                        "softdevice_req": [
                            17,
                            18
                        ]
                    }
                }
        }

        Attributes application, bootloader, softdevice, softdevice_bootloader shall not be put into the manifest if they are null

    """

    MANIFEST_FILENAME = "manifest.json"

    @staticmethod
    def unpack_package(package_path, target_dir):
        """
        Unpacks a Nordic DFU package.

        :param str package_path: Path to the package
        :param str target_dir: Target directory to unpack the package to
        :return: Manifest Manifest: Returns a manifest back to the user. The manifest is a parse datamodel
        of the manifest found in the Nordic DFU package.
        """

        if not os.path.isfile(package_path):
            raise NordicSemiException("Package {0} not found.".format(package_path))

        target_dir = os.path.abspath(target_dir)
        target_base_path = os.path.dirname(target_dir)

        if not os.path.exists(target_base_path):
            raise NordicSemiException("Base path to target directory {0} does not exist.".format(target_base_path))

        if not os.path.isdir(target_base_path):
            raise NordicSemiException("Base path to target directory {0} is not a directory.".format(target_base_path))

        if os.path.exists(target_dir):
            raise NordicSemiException(
                "Target directory {0} exists, not able to unpack to that directory.",
                target_dir)

        with ZipFile(package_path, 'r') as pkg:
            pkg.extractall(target_dir)

            with open(os.path.join(target_dir, Package.MANIFEST_FILENAME), 'r') as f:
                _json = f.read()
                """:type :str """

                return Manifest.from_json(_json)
