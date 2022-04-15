VLC Timeline Sync
=================

## How to run
"""
...
function f1_stream(){
  find . -name "*$1*.mkv" | parallel \vlc --rc-host 127.0.0.1 &>/dev/null & 
  /home/petr/Projects/_Learn/python/f1-stream/vlc_sync.py 
  fg
}
...
"""

"""bash 
cd GP
f1_stream Race
f1_stream Qal
"""


- Roadmap 
  
  - Nonblocking sockets instead slow func_timeout
  - Detect main window, time drift by offsets and remove all others logic
