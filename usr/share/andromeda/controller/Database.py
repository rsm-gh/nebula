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

"""
    +   I ignore why the banshee developpers didn't added ON DELETE CASCADE
        to many of the entities. In order of do not modify the database I
        didn't add it neither.

"""

import sqlite3
import os
import urllib.parse

# local imports
from Paths import Paths; PATHS=Paths()


class Database:
    
    def __init__(self):
        self._connection = sqlite3.connect(PATHS.database, check_same_thread=False)
        self._cursor = self._connection.cursor()
        self._database_quering_queue=[]
        self._query_id=0
        
        self._standard_track_query='''
SELECT
    T.TrackID, T.TrackNumber, T.Title,           Ab.Title,           Ab.ArtistName,  Ar.Name,     T.BitRate,  T.SampleRate, BitsPerSample, 
    T.Comment, T.Composer,    T.Conductor,       T.DateAddedStamp,   T.DiscCount,    T.Uri,       T.FileSize, T.Genre,      T.AlbumID,
    T.Rating,  T.Duration,    T.LastPlayedStamp, T.LastSkippedStamp, T.SkipCount,    T.PlayCount, T.Score,    T.Year
FROM CoreTracks T
    JOIN CoreArtists Ar ON T.ArtistID = Ar.ArtistID
    JOIN CoreAlbums Ab  ON T.AlbumID = Ab.AlbumID
'''
        
        
        
    def close(self):
        self._connection.close()
            
    def _get(self, query, tup=False):
        """
            Get a single value from a query:
                If the value does not exists return None.
                If multiple values, return the first one.
                
            It accepts a tupple as second argument in order to pass
            variables to the execute() method.
            
            query must be a string
        """
        try:
            if tup:
                self._cursor.execute(query, tup)
            else:
                self._cursor.execute(query)
                
            data=self._cursor.fetchone()
            
            return data[0]
            
        except Exception as e:
            if not 'no such column' in str(e):
                print(e)
        
            return None
        
    def get_genres(self, filter=None, playlist_id=None):

        WHERE=[]
        ARGS=[]

        if playlist_id is not None:
            WHERE.append('''T.TrackID IN (SELECT TrackID FROM CorePlaylistEntries WHERE PlaylistID = ?)''')
            ARGS+=[playlist_id]
        
        if filter is not None:
            WHERE.append('''(T.TitleLowered like ? OR Ar.NameLowered like ? OR Ab.TitleLowered like ?)''')
            filter=['%{}%'.format(filter.lower())]
            ARGS+=filter*3


        if WHERE == []:
            self._cursor.execute('''SELECT Genre FROM CoreTracks GROUP BY Genre ORDER BY Genre''')            
        else:
            self._cursor.execute('''
SELECT T.Genre 
FROM CoreTracks T
    JOIN CoreArtists Ar ON T.ArtistID = Ar.ArtistID
    JOIN CoreAlbums Ab  ON T.AlbumID = Ab.AlbumID
WHERE {}
GROUP BY T.Genre
ORDER BY T.Genre'''.format(''' AND '''.join(item for item in WHERE)), ARGS)
        
        return self._cursor.fetchall()
                
    def get_artists(self, filter=None, playlist_id=None, genres=None):

        WHERE=[]
        ARGS=[]

        if playlist_id is not None:
            WHERE.append('''T.TrackID IN (SELECT TrackID FROM CorePlaylistEntries WHERE PlaylistID = ?)''')
            ARGS+=[playlist_id]
        
        if genres is not None:
            WHERE.append('''T.Genre IN ({})'''.format(','.join('?'*len(genres))))
            ARGS+=genres
                    
        if filter is not None:
            WHERE.append('''(T.TitleLowered like ? OR Ar.NameLowered like ? OR Ab.TitleLowered like ?)''')
            filter=['%{}%'.format(filter.lower())]
            ARGS+=filter*3
        
        if WHERE == []:
            self._cursor.execute('''
SELECT Ar.ArtistID, Ar.Name 
FROM CoreTracks T
    JOIN CoreArtists Ar ON T.ArtistID = Ar.ArtistID
GROUP BY Ar.ArtistID
ORDER BY Name''')
        
        else:
            self._cursor.execute('''
SELECT Ar.ArtistID, Ar.Name 
FROM CoreTracks T
    JOIN CoreArtists Ar ON T.ArtistID = Ar.ArtistID
    JOIN CoreAlbums Ab  ON T.AlbumID = Ab.AlbumID
WHERE {}
GROUP BY Ar.ArtistID
ORDER BY Name   '''.format(''' AND '''.join(item for item in WHERE)), ARGS)
        
      

        return self._cursor.fetchall()


    def get_albums(self, filter=None, playlist_id=None, genres=None, artists_ids=None):

        WHERE=[]
        ARGS=[]

        if playlist_id is not None:
            WHERE.append('''T.TrackID IN (SELECT TrackID FROM CorePlaylistEntries WHERE PlaylistID = ?)''')
            ARGS+=[playlist_id]
        
        if genres is not None:
            WHERE.append('''T.Genre IN ({})'''.format(','.join('?'*len(genres))))
            ARGS+=genres
        
        if artists_ids is not None:
            WHERE.append('''Ar.ArtistID IN ({})'''.format(','.join('?'*len(artists_ids))))
            ARGS+=artists_ids
                    
        if filter is not None:
            WHERE.append('''(T.TitleLowered like ? OR Ar.NameLowered like ? OR Ab.TitleLowered like ?)''')
            filter=['%{}%'.format(filter.lower())]
            ARGS+=filter*3

        if WHERE == []:
            self._cursor.execute('''
SELECT Ab.ArtworkID, Ab.Title, Ab.ArtistName, Ab.AlbumID       
FROM CoreTracks T
    JOIN CoreArtists Ar ON T.ArtistID = Ar.ArtistID
    JOIN CoreAlbums Ab  ON T.AlbumID = Ab.AlbumID
GROUP BY Ab.ArtworkID
ORDER BY Ar.Name, Ab.Title''')

        else:
            self._cursor.execute('''
SELECT Ab.ArtworkID, Ab.Title, Ab.ArtistName, Ab.AlbumID       
FROM CoreTracks T
    JOIN CoreArtists Ar ON T.ArtistID = Ar.ArtistID
    JOIN CoreAlbums Ab  ON T.AlbumID = Ab.AlbumID
WHERE {}
GROUP BY Ab.ArtworkID
ORDER BY Ar.Name, Ab.Title'''.format(''' AND '''.join(item for item in WHERE)), ARGS)

        return self._cursor.fetchall()


    def get_tracks(self, filter=None, playlist_id=None, genres=None, artists_ids=None, albums_ids=None):
 
        WHERE=[]
        ARGS=[]
        
        if playlist_id is not None:
            WHERE.append('''T.TrackID IN (SELECT TrackID FROM CorePlaylistEntries WHERE PlaylistID = ?)''')
            ARGS+=[playlist_id]
        
        if genres is not None:
            WHERE.append('''T.Genre IN ({})'''.format(','.join('?'*len(genres))))
            ARGS+=genres
        
        if artists_ids is not None:
            WHERE.append('''Ar.ArtistID IN ({})'''.format(','.join('?'*len(artists_ids))))
            ARGS+=artists_ids
        
        if albums_ids is not None:
            WHERE.append('''Ab.AlbumID IN ({})'''.format(','.join('?'*len(albums_ids))))
            ARGS+=albums_ids
            
        if filter is not None:
            WHERE.append('''(T.TitleLowered like ? OR Ar.NameLowered like ? OR Ab.TitleLowered like ?)''')
            filter=['%{}%'.format(filter.lower())]
            ARGS+=filter*3
      
      
        if WHERE == []:
            self._cursor.execute('''{} GROUP BY T.TrackID ORDER BY Ar.Name, Ab.Title, T.Title'''.format(self._standard_track_query))
        else:
            self._cursor.execute('''
{} 
WHERE {}
GROUP BY T.TrackID
ORDER BY Ar.Name, Ab.Title, T.Title'''.format(self._standard_track_query, ''' AND '''.join(item for item in WHERE)), ARGS)
            
        return self._cursor.fetchall()
   
    
    def get_tracks_count(self):
        self._cursor.execute('''SELECT COUNT(T.TrackID) FROM CoreTracks T''')
        return self._cursor.fetchall()[0][0]


    def get_artwork_id_from_album_id(self, albumId):        
        return self._get('''SELECT ArtworkID FROM CoreAlbums WHERE CoreAlbums.AlbumID = ?''', (albumId,))
    
    
    def get_tracks_from_ids(self, track_ids):
        
        query='''{} WHERE T.TrackID IN ({})'''.format(self._standard_track_query, ','.join('?'*len(track_ids)))

        self._cursor.execute(query, track_ids)

        return self._cursor.fetchall()
        
        
    def get_playlists(self, play_queue=False):
        """
            Banshee creates a list called "Play Queue" in order to keep the queue.
            Since I ignore if the id of the list is always the same this method will simply
            ignore the list by name.
        """
        if play_queue:
            self._cursor.execute('''SELECT PlaylistID, Name FROM CorePlaylists ORDER BY Name''')
        else:
            self._cursor.execute('''SELECT PlaylistID, Name FROM CorePlaylists WHERE Name != "Play Queue" ORDER BY Name''')
            
            
        return self._cursor.fetchall()
        
    #def get_track_ids_with_duplicated_artist_album_title(self):
        
        
        
    def get_playlist_tracks_count(self, playlist_id):
        self._cursor.execute('''
SELECT COUNT(E.EntryID) 
FROM CorePlaylists P
    JOIN CorePlaylistEntries E on E.PlaylistID = P.PlaylistID
WHERE P.PlaylistID = ?''', (playlist_id,))
        return self._cursor.fetchall()[0][0]

        
    def get_track_with_duplicated_uri(self):
        """
            Find duplicated tracks pointing to the same hard_drive file,
            but with different id.
        """
        self._cursor.execute('''
{}
WHERE T.Uri IN (SELECT Uri FROM CoreTracks GROUP BY Uri HAVING COUNT(*) > 1)    
GROUP BY T.TrackID
ORDER BY T.Uri'''.format(self._standard_track_query))

        return self._cursor.fetchall()

    
    def get_track_ids_with_unexisting_uri(self):
        """
            Find all tracks ids that have an unexisting uri
        """
        self._cursor.execute('''SELECT TrackID, Uri FROM CoreTracks''')
        
        track_ids=[]
        for track_id, track_path in self._cursor.fetchall():
            track_path=urllib.parse.unquote(track_path).replace('file://','')
            if not os.path.exists(track_path):
                track_ids.append(track_id)

        return track_ids    
    
    def delete_playlist(self, playlist_id):
        self._cursor.execute('''DELETE FROM CorePlaylistEntries WHERE PlaylistID = ?''', (playlist_id,))
        self._cursor.execute('''DELETE FROM CorePlaylists WHERE PlaylistID = ?''', (playlist_id,))
        self._connection.commit()

    def delete_artist(self, artist_id):
        self._cursor.execute('''DELETE FROM CoreArtists WHERE ArtistID = ?''', (artist_id,))
        self._connection.commit()

    def delete_album(self, album_id):
        self._cursor.execute('''DELETE FROM CoreAlbums WHERE AlbumID = ?''', (album_id,))
        self._connection.commit()

    def delete_track(self, track_id):
        self._cursor.execute('''DELETE FROM CoreTracks WHERE TrackID = ?''', (track_id,))
        self._connection.commit()


    def clean_tracks_with_unexistent_uri(self):
        
        track_ids=self.get_track_ids_with_unexisting_uri()
        query='''DELETE FROM CoreTracks WHERE NOT TrackID IN ({})'''.format(','.join('?'*len(track_ids)))

        self._cursor.execute(query, track_ids)
        self._connection.commit()

    
    def clean_artists_and_albums_without_tracks(self, test=True):
        # *it is better to use `NOT EXISTS` instead  `NOT IN` because it will
        #  also delete the rows containing null id's
        
        # Check:
        # http://stackoverflow.com/questions/36314336/sql-delete-not-working-but-select-does
        
        if test == True:
            ## Check the albums
            #self._cursor.execute('''
