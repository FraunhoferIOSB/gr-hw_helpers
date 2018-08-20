#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

        try:
            self.uhd_dev = eval("self.parent.%s"%(self.device_name))
            sensor_names = self.uhd_dev.get_mboard_sensor_names()
        except:
            self.uhd_dev = None
            gr.log.warn("UHD Device not found, re-check the block config")
            return False

        

    

        if 'gps_locked' in sensor_names:
            while not self.uhd_dev.get_mboard_sensor('gps_locked').to_bool():
                pass

            self.uhd_dev.set_time_source('gpsdo')
            last = self.uhd_dev.get_time_last_pps()
            next = self.uhd_dev.get_time_last_pps()
            while last == next:
                time.sleep(0.05)
                next = self.uhd_dev.get_time_last_pps()
            time.sleep(0.1)
            
            self.uhd_dev.set_time_next_pps(uhd.time_spec_t(self.uhd_dev.get_mboard_sensor('gps_time').to_int() + 1))
            time.sleep(1.1)
            self.has_gps_sensor = True
            self.timer.start()
        else:
            gr.log.info("No GPSDO found using OS time")
            self.uhd_dev.set_time_next_pps(uhd.time_spec_t(int(time.time()) + 1))
            self.has_gps_sensor = False
            
        return True


    def stop(self):
        self.timer.cancel()
        return True



    def timer_tick(self):    

        if(self.has_gps_sensor):
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







                

        
        
