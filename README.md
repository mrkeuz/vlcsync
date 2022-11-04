VLC Sync
========

Utility for synchronize multiple instances of VLC. Supports seek, play and pause. 
  

#### Motivation

Strongly inspired by F1 streams with extra driver tracking data streams. Did [not find](#alternatives) reasonable alternative for Linux for playing several videos synchronously. So decided to write my own solution.

## Install

```shell
pip3 install -U vlcsync
```

or 

- Download [binary release](https://github.com/mrkeuz/vlcsync/releases) for Windows 7/10  
  NOTE: On some systems there are false positive Antivirus warnings [issues](https://github.com/mrkeuz/vlcsync/issues/1).
  In this case use [alternative way](./docs/install.md#windows-detailed-instructions) to install.   

## Run

`Vlc` players should open with `--rc-host 127.0.0.42` option OR configured properly from gui (see [how configure vlc](./docs/vlc_setup.md)) 

```shell

# Run vlc players 
$ vlc --rc-host 127.0.0.42 SomeMedia1.mkv &
$ vlc --rc-host 127.0.0.42 SomeMedia2.mkv &
$ vlc --rc-host 127.0.0.42 SomeMedia3.mkv &

# vlcsync will monitor and syncing all players
$ vlcsync

# Started from version 0.2.0

# For control remote vlc instances, 
# remote port should be open and rc interface listen on 0.0.0.0
$ vlcsync --rc-host 192.168.1.100:12345 --rc-host 192.168.1.50:54321

# For disable local discovery (only remote instances)
$ vlcsync --no-local-discovery --rc-host 192.168.1.100:12345

# For help and see all options
$ vlcsync --help
```

## Awesome 

Awesome [use-case](./docs/awesome.md) ideas

## Demo

![vlcsync](./docs/vlcsync.gif)

## Limitations 

- Frame-to-frame sync NOT provided. `vlc` does not have precise controlling via `rc` interface out of box. 
  Difference between videos can be **up to ~0.5 seconds** in worst case. Especially when playing from network share, 
  due buffering time and network latency.

- Currently, tested only on:
  - Linux (Ubuntu 20.04)
  - Windows 7 (32-bit)
  - Windows 10 (64-bit)

## Alternatives

- [vlc](https://www.videolan.org/vlc/index.ru.html) 
    - There is a [netsync](https://wiki.videolan.org/Documentation:Modules/netsync/) but seem only master-slave (tried, but not working by some reeason)
    - Open additional media. Seems feature broken in vlc 3 (also afaik limited only 2 streams)  
- [Syncplay](https://github.com/Syncplay/syncplay) - very promised, but little [complicated](https://github.com/Syncplay/syncplay/discussions/463) for sync different videos
- [bino](https://bino3d.org/) - working, very strange controls, file dialog not working and only fullscreen
- [gridplayer](https://github.com/vzhd1701/gridplayer) - low fps by some reason
- [mpv](https://github.com/mpv-player/mpv) - with [mixing multiple videos](https://superuser.com/a/1325668/1272472) in one window. Unfortunally does not support multiple screens
- [AVPlayer](http://www.awesomevideoplayer.com/) - only Win, macOS, up to 4 videos in free version

## Contributing

Any thoughts, ideas and contributions welcome!

Special thanks to **KorDen32** for inspiration! <img src="./docs/F1.svg" alt="F1" width="45"/>

Enjoy!