#SELECT Ab.Title
#FROM CoreAlbums Ab
#WHERE NOT EXISTS (
    #SELECT T.AlbumID
    #FROM CoreTracks T
    #WHERE T.AlbumId = Ab.AlbumId)''')
            
            self._cursor.execute('''
SELECT Ab.Title
FROM CoreAlbums Ab
WHERE NOT Ab.AlbumID IN (
    SELECT T.AlbumID
    FROM CoreTracks T
    GROUP BY T.AlbumID)''')
            albums=self._cursor.fetchall()
        
            # Check the artists
            #self._cursor.execute('''
#SELECT Ar.Name
#FROM CoreArtists Ar
#WHERE NOT EXISTS (
    #SELECT T.ArtistID
    #FROM CoreTracks T
    #WHERE T.ArtistID = Ar.ArtistID)''')
            self._cursor.execute('''
SELECT Ar.Name
FROM CoreArtists Ar
WHERE NOT Ar.ArtistID IN (
    SELECT T.ArtistID
    FROM CoreTracks T
    GROUP BY T.ArtistID)''')  
            artists=self._cursor.fetchall()
        
            return albums, artists


        # Delete the albums
        #

        #self._cursor.execute('''
#DELETE Ab
#FROM CoreAlbums AS Ab
#WHERE (NOT EXISTS (
    #SELECT T.AlbumID
    #FROM CoreTracks T
    #WHERE T.AlbumId = Ab.AlbumId))''')

        self._cursor.execute('''SELECT AlbumID FROM CoreTracks GROUP BY AlbumID''')
        album_ids=[item[0] for item in self._cursor.fetchall()]
        query='''DELETE FROM CoreAlbums WHERE NOT AlbumId IN ({})'''.format(','.join('?'*len(album_ids)))
        self._cursor.execute(query, album_ids)

    
        #self._cursor.execute('''
