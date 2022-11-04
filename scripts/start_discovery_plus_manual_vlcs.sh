#!/usr/bin/env bash

killall vlc

vlc --rc-host 127.0.0.42 ~/.cache/vlssync/tests/test1.mp4 &> /dev/null &
vlc --rc-host 127.0.0.1:12345 ~/.cache/vlssync/tests/test1.mp4 &> /dev/null &

vlcsync --rc-host 127.0.0.1:12345
