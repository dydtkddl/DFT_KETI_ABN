#!/bin/bash

orca_bin="/home/ys/orca_6_0_1_linux_x86-64_shared_openmpi416/orca"

$orca_bin /home/ys/Research/PSID_server_room/orca/4nitroaniline_water_3/4nitroaniline_water_3.inp > \
          /home/ys/Research/PSID_server_room/orca/4nitroaniline_water_3/4nitroaniline_water_3.out

$orca_bin /home/ys/Research/PSID_server_room/orca/ABN_water_3/ABN_water_3.inp > \
          /home/ys/Research/PSID_server_room/orca/ABN_water_3/ABN_water_3.out

$orca_bin /home/ys/Research/PSID_server_room/orca/aniline_water_3/aniline_water_3.inp > \
          /home/ys/Research/PSID_server_room/orca/aniline_water_3/aniline_water_3.out

$orca_bin /home/ys/Research/PSID_server_room/orca/p_toluidine_water_3/p_toluidine_water_3.inp > \
          /home/ys/Research/PSID_server_room/orca/p_toluidine_water_3/p_toluidine_water_3.out
