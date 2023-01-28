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

from controller import vlc

_VLC_STATE_PLAYING=vlc.State.Playing
_VLC_STATE_PAUSED=vlc.State.Paused
_VLC_STATE_STOPPED=vlc.State.Stopped
_VLC_STATE_ENDED=vlc.State.Ended


class Player(object):
    
    def __init__(self):
        self._instance = vlc.Instance(['--no-xlib'])
        self._media_player=self._instance.media_player_new()

    def play(self, file_path=False):
        
        if file_path:
            media=self._instance.media_new(file_path)
            media.parse()
            self._media_player.set_media(media)
        
        self._media_player.play()
    
    def stop(self):
        self._media_player.stop()
    
    def pause(self):
        self._media_player.pause()
        
    def set_volume(self, number):
        if number >=0 and number <= 100:
            self._media_player.audio_set_volume(int(number))
            
    def set_position(self, number):
        if number >=0 and number <= 1:
            self._media_player.set_position(number)
                        
    def get_volume(self):
        return self._media_player.audio_get_volume()

    def get_position(self):
        return self._media_player.get_position()

    def get_length(self):
        return self._media_player.get_length()

    def is_playing(self):
        if self._media_player.get_state() == _VLC_STATE_PLAYING:
            return True
            
        return False
        
    def is_paused(self):
        if self._media_player.get_state() == _VLC_STATE_PAUSED:
            return True
            
        return False
        
    def is_stopped(self):
        if self._media_player.get_state() == _VLC_STATE_STOPPED:
            return True
        
        return False
        
    def ended_playing(self):
        if self._media_player.get_state() == _VLC_STATE_ENDED:
            return True
            
        return False

    def _get_state(self):
        return self._media_player.get_state()


        
if __name__ == '__main__':
    
    import time
    p=Player()
    p.play('/home/public/music/BB Brunes/Nico Teen Love/01. Seul Ou Accompagne.ogg')
    time.sleep(2)
    p.stop()
    print(p.is_stopped())
