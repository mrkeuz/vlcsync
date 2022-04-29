VLC Sync
========

Utility for synchronize multiple instances of VLC. Supports seek, play and pause. 
Inspired by F1 streams with extra driver tracking data.  

Motivation:

Did [not find](#alternatives) reasonable alternative for Linux. 
So decided to write my own solution.

# Run

`Vlc` instances should expose "Remote control interface" on 127.0.0.42 (see [how configure vlc](./docs/vlc_setup.md))

```shell

# Run vlc (should with open --rc-host 127.0.0.42 option) 
$ vlc --rc-host 127.0.0.42 SomeMedia1.mkv &
$ vlc --rc-host 127.0.0.42 SomeMedia2.mkv &
$ vlc --rc-host 127.0.0.42 SomeMedia3.mkv &

# vlcsync will find all vlc on 127.0.0.42:* and start syncing 
$ vlcsync

Vlcsync started...
Found instance with pid 3538289 and port 127.0.0.42:34759 State(play_state=playing, seek=10)
Found instance with pid 3538290 and port 127.0.0.42:38893 State(play_state=playing, seek=10)
Found instance with pid 3538291 and port 127.0.0.42:45615 State(play_state=playing, seek=10)
```

## Install

```shell
pip3 install -U vlcsync
```

## Status 

In development. Tested on Linux, Windows 10 (macOS should also work).

Any thoughts, ideas and contributions welcome!

Roadmap:

- [ ] Add ability to set static addresses i.e. for remote sync (to external pc/screen)
- [ ] Add portable `*.exe` build for Windows
- [ ] Automatic tune vlc [config](https://wiki.videolan.org/Preferences/#:~:text=Configuration%20File&text=Windows%3A%20%25appdata%25%5Cvlc%5C,%5CApplication%20Data%5Cvlc%5Cvlcrc) file for correct expose

## Alternatives

Possible alternatives:

- [vlc](https://www.videolan.org/vlc/index.ru.html) 
    - Open additional media. Seems feature broken in vlc 3 (also afaik limited only 2 instances)  
    - There is a [netsync](https://wiki.videolan.org/Documentation:Modules/netsync/) but seem only master-slave (not tried)
- [Syncplay](https://github.com/Syncplay/syncplay) - very promised but much [complicated](https://github.com/Syncplay/syncplay/discussions/463) for my task
- [bino](https://bino3d.org/) - working, very strange controls, file dialog not working, only fullscreen
- [gridplayer](https://github.com/vzhd1701/gridplayer) - low fps by some reason

## Demo

![vlcsync](./docs/vlcsync.gif)

Enjoy! 🚀