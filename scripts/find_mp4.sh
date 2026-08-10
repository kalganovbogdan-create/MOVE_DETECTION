#!/bin/zsh
#C:\Users\Bogdan1\Videos
find /mnt/c/Users/Bogdan1/Videos -type f -name "*.mp4" -exec du -h {} \; | sort -h
