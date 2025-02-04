# Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

##
# @file   legality_check.py
# @author Yibo Lin
# @date   Jan 2020
#

import math
import torch
from torch import nn
from torch.autograd import Function

import dreamplace.ops.legality_check.legality_check_cpp as legality_check_cpp


class LegalityCheck(object):
    """Check legality including,
    1. out of boundary
    2. row and site alignment
    3. overlap
    4. fence region
    """

    def __init__(
        self,
        node_size_x,
        node_size_y,
        flat_region_boxes,
        flat_region_boxes_start,
        node2fence_region_map,
        fp_info,
        num_terminals,
        num_movable_nodes,
    ):
        super(LegalityCheck, self).__init__()
        self.node_size_x = node_size_x
        self.node_size_y = node_size_y
        self.flat_region_boxes = flat_region_boxes
        self.flat_region_boxes_start = flat_region_boxes_start
        self.node2fence_region_map = node2fence_region_map
        self.fp_info = fp_info
        self.num_terminals = num_terminals
        self.num_movable_nodes = num_movable_nodes

    def __call__(self, pos):
        return self.forward(pos)

    def forward(self, pos):
        """
        @param pos current roughly legal position
        """
        if pos.is_cuda:
            pos_cpu = pos.cpu()
        else:
            pos_cpu = pos
        return legality_check_cpp.forward(
            pos_cpu,
            self.node_size_x.cpu(),
            self.node_size_y.cpu(),
            self.flat_region_boxes.cpu(),
            self.flat_region_boxes_start.cpu(),
            self.node2fence_region_map.cpu(),
            self.fp_info.xl,
            self.fp_info.yl,
            self.fp_info.xh,
            self.fp_info.yh,
            self.fp_info.site_width,
            self.fp_info.row_height,
            self.fp_info.scale_factor,
            self.num_terminals,
            self.num_movable_nodes,
        )
