#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# MIT License
#
# Copyright (c) 2021 Flywire
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Information provider for VooV Meeting software downloads."""

import ssl
import certifi
import json

from autopkglib import Processor
from urllib.request import urlopen

__all__ = ["VooVMeetingInfoProvider"]

DOWNLOAD_INFO_URL = (
    "https://voovmeeting.com/wemeet-webapi/v2/config/query-download-info"
)


class VooVMeetingInfoProvider(Processor):
    """Determines the latest version of VooV Meeting available.

    Returns the URL, version, and md5 of the software.
    """

    description = __doc__
    input_variables = {
        "ARCH": {
            "required": False,
            "default": "x86_64",
            "description": (
                "The architecture type of the software package."
                "Should match the output of os.uname[4] or `uname -m`"
            ),
        },
    }
    output_variables = {
        "url": {"description": "The full url for the software download."},
        "version": {"description": "The version of the software download."},
        "md5": {"description": "The MD5 checksum of the software download."},
    }

    def main(self):
        """Main process."""
        # Debug output the URL we're using
        self.output(f"Query URL: {DOWNLOAD_INFO_URL}", 3)

        # Map the output of os.uname[4] or `uname -m` to the "instance" we need to download.
        arch_map = {"x86_64": "mac", "arm64": "mac_arm64"}
        # What architecture type is the recipe looking for.
        # Default to `x86_64` : `mac` for now.
        arch = self.env.get("ARCH") or self.input_variables["ARCH"]["default"]
        arch_instance = arch_map[arch]
        # Debug output for the arch we're using
        self.output(f"Architecture type: {arch}", 3)
        self.output(f"Architecture instance: {arch_instance}", 3)

        # Setup our JSON to be sent to the server to request the download URL.
        data_template = [{"instance": f"{arch_instance}", "type": "1410000198"}]
        data = json.dumps(data_template).encode("ascii")
        self.output(f"Full JSON being sent: {data}", 3)

        with urlopen(
            DOWNLOAD_INFO_URL,
            data,
            context=ssl.create_default_context(cafile=certifi.where()),
        ) as response:
            res = json.loads(response.read())

        for attribute in ("url", "version", "md5"):
            self.env[attribute] = res["data"][0][attribute]


if __name__ == "__main__":
    PROCESSOR = VooVMeetingInfoProvider()
    PROCESSOR.execute_shell()