#DELETE CoreAlbums
#FROM CoreAlbums
#WHERE NOT CoreAlbums.AlbumId IN (
    #SELECT AlbumID
    #FROM CoreTracks
    #GROUP BY AlbumID)''')

        self._connection.commit()
        
        # Delete the artists
        #

        #self._cursor.execute('''
#DELETE Ar
#FROM CoreArtists AS Ar
#WHERE (NOT EXISTS (
    #SELECT T.ArtistID
    #FROM CoreTracks T
    #WHERE T.ArtistID = Ar.ArtistID))''') 

        self._cursor.execute('''SELECT ArtistID FROM CoreTracks GROUP BY ArtistID''')
        album_ids=[item[0] for item in self._cursor.fetchall()]
        query='''DELETE FROM CoreArtists WHERE NOT ArtistId IN ({})'''.format(','.join('?'*len(album_ids)))
        self._cursor.execute(query, album_ids)


        self._connection.commit()
        
        
    def update_track_rating(self, track_id, rating):
        self._cursor.execute('''UPDATE CoreTracks SET Rating = ? WHERE TrackID = ?''', (rating, track_id))
        self._connection.commit()
        
    def update_track_paths(self, items):
        for old_path, new_path in items:
            self._cursor.execute('''UPDATE CoreTracks SET Uri = ? WHERE Uri = ?''', (new_path, old_path))
            self._connection.commit()
        
    def update_full_tracks(self, tracks_data):

        self._cursor.execute('''SELECT ArtistID, NameLowered FROM CoreArtists''')
        artists=self._cursor.fetchall()

        self._cursor.execute('''SELECT AlbumID, TitleLowered, ArtistID, Year FROM CoreAlbums''')
        albums=self._cursor.fetchall()
        

        #8:  T.TrackID, T.TrackNumber, T.Title, Ab.Title, Ab.ArtistName, Ar.Name, T.BitRate, T.SampleRate, BitsPerSample, 
        #17: T.Comment, T.Composer, T.Conductor, T.DateAddedStamp, T.DiscCount, T.Uri, T.FileSize, T.Genre, T.AlbumID,
        #25: T.Rating, T.Duration, T.LastPlayedStamp, T.LastSkippedStamp, T.SkipCount, T.PlayCount, T.Score, T.Year


        for track_data in tracks_data:
            """
                Create/modify the artist
            """
            artist_id=-1
            try:
                artist_lowered_name=track_data[5].lower()
            except:
                artist_lowered_name=None
            
            
            for artist_item in artists:
                if artist_lowered_name == artist_item[1]:
                    artist_id=artist_item[0]
            
            if artist_id == -1:
                data=(track_data[5], artist_lowered_name)
                self._cursor.execute('''INSERT INTO CoreArtists(Name, NameLowered) VALUES(?, ?)''', data)
                self._connection.commit()
                artist_id=self._cursor.lastrowid
                artists.append(data)
                
            
            """
                Create/modify the album
            """
            album_id=-1
            try:
                album_loweredtitle=track_data[3].lower()
            except:
                album_loweredtitle=None
            
            for album_item in albums:
                if album_loweredtitle == album_item[1]:
                    album_id=album_item[0]
                    album_artist_id=album_item[2]
                    album_year=album_item[3]
            
            if album_id == -1:
                # Create a new album
                # 
                data=(artist_id, track_data[3], album_loweredtitle, track_data[25])
                
                self._cursor.execute('''
INSERT INTO CoreAlbums(ArtistID, Title, TitleLowered, Year)
VALUES(?, ?, ?, ?)''', data)
            
                album_id=self._cursor.lastrowid
                self._connection.commit()
                albums.append(data)
            
            elif album_artist_id != artist_id or album_year != track_data[25]:
                # Update the current album
                #
                self._cursor.execute('''
UPDATE CoreAlbums
SET ArtistID = ?, Title = ?, TitleLowered = ?, Year = ?
WHERE AlbumID = ?''', (artist_id, track_data[3], album_loweredtitle, track_data[25], album_id))
                self._connection.commit()
                
            
            """
                Update the tracks table
            
            """
                    
            self._cursor.execute('''
UPDATE CoreTracks 
SET TrackNumber = ?,    Title = ?,      BitRate = ?,    SampleRate = ?, BitsPerSample = ?,      Comment = ?, 
    Composer = ?,       Conductor = ?,  DiscCount = ?,  Genre = ?,      Rating = ?,             PlayCount = ?, 
    Score = ?,          Year = ?,       AlbumID = ?,    ArtistID = ?
WHERE TrackID = ?''', ( track_data[1],  track_data[2],  track_data[6],  track_data[7],  track_data[8],  track_data[9],
                        track_data[10], track_data[11], track_data[13], track_data[16], track_data[18], track_data[23], 
                        track_data[24], track_data[25], album_id,       artist_id,      track_data[0])
                    )
            self._connection.commit()

    
    
    def increment_track_playcount(self, track_id):
        self._cursor.execute('''UPDATE CoreTracks SET PlayCount = PlayCount + 1 WHERE TrackID = ?''', (track_id,))
        self._connection.commit()
        self._cursor.execute('''SELECT PlayCount FROM CoreTracks WHERE TrackID = ?''', (track_id,))
        
        return self._cursor.fetchall()[0][0]
        
        
    def increment_track_skipcount(self, track_id):
        self._cursor.execute('''UPDATE CoreTracks SET SkipCount = SkipCount + 1 WHERE TrackID = ?''', (track_id,))
        self._connection.commit()
        self._cursor.execute('''SELECT SkipCount FROM CoreTracks WHERE TrackID = ?''', (track_id,))
        
        return self._cursor.fetchall()[0][0]


    def _(self):
        self._cursor.execute('''PRAGMA table_info(CoreArtists)''')
        
        data=self._cursor.fetchall()
        
        for row in data:
            print(row)
        
        for item in self._cursor.description:
            print(item)

        
if __name__ == '__main__':
    
    
    
    def printl(items):

        print('-'*20)

        if isinstance(items, str):
            print(items)
        elif items is None:
            print(None)
        else:
            for item in items:
                print(item)
                print()
    
    db=Database()

    
    
    
    
