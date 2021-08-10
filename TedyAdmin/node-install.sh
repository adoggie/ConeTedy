#!/usr/bin/env bash

#usage:
# bash node-install.sh 22 scott 192.168.30.21 ./DemoPhoenix /home/scott/conetedy/repo

rsync -av -e 'ssh -p $1 -o StrictHostKeyChecking=no ' $4 $2@$3:$5