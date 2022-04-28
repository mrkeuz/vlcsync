VLC Timeline Sync
=================

Utility for synchronize multiple instances of VLC supports seek, play and pause

# Run

```shell

# Run vlc (should with open --rc-host 127.0.0.42 option) 
vlc --rc-host 127.0.0.42 SomeMedia1.mkv
vlc --rc-host 127.0.0.42 SomeMedia2.mkv
vlc --rc-host 127.0.0.42 SomeMedia3.mkv

# vlcsync will find all vlc on 127.0.0.42:*
# and start sync 
vlcsync
```

## Install

```shell
pip3 install -U .
```
