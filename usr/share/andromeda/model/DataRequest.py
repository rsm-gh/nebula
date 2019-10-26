#!/usr/bin/python3
#

#  Copyright (C) 2019  Rafael Senties Martinelli 
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


class DataRequest(object):
    
    
    def __init__(self,
                play_track,
                force_update,
                request_filter, 
                playlist_id,
                genres, 
                artists_id, 
                albums_id):
    
    
        self._filter = request_filter
        self._playlist_id = playlist_id
        self._genres = genres
        self._artists_id = artists_id
        self._albums_id = albums_id
        self._play_track = play_track
        self._force_update = force_update
        
    def __str__(self):
        return """\nDataRequest:
 _play_track={ptk}
 _force_update={force}
 _filter={filter}
 _playlist_id={plist}
 _genres={genres}
 _artists_id={artists}
 _albums_id={albums}\n""".format(ptk=self._play_track,
                                force=self._force_update,
                                filter=self._filter,
                                plist=self._playlist_id,
                                genres=self._genres,
                                artists=self._artists_id,
                                albums=self._albums_id)
    
    