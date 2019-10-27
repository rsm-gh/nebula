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


from typing import Union, List


class DataRequest(object):
    """
        This class is used for storing the data associated to the user data (tracks) requests.
        
        When the user uses the GUI and selects some; playlist, genre, album, artists or a 
        manual filter, he creates a data request that will be searched in the database and
        loaded in the GUI.
    """
    
    
    def __init__(self,
                play_track: bool,
                force_update: bool,
                request_filter: Union[str, None], 
                playlist_id: Union[int, None],
                genres: Union[List[str], None], 
                artists_id: Union[List[int], None], 
                albums_id: Union[List[int], None]):
        
        """
            Args:
                play_track (bool): If once the request loaded in the GUI, a track should be played.
                force_update (bool): Requests containing the same information are not loaded.
                                     If force_update=True, that condition is ignored.
                request_filter (Union[str, None]): Filter created by the user.
                playlist_id (Union[int, None]): Playlist ID.
                genres (Union[List[str], None]): List of genres names.
                artists_id (Union[List[int], None]): List of the artists ID.
                albums_id (Union[List[int], None]): List of the albums ID.
        """
    
    
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
    
    