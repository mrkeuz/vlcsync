VLC Sync
========

Utility for synchronize multiple instances of VLC. Supports seek, play and pause. 
Inspired by F1 streams with extra driver tracking data.  

Motivation:

Did [not find](#alternatives) reasonable alternative for Linux. 
So decided to write my own solution.

Currently, tested on Linux, Windows 7/10 (macOS should also work).

## Install

```shell
pip3 install -U vlcsync
```

or 

Download [binary release](https://github.com/mrkeuz/vlcsync/releases) (Windows)

## Run

`Vlc` players should open with `--rc-host 127.0.0.42` option OR configured properly from gui (see [how configure vlc](./docs/vlc_setup.md)) 

```shell

# Run vlc players 
$ vlc --rc-host 127.0.0.42 SomeMedia1.mkv &
$ vlc --rc-host 127.0.0.42 SomeMedia2.mkv &
$ vlc --rc-host 127.0.0.42 SomeMedia3.mkv &

# Vlcsync will monitor all vlc players and do syncing 
$ vlcsync
```

## Demo

![vlcsync](./docs/vlcsync.gif)

## Alternatives

- [vlc](https://www.videolan.org/vlc/index.ru.html) 
    - Open additional media. Seems feature broken in vlc 3 (also afaik limited only 2 instances)  
    - There is a [netsync](https://wiki.videolan.org/Documentation:Modules/netsync/) but seem only master-slave (not tried)
- [Syncplay](https://github.com/Syncplay/syncplay) - very promised, but little [complicated](https://github.com/Syncplay/syncplay/discussions/463) for my case
- [bino](https://bino3d.org/) - working, buy very strange controls, file dialog not working and only fullscreen
- [gridplayer](https://github.com/vzhd1701/gridplayer) - low fps by some reason

## Contributing

Any thoughts, ideas and contributions welcome!  

Enjoy! 🚀
