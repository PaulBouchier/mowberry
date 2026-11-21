# mowberry
This repo contains support for the mowberry mower project.

# Nodes

## print_zedf9p_pos

This node prints the rover position for GPS fixes from a ZED-F9P rover. By
default it provides X/Y/Z offset from a local origin as reported by
a gps_xy_node. In verbose mode, also prints Lat/Lon and UTM coordinates.
This node differs from print_pos in the lc29h_da_rtk_gps_driver package
by not interpreting the status field from the NavSatFix message, which is
not populated the same way on the ZED-F9P.

### Topics

- **fix**: NavSatFix message from ZED-F9P. Typically you could start the
ZED-F9P with ros2 launch ublox_dgnss ublox_rover_hpposllh.launch.py to
get it to publish NavSatFix with llh.

### Example run command

```bash
ros2 run lc29h_da_rtk_gps_driver print_pos --ros-args -p verbose:=true -r /gps/fix:=/fix
```

## send_lc_corr_udp

A non-ROS script that reads corrections from an LC29H(BA) and sends them to the matching
UDP receiver script rx_lc_corr_udp. It is intended to run on pizero.

## rx_lc_corr_udp

A ROS node which receives corrections sent by UDP from send_lc_corr_udp.py and publishes them
to /rtcm. It also publishes diagnostic messages with status of data received, and warns if
the rate falls below the expected 1 Hz - useful for detecting loss of corrections.

# Launch files

## buz.launch.py - Bringup mowberry with zedf9p GPS

Launches:
- linorobot2_bringup bringup.launch.py with serial port pointing to ESP32
- Includes zedf9p_ntrip.launch.py - see documentation below

## zedf9p_ntrip.launch.py

Launches zedf9p and ntrip connected by default to VN1 on rtk2go

Status: not fully checked out with zedf9p. zedf9p needs some topic remapping to connect to fusioncore. Launches  zedf9p_gps_xy_node which consumes /fix (NavSatFix) and emits /gps/zedf9p_xy - the xy delta from the local origin

## bu_lc.launch.py

Launches:
- linorobot2_bringup bringup.launch.py with the serial port set for mowberry
- lc29h(DA) gps receiver node
- rx_lc_corr_udp corrections receiver node
- gps_to_local_map_pose node with arguments that convert the received lat/lon to X/Y referenced to some point defined in parameters

## ublox_rover_hpposllh_navsatfix.launch.py

A version of the ublox launch file of the same name which launches the
ublox_dgnss driver node and pulls corrections from topic /rtcm (vs. the
ntrip_client/rtcm topic which is the default for the ublox launch file.)

## zedf9p_lc29h.launch.py

This launch file runs both a ZED-F9P and a LC29H(DA) GPS receiver side by side, and feeds them both corrections from an ntrip_client it starts. It
runs two gps_xy_node instances - one for each receiver - which convert the fix messages from each receiver into local offset position messages.

The launch starts the ublox_dgnss node to handle the ZED-F9P, which is
expected to be on /dev/ACM0 (changeable by parameter). It starts the
lc29h_da_rtk_gps_driver node, which is expected to be on /dev/ttyUSB0
(changeable by parameter). It does the appropriate topic remapping so
that the two instances of gps_xy_node use the appropriate topics for each
receiver.

### Example run command

```bash
ros2 launch mowberry zedf9p_lc29h.launch.py host:=rtk2go.com mountpoint:=VN1 username:=YOUR_EMAIL password:=none authenticate:=true send_nmea:=false
```

