![Nebula GUI](https://raw.githubusercontent.com/rsm-gh/nebula/master/usr/share/doc/nebula/preview.jpeg)

> This software is in a "experimental" stage because I moved to Spotify before finishing it. I may continue one day and include [my video player](https://github.com/rsm-gh/vlist-player).


Nebula is a music player powered with Python3, GTK+, Sqlite and pyVLC. I code it for GNU/Linux Systems and its look and behavior is pretty similar to [Banshee](https://www.banshee-project.org/).

Currently it can reproduce music, manage lists and queues, but the database import and modification stills to be finished / debugged. Also it is pretty easy to add pluggins to customize or code new features, examples can be found in `etc/nebula/pluggins`.

Also, despite some widgets optimization, I find that the interface is a little bit slower than banshee which is mainly coded in C++, I noticed this with a database containing 14'650 tracks (155 Gib).

## How to Install

1. Download the [stable branch](https://github.com/rsm-gh/nebula/archive/master.zip).
2. Install the dependencies:
    * Debian based distributions: `libgtk-3-0, vlc, python3, python3-gi, python3-gi-cairo gir1.2-ayatanaappindicator3-0.1`
    * ArchLinux: `?`

3. Execute the setup file.

## Features

[..todo]


### Console Commands
```
Usage: nebula [options..]

Playback Control Options

    --next                     Play the next track.
    --play                     Start playback
    --play-pause               Toggle playback
    --pause                    Pause playback
    --stop                     Completely stop playback
```

### Pluggins

[..todo]
