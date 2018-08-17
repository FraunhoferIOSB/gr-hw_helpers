#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

import numpy
from gnuradio import gr
import pmt
from threading import Timer

class channel_switcher(gr.sync_block):
    """
    docstring for block channel_switcher
    """
    def __init__(self, freq_list=[], channel = -1, switching_interval=1.0):
        gr.sync_block.__init__(self,
            name="channel_switcher",
            in_sig=None,
            out_sig=None)
        self.msg_port_name = 'usrp_ctrl'
        self.message_port_register_out(pmt.intern(self.msg_port_name))
        self.freq_list = freq_list
        self.uhd_channel = channel
        self.current_idx = 0
        self.switching_interval = switching_interval
        self.timer = Timer(self.switching_interval, self.timer_tick)
        

    def start(self):
        self.timer.start()
        return True

    def stop(self):
        self.timer.cancel()
        return True

    

    def timer_tick(self):
        cmd = pmt.make_dict()
        cmd = pmt.dict_add(cmd, pmt.intern('chan'), pmt.to_pmt(self.uhd_channel))
        cmd = pmt.dict_add(cmd, pmt.intern('freq'), pmt.to_pmt(self.freq_list[self.current_idx]))
        cmd = pmt.dict_add(cmd, pmt.intern('tag'), pmt.from_long(1))

        self.message_port_pub(pmt.intern(self.msg_port_name),  cmd)

        self.current_idx = self.current_idx + 1
        self.current_idx = self.current_idx % len(self.freq_list)
        self.timer = Timer(self.switching_interval, self.timer_tick)
        self.timer.start()