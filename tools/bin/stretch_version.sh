#!/bin/bash

echo "# -----------------------------------------------"
echo "# VERSION INFORMATION FOR THE STRETCH RE FROM HELLO ROBOT"
echo "# -----------------------------------------------"
echo
echo "# stretch_about_text.py"
stretch_about_text.py
echo
echo "# -----------------------------------------------"
echo
echo "# uname -a"
uname -a
echo
echo "# -----------------------------------------------"
echo
echo "# rs-fw-update -l"
rs-fw-update -l
echo
echo "# -----------------------------------------------"
echo
echo "# cd $HOME/catkin_ws/src/stretch_ros"
echo "# git log -1 "
cd $HOME/catkin_ws/src/stretch_ros
git log -1
echo
echo "# -----------------------------------------------"
echo
echo "# python -m pip list | grep hello"
python -m pip list | grep hello
echo
echo "# -----------------------------------------------"
echo
echo "# python -m pip list | grep realsense"
python -m pip list | grep realsense
echo
echo "# -----------------------------------------------"
echo
echo "# python -m pip list | grep opencv"
python -m pip list | grep opencv
echo
echo "# -----------------------------------------------"
echo
echo "# python3 -m pip list | grep hello"
python3 -m pip list | grep hello
echo
echo "# -----------------------------------------------"
echo
echo "# python3 -m pip list | grep realsense"
python3 -m pip list | grep realsense
echo
echo "# -----------------------------------------------"
echo
echo "# python3 -m pip list | grep opencv"
python3 -m pip list | grep opencv
echo
echo "# -----------------------------------------------"
echo
echo "# apt list --installed | grep realsense"
apt list --installed | grep realsense
echo
echo "# -----------------------------------------------"
echo
echo "# apt list --installed | grep opencv"
apt list --installed | grep opencv
echo
echo "# -----------------------------------------------"
echo
echo "# REx_firmware_updater.py --current"
REx_firmware_updater.py --current
echo
echo "# -----------------------------------------------"
