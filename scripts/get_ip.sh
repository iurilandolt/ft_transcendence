#!/bin/bash

#get the private IP address of the machine

echo $(ifconfig | awk '/flags=4163<UP,BROADCAST,RUNNING,MULTICAST>/ {getline; print $2}')

