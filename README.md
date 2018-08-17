# gr-hw_helpers
 
 Various GNURadio Blocks to interface with SDR Hardware 


__This is work in progress!__ Right now there are two blocks, which are specific to Ettus SDR Hardware.

## gps_info Block

This Block tries to change the internal time of a UHD SDR to the absolute time provided by the integerated gpsdo of it. Additional this block sends the NMEA data of the gpsdo to a local UDP socket, where it can be parsed by the gpsd Daemon. For debugging purposes this block has a message output where it is possible to monitor the GPS lock as well as the gps and internal time of the SDR.

```bash 
gpsd -nNG udp://localhost:12345
```


## channel_switcher

This Block changes the center frequency of an UHD SDR by generating control messages ase described in the [GNURadio documentation](https://www.gnuradio.org/doc/doxygen/page_uhd.html#uhd_command_syntax_cmds). 

