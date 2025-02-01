#!/bin/sh

clear && while true; do 
    output=$(printf "\ec"; python3 src/mdtparse.py logs/mapdoortext.log | tail -n `tput lines`);
    echo "$output";
done