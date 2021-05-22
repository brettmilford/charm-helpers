#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2014-2015 Canonical Limited.
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

from charmhelpers.core.hookenv import (
    log,
    DEBUG,
    ERROR,
    WARNING,
)

import re

WMARK_MAX = 1000
WMARK_DEFAULT = 10
MAX_PAGES = 250000000 #~1T of 4K pages
MIN_PAGES = 4000000 #~16G of 4K pages
P = re.compile('\d+')


def calculate_watermark_scale_factor():
    """Calculates optimal vm.watermark_scale_factor value

    :returns: watermark_scale_factor
    :type: int
    """

    normal_managed_pages = []
    with open('/proc/zoneinfo', 'r') as f:
        for line in f.read().splitlines():
            if "Node" in line and "zone" in line:
                zone = [v for v in line.split(' ')
                        if v in ["DMA","DMA32","Normal","Movable","Device"]][0]
                node = int(P.search(line).group()) #int([v for v in line.split(' ') if P.match(v)][0].rstrip(','))

            if zone == "Normal" and "managed" in line:
                managed = int([v for v in line.split(' ') if P.match(v)][0])
                normal_managed_pages.append(managed)

    # getconf PAGESIZE
    wmark = min([watermark_scale_factor(managed_pages)
                 for managed_pages in normal_managed_pages])
    log(f"vm.watermark_scale_factor: {wmark}", DEBUG)
    return wmark

def watermark_scale_factor(managed_pages, page_size=4096):
    return int((managed_pages - MIN_PAGES)/(MAX_PAGES - MIN_PAGES) * (WMARK_MAX - WMARK_DEFAULT) + WMARK_DEFAULT)
