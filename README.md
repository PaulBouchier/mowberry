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

# Launch files

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
