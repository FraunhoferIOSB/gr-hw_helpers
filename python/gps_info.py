#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2018 gr-argus author.
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
from gnuradio import gr, uhd
import pmt
import time
import socket
from threading import Timer


class gps_info(gr.sync_block):
    """
    docstring for block gps_info
    """
    def __init__(self, parent, uhd_device, update_rate = 1.0, udp_out = True, udp_port = 12345):
        gr.sync_block.__init__(self,
            name="gps_info",
            in_sig=None,
            out_sig=None)
        self.parent = parent
        self.device_name = uhd_device
        self.message_port_register_out(pmt.intern('gps_data'))
        if udp_out:
            self.udp_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            self.udp_port = udp_port
        self.update_rate = update_rate
        self.timer = Timer(self.update_rate, self.timer_tick)



    def start(self):
        self.uhd_dev = eval("self.parent.%s"%(self.device_name))

        gps_time =  self.uhd_dev.get_mboard_sensor('gps_time').to_int()
        gps_locked =  self.uhd_dev.get_mboard_sensor('gps_locked').to_bool()
        if gps_locked:
            self.uhd_dev.set_time_next_pps(uhd.time_spec_t(gps_time + 1.0))
            time.sleep(1.1)
        self.timer.start()
        return True


    def stop(self):
        self.timer.cancel()
        return True



    def timer_tick(self):       

        gps_gpgga = self.uhd_dev.get_mboard_sensor('gps_gpgga').value
        gps_gprmc = self.uhd_dev.get_mboard_sensor('gps_gprmc').value
        gps_time =  self.uhd_dev.get_mboard_sensor('gps_time').to_int()
        gps_locked =  self.uhd_dev.get_mboard_sensor('gps_locked').to_bool()
        uhd_time_set = False
        pps_seconds = self.uhd_dev.get_time_last_pps().to_ticks(1.0)

        if pps_seconds == gps_time:
            uhd_time_set = True
            
        
        gps_data = pmt.make_dict()
        gps_data = pmt.dict_add(gps_data, pmt.intern('gps_time'), pmt.to_pmt(gps_time))
        gps_data = pmt.dict_add(gps_data, pmt.intern('gps_locked'), pmt.to_pmt(gps_locked))
        gps_data = pmt.dict_add(gps_data, pmt.intern('usrp_time_is_absolute'), pmt.to_pmt(uhd_time_set))
        gps_data = pmt.dict_add(gps_data, pmt.intern('usrp_time'), pmt.to_pmt(pps_seconds))
        self.message_port_pub(pmt.intern('gps_data'), gps_data)
            
        if self.udp_socket:
            # send UDP
            self.udp_socket.sendto("\r\n" + gps_gprmc +"\r\n" + gps_gpgga, ("127.0.0.1" , self.udp_port))

        self.timer = Timer(self.update_rate, self.timer_tick)
        self.timer.start()







                

        
        
