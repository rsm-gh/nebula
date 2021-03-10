*Unless you want to try experimental software or contribute to the project you should not yet use the player. I stopped developing it because I moved to spotify... but I may continue some day.*

----------------------------------------------------------------

![Andromeda GUI](https://raw.githubusercontent.com/rsm-gh/andromeda/master/usr/share/doc/andromeda/preview.jpeg)

Andromeda is a music player powered by Python3, GTK3 and pyVLC. I code it for GNU/Linux Systems and its look and behavior is pretty similar to [Banshee](http://banshee.fm).

Currently it can reproduce music, manage lists and queues, but the database import and modification stills to be finished / debugged. Also it is pretty easy to add pluggins to customize or code new features, examples can be found in `etc/andromeda/pluggins`.

Also, despite some widgets optimization, I find that the interface is a little bit slower than banshee which is mainly coded in C++. I noticed this with a database containing 14'650 tracks.

## How to Install

1. Download the [stable branch](https://github.com/rsm-gh/andromeda/archive/master.zip).
2. Install the dependencies:
    * Debian based distributions: `libgtk-3-0 (>= 3.10), vlc, python3, python3-gi, python3-gi-cairo`
    * ArchLinux: `?`

3. Execute the setup file.
