#!/usr/bin/python3
#

#  Copyright (C) 2016  Rafael Senties Martinelli 
#
#  This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License 3 as published by
#   the Free Software Foundation.
#
#  This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software Foundation,
#   Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA.


import os
from getpass import getuser


class Paths:
    
    def __init__(self):
        
        user=getuser()
        current_dir=os.path.dirname(os.path.realpath(__file__))
        
        
        self.database='/home/{}/.config/banshee-1/banshee.db'.format(user)
        self.config='/home/{}/.config/adromeda.ini'.format(user)
        
        self.albums_artwork='/home/{}/.cache/media-art/90/{}.jpg'.format(user,'{}')
        self.albums_current='/home/{}/.cache/media-art/36/{}.jpg'.format(user,'{}')

        self.port='/tmp/{}-banshee-port'.format(user)
        self.plugins_dir='/etc/andromeda/'


        # local
        self.glade='{}/gui.glade'.format(current_dir)
        self.albums_artwork_default='{}/images/album_x90.jpg'.format(current_dir)
        self.albums_current_default='{}/images/album_x36.jpg'.format(current_dir)
        self.playlist='{}/images/playlist.png'.format(current_dir)


if __name__ == '__main__':
    p=Paths()
    print(p.port)
