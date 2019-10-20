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

    TO DO:
    
        > Activate the spin when modifiying data
        > Finish "edit tracks" for albums, and add to queue for all


    The state of some buttons/checkboxes is being saved at the configuration
    file by refering at the widget's label. This can cause problems and I'd like
    to do it by using the widget's id.
    
        >> How can I retrive the widget's id??




    RT: Root (Window)
    TE: Tracks Editor (Window)
    SE: Settings (Window)
    
    
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')
from gi.repository import Gtk, GObject, Gdk, Notify
from gi.repository import AppIndicator3 as appindicator
from gi.repository.GdkPixbuf import Pixbuf


import os
import sys
import socket
import traceback

from html import escape
from threading import Thread
from time import sleep, time
from fnmatch import fnmatch
from datetime import timedelta
from random import choice, shuffle


from CCParser import CCParser
from Database import Database
from Paths import Paths; PATHS=Paths()
from Player import Player
from texts import *


from CellRenderers.CellRendererRating import CellRendererRating
from CellRenderers.CellRendererTrackTime import CellRendererTrackTime, FORMAT_miliseconds
from CellRenderers.CellRendererBytes import CellRendererBytes, FORMAT_bytes
from CellRenderers.CellRendererTimeStamp import CellRendererTimeStamp
from CellRenderers.CellRendererURI import CellRendererURI, FORMAT_uri
from CellRenderers.CellRendererLongText import CellRendererLongText
from CellRenderers.CellRendererAlbum import CellRendererAlbum


os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(1, PATHS.plugins_dir)

def get_plugins_data():
    plugins_dict={}

    for filename in os.listdir(PATHS.plugins_dir):
                
        data={}
        
        if not filename.startswith('_') and filename.endswith('.py'):
            
            try:
            
                module=__import__(filename[:-3])
            
                module_name=module.__name__
            
                data['name']=module_name
                data['description']=module.__description__
                data['version']=module.__version__
                
                try:
                    data['date']=module.__date__
                except:
                    data['date']=''
                
                data['mantainer']=module.__mantainer__
                
                try:
                    data['website']=module.__website__
                except:
                    data['website']=''
            
                if not module_name in plugins_dict.keys():
                    plugins_dict[filename[:-3]]=data
            except Exception as e:
                print(traceback.format_exc())
    
    return plugins_dict


# Properties of the track editor
#

#8:  T.TrackID, T.TrackNumber, T.Title, Ab.Title, Ab.ArtistName, Ar.Name, T.BitRate, T.SampleRate, BitsPerSample, 
#17: T.Comment, T.Composer, T.Conductor, T.DateAddedStamp, T.DiscCount, T.Uri, T.FileSize, T.Genre, T.AlbumID,
#25: T.Rating, T.Duration, T.LastPlayedStamp, T.LastSkippedStamp, T.SkipCount, T.PlayCount, T.Score, T.Year

TE_STRING_TO_STRING=(   ('label_TE_title',2),('entry_TE_title',2),
                        ('label_TE_artist',5),('entry_TE_artist',5),
                        ('entry_TE_album_artist',4),
                        ('label_TE_album_title',3),
                        ('entry_TE_album_title',3),
                        ('combobox_entry_TE_genre',16),
                        ('entry_TE_composer',10),
                        ('entry_TE_conductor',11),
                        #('entry_TE_copyright',?),
                        ('entry_TE_comment',9),
                    )
                    
TE_INT_TO_INT=(     ('spinbutton_TE_tracknumber',1),
                    ('spinbutton_TE_disk_numb',22),
                    ('spinbutton_TE_rating',18),
                    ('spinbutton_TE_year',25),
                    ('spinbutton_TE_beats_per_minute',8),
                )

#
# Connect the checkbuttons of the TE
#
TE_checkbuttons_items=(
    ('togglebutton_TE_1','entry_TE_artist'),
    ('togglebutton_TE_2','entry_TE_album_artist'),
    ('togglebutton_TE_3','entry_TE_album_title'),
    ('togglebutton_TE_5','combobox_entry_TE_genre'),
    ('togglebutton_TE_4','entry_TE_composer'),
    ('togglebutton_TE_6','entry_TE_conductor'),
    ('togglebutton_TE_7','entry_TE_grouping'),
    ('togglebutton_TE_8','entry_TE_copyright'),
    ('togglebutton_TE_9','combobox_entry_TE_license'),
    ('togglebutton_TE_10','entry_TE_comment'),
)

def gtk_get_selected_cells_from_selection(gtk_selection, column=0):
    model, treepaths = gtk_selection.get_selected_rows()
    return [model[treepath][column] for treepath in treepaths]


def gtk_get_first_selected_cell_from_selection(gtk_selection, column=0):
    
    model, treepaths = gtk_selection.get_selected_rows()

    if treepaths==[]:
        return None
    
    return model[treepaths[0]][column]

def gtk_get_iter_from_liststore_cell(gtk_liststore, cell_value, column=0):
    
    treeiter = gtk_liststore.get_iter_first()
    while treeiter != None:
        if gtk_liststore.get_value(treeiter, column) == cell_value:
            return treeiter

        treeiter=gtk_liststore.iter_next(treeiter)
    
    return None
    
def gtk_liststore_has_value(gtk_liststore, cell_value, column=0):
    
    for row in gtk_liststore:
        if row[column]==cell_value:
            return True
    
    return False


def gtk_select_row_from_cell(gtk_treeview, column, cellvalue, safe_thread=False):

    gtk_liststore=gtk_treeview.get_model()
    gtk_selection=gtk_treeview.get_selection()

    if cellvalue is None:
        iter=gtk_liststore.get_iter_first()
    else:
        iter=gtk_get_iter_from_liststore_cell(gtk_liststore, cellvalue, column)
    
        if iter is None:
            iter=gtk_liststore.get_iter_first()

    if iter is not None: # when a liststore is empty
        if not safe_thread:
            Gdk.threads_enter()
            gtk_selection.select_iter(iter)
            Gdk.threads_leave()
        else:
            gtk_selection.select_iter(iter)


def gtk_shuffle_treeview(gtk_treeview):
    """ 
        It is not possible to use `liststore.reorder()` because
        the treeview is sorted.
    """
    
    gtk_treeview.set_sensitive(False)
    gtk_treeview.freeze_child_notify()
    
    gtk_liststore=gtk_treeview.get_model()
    gtk_treeview.set_model(None)

    gtk_liststore.set_default_sort_func(lambda *unused: 0)
    gtk_liststore.set_sort_column_id(-1, Gtk.SortType.ASCENDING)
   
    rows=[tuple(row) for row in gtk_liststore]
    shuffle(rows)
    
    gtk_liststore.clear()
    for row in rows:
        gtk_liststore.append(row)
    
    
    gtk_treeview.set_model(gtk_liststore)
    gtk_treeview.set_sensitive(True)
    gtk_treeview.thaw_child_notify()


def gtk_treeview_selection_is_okay(treeview, event):
    """
        When an user do a right click on a treeview, if click
        was not inside the selection, the selection will change.
    """
    
    try:
        pointing_treepath=treeview.get_path_at_pos(event.x, event.y)[0]
    except:
        return True
    
    treeview_selection=treeview.get_selection()

    # if the iter is not in the selected iters, remove the previous selection
    model, treepaths = treeview_selection.get_selected_rows()
    
    if not pointing_treepath in treepaths:
        treeview_selection.unselect_all()
        treeview_selection.select_path(pointing_treepath)


def gtk_get_selected_cells_from_iconview_selection(gtk_iconview, row=0):

    cells_data=[]
    liststore=gtk_iconview.get_model()
    
    for item in gtk_iconview.get_selected_items():
        treeiter = liststore.get_iter(item)
        if treeiter is not None:
            cells_data.append(liststore.get_value(treeiter, row))
            
    return cells_data



def label_to_configuration_name(label):
    return label.lower().replace(' ','_')


class GUI(Gtk.Window):
        
    def __init__(self):
        
        self.ccp=CCParser(ini_path=PATHS.config, section='Andromeda Music Player')
        
        """
            Init glade stuff
        """

        self.builder=Gtk.Builder()
        self.builder.add_from_file(PATHS.glade)
        self.builder.connect_signals(self)
        
        OBJECTS=(
            'window_root',
                'liststore_genres','liststore_artists','liststore_playlists','liststore_tracks','liststore_albums',
                    'liststore_general_playlists', 'liststore_tracks_historial', 'liststore_tracks_queue',
                'liststore_completion_artists', 'liststore_completion_genres','liststore_completion_albums',
                'treeview_RT_tracks_queue', 'treeview_RT_genres', 'treeview_RT_tracks', 'treeview_RT_artists','iconview_RT_albums',
                    'treeview_RT_tracks_historial',
                'treeview_selection_playlists','treeview_selection_queue', 'treeview_selection_historial',
                    'treeview_selection_general_playlists', 'treeview_selection_genres', 'treeview_selection_artists',
                    'treeview_selection_tracks',
                'label_track_title','label_album_title','label_track_progress','label_songs_stats',
                'menu_tracks','menu_tracks_queue','menu_on_playlist',
                'menuitem_repeat','menuitem_shuffle_off','menuitem_shuffle_by_track','radiomenuitem_repeat_off',
                    'radiomenuitem_repeat_all','menuitem_edit_tracks',
                'button_RT_play_pause','toolbutton_RT_next','searchentry','box_current_album','volumebutton','scale_RT_track_progress',
                'spinner','expander_more',
                'box_playing','box_queue','box_playing','box_historial','box_top_queue_tools','box_historial_tools',
                
            'indicator_menu',
                'indicator_menu_button','menuitem_indicator_button',
            
            'dialog_settings',
                'plugins_box',
            
            'dialog_track_editor',
                'button_TE_back','button_TE_back','button_TE_foward','button_TE_foward2','eventbox_TE_album',
                'label_TE_title','entry_TE_title','label_TE_artist','entry_TE_artist','entry_TE_album_artist','label_TE_current_track',
                    'label_TE_album_title','entry_TE_album_title','combobox_entry_TE_genre','spinbutton_TE_tracknumber',
                    'spinbutton_TE_disk_numb','spinbutton_TE_year','spinbutton_TE_rating',
                'entry_TE_composer','entry_TE_conductor','spinbutton_TE_beats_per_minute','entry_TE_copyright','entry_TE_comment',
                    'entry_TE_grouping','combobox_entry_TE_license',
                
            'dialog_about',
        )
        
        for object in OBJECTS:
            setattr(self, object, self.builder.get_object(object))


        #
        # Connect the right-click header menu to the track listore headers
        #
        # http://stackoverflow.com/a/34582432/3672754
        #
        treeview_labels=[]
        for id in range(3,27):
            for name in ('','_q','_h'):
                
                treeview_column_str='treeviewcolumn{}{}'.format(name, id)                
                setattr(self, treeview_column_str, self.builder.get_object(treeview_column_str))
                treeview_column = getattr(self, treeview_column_str)
                treeview_column_title = treeview_column.get_title()
                
                label=Gtk.Label(label=treeview_column_title)
                label.show()
                treeview_column.set_widget(label)
                
                widget = treeview_column.get_widget()
                while not isinstance(widget, Gtk.Button):
                    widget = widget.get_parent()
                widget.connect('button-press-event', self.on_treeview_RT_tracks_header_button_press_event)
   
                if name == '':
                    treeview_labels.append((treeview_column_title, id))
        
        #
        # Create the tracks right-click menu, set its default states and connect the signals
        #
        self.menu_tracks_header=Gtk.Menu()
        half=len(treeview_labels)//2

        
        for i, (_label, _id) in enumerate(sorted(treeview_labels, key=lambda x: x[0].lower())):

            # populate
            checkmenuitem=Gtk.CheckMenuItem(label=_label)
            if i < half:
                self.menu_tracks_header.attach(checkmenuitem, 0,1,i,i+1)
            else:
                self.menu_tracks_header.attach(checkmenuitem, 1,2,i-half,i+1-half)

            # read/set their state from the configuration
            conf_name=label_to_configuration_name('treeview_'+_label)
            
            
            treeview_column   = getattr(self, 'treeviewcolumn{}'.format(_id))
            treeview_column_q = getattr(self, 'treeviewcolumn_q{}'.format(_id))
            treeview_column_h = getattr(self, 'treeviewcolumn_h{}'.format(_id))
            
            if not self.ccp.get_bool_defval(conf_name, True):
                checkmenuitem.set_active(False)
                treeview_column.set_visible(False)
                treeview_column_q.set_visible(False)
                treeview_column_h.set_visible(False)
            else:
                checkmenuitem.set_active(True)
                treeview_column.set_visible(True)
                treeview_column_q.set_visible(True)
                treeview_column_h.set_visible(True)
            
            checkmenuitem.connect('activate', self.on_menuitem_tracks_clicked, _id)
            
        self.menu_tracks_header.show_all()
        
        
        #
        # Connect the checkbuttons of the TE.
        #

        for togglebutton_name, entry_name in TE_checkbuttons_items:
            togglebutton=self.builder.get_object(togglebutton_name)
            setattr(self, togglebutton_name, togglebutton)
            entry=getattr(self, entry_name)
            togglebutton.connect('toggled', self.on_togglebutton_TE_clicked, entry)

        #
        # Connect the `all` buttons of the TE
        #
        all_buttons=(
            ('button_TE_all_artist_name', 5),
            ('button_TE_all_album_artist', 4),
            ('button_TE_all_album_title', 3),
            ('button_TE_all_comment',9),
            ('button_TE_all_composer',10),
            ('button_TE_all_conductor',11),
            ('button_TE_all_genre', 16),
        )
        for button_id, column in all_buttons:
            object=self.builder.get_object(button_id)
            object.connect('clicked', self.on_button_TE_ALL_X_clicked, column)

        #
        # Initialize & Connect all the boolean buttons that should be simply saved in the configuration
        #
        toggle_buttons=(
            ('checkbutton_start_playing_on_startup', False),
            ('checkbutton_on_close_system_try', True),
            ('checkbutton_warning_when_deleteing_track_from_library', True),
            ('checkbutton_warning_when_deleteing_track_from_hardrive', True),
            ('checkbutton_display_notifications', True),
        )
        for button_name, default_state in toggle_buttons:
            object=self.builder.get_object(button_name)
            setattr(self, button_name, object)
            configuration_name=label_to_configuration_name(object.get_label())
            object.set_active(self.ccp.get_bool_defval(configuration_name, default_state))
            
            object.connect('toggled',self.on_toggle_button_toggled)
        
        """
            Some extra GUI/Glade initialization
        """
        self.treeview_selection_general_playlists.select_iter(self.liststore_general_playlists.get_iter_first())
        self.window_root.set_title(TEXT_PROGAM_NAME)
        self.label_album_title.set_text('')
        self.label_track_title.set_text('')
        self.label_track_progress.set_text('')
        
        self.box_queue.hide()
        self.box_historial.hide()
        self.box_playing.show()
        self.box_top_queue_tools.hide()
        self.box_historial_tools.hide()
        
        self.expander_more.set_expanded(self.ccp.get_bool_defval('expander_more', True))
        
        
        shuffle=self.ccp.get_str_defval('shuffle', 'tracks')
        if shuffle == 'tracks':
            self.menuitem_shuffle_by_track.set_active(True)
        else:
            self.menuitem_shuffle_off.set_active(True)
            
        
        toolbutton_suffle=self.builder.get_object('toolbutton_suffle')
        menu_shuffle=self.builder.get_object('menu_shuffle')
        toolbutton_suffle.set_menu(menu_shuffle)

        """
            Initialize the custom cellrenderers
        """
        
        # for the tracks
        for name in ('','_q','_h'):
            # file_size
            treeviewcolumn=getattr(self, 'treeviewcolumn{}16'.format(name))
            cellrenderer=CellRendererBytes()
            treeviewcolumn.pack_start(cellrenderer, True)
            treeviewcolumn.add_attribute(cellrenderer, 'bytes', 15)
            
            # rating
            treeviewcolumn=getattr(self, 'treeviewcolumn{}19'.format(name))
            cellrenderer=CellRendererRating()
            treeviewcolumn.pack_start(cellrenderer, True)
            treeviewcolumn.add_attribute(cellrenderer, 'rating', 18)
            cellrenderer.connect_rating(treeview_column, 18, self.on_cellrenderer_rating_changed)

            # time
            treeviewcolumn=getattr(self, 'treeviewcolumn{}20'.format(name))
            cellrenderer=CellRendererTrackTime()
            treeviewcolumn.pack_start(cellrenderer, True)
            treeviewcolumn.add_attribute(cellrenderer, 'miliseconds', 19)
    
            # date, last_played, last_skipped
            for i in (13, 21, 22):
                treeviewcolumn=getattr(self, 'treeviewcolumn{}{}'.format(name, i))
                cellrenderer=CellRendererTimeStamp()
                treeviewcolumn.pack_start(cellrenderer, True)
                treeviewcolumn.add_attribute(cellrenderer, 'timestamp', i-1)

            # path
            treeviewcolumn=getattr(self, 'treeviewcolumn{}15'.format(name))
            cellrenderer=CellRendererURI()
            treeviewcolumn.pack_start(cellrenderer, True)
            treeviewcolumn.add_attribute(cellrenderer, 'uri', 14)            


        # for the albums
        
        cellrenderer = CellRendererAlbum()
        self.iconview_RT_albums.pack_start(cellrenderer, True)
        self.iconview_RT_albums.add_attribute(cellrenderer, 'text', 0)

        cellrenderer = CellRendererLongText()
        self.iconview_RT_albums.pack_start(cellrenderer, True)
        self.iconview_RT_albums.add_attribute(cellrenderer, 'text', 1)

        cellrenderer = CellRendererLongText()
        self.iconview_RT_albums.pack_start(cellrenderer, True)
        self.iconview_RT_albums.add_attribute(cellrenderer, 'text', 2)
        

        """
            Initialize general atributes
        """

        # It is pretty important that each thread 
        # run a different database connection
        self.db_main_thread=Database()
        self.db_playlists=Database()
        self.db_tracks_queue=Database()
        self.db_populate_albums=Database()
        self.db_populate_artists_genres=Database()
        self.db_populate_tracks=Database()
        self.db_track_editor=Database()
        
        
        self.populating_state=[False, False, False] # artsts&genres, album, tracks
        self.populating_abort=False
        self._populate_queue=[]
        
        self.cache_albums=[]
        self.cache_tracks=[]
        self.cache_artists=[]
        self.cache_genres=[]
        self.current_track_id=-1

        self.keep_threads_alive=True
        self.update_scale_RT_track_progress=True
        
        self.player=Player()
        self.player.set_volume(self.volumebutton.get_value())


        self._treeview_playlists_double_clicked=False
        self._treeview_tracks_queue_double_clicked=False

        """
            Start the notifications
        """
        Notify.init('Andromeda Music Player')

        """
            Populate the GUI
        """
        if self.checkbutton_start_playing_on_startup.get_active():
            self.APPEND_request_to_queue(True)
        else:
            self.APPEND_request_to_queue(False)
            
        Thread(target=self.POPULATE_playlists).start()
        Thread(target=self.thread_spinner).start()        
        Thread(target=self.thread_player_manager).start()
        Thread(target=self.thread_populator_manager).start()
        self.POPULATE_completions()
    
        # update the tracks count number: All Music X
        self.liststore_general_playlists[0][2]=self.db_main_thread.get_tracks_count()


        """
            Create & start the app (system try) indicator
        """
        self.window_root_is_minimized=False
        self.indicator = appindicator.Indicator.new_with_path(  'andromeda-indicator',
                                                                'images/logo_x32.png',
                                                                appindicator.IndicatorCategory.APPLICATION_STATUS,
                                                                os.path.dirname(os.path.realpath(__file__)))
        
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        
        
        self.indicator.set_menu(self.indicator_menu_button)
        
        
        # This is a hack to make the menu do not display an empty
        # menu. In the future I'd like to add the current playing
        # track, and display it when the mouse is over.
        #
        # I haven't done it because I don't know how to connect the
        # 'mouse over'
        menuitem=Gtk.MenuItem()
        indicator_box=Gtk.Box()
        menuitem.add(indicator_box)
        
        self.indicator_menu_button.add(menuitem)
        self.indicator_menu_button.show_all()
        


        """
            Start the listening socket, and increment the port if necessary
        """
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port=5320
        while True:
            try:
                self.serversocket.bind(('localhost', self.port))
                break
            except:
                self.port+=1

        with open(PATHS.port, mode='wt', encoding='utf-8') as f:
            f.write(str(self.port))
        
        self.serversocket.listen(5) # maximum of 5 connections 
        Thread(target=self.thread_socket_listener).start()


    
        """
            Load the plugins
        """
        for plugin_name in get_plugins_data().keys():
            
            if self.ccp.get_bool_defval(label_to_configuration_name(plugin_name), False):
                try:
                    plugin=__import__(plugin_name)
                    plugin.load_imports()
                
                    setattr(self, plugin_name, plugin.Main(self, True))
                except Exception as e:
                    print(traceback.format_exc())
    
    
        self.window_root.maximize()
        self.window_root.show()


    def thread_socket_listener(self):
        """
            This thread listens a web socket in order to update the stats and TUI.
            
            For the moment it only scans for simple codes of 3 numbers.
        """
        while self.keep_threads_alive:
            connection, address = self.serversocket.accept()
            data=int(connection.recv(3).decode('utf-8'))

            if data == 100:
                self.NEXT_track()
            elif data == 150:
                self.player.play()
                Gdk.threads_enter()
                self.button_RT_play_pause.set_icon_name('gtk-media-pause')
                Gdk.threads_leave()
            
            elif data == 175:
                if self.player.is_playing():
                    self.player.pause()
                    Gdk.threads_enter()
                    self.button_RT_play_pause.set_icon_name('gtk-media-play')
                    Gdk.threads_leave()
                
                elif self.player.is_paused():
                    self.player.play()
                    Gdk.threads_enter()
                    self.button_RT_play_pause.set_icon_name('gtk-media-pause')
                    Gdk.threads_leave()
                
            elif data == 200:
                self.player.pause()
                Gdk.threads_enter()
                self.button_RT_play_pause.set_icon_name('gtk-media-play')
                Gdk.threads_leave()
            elif data == 250:
                self.player.stop()
                Gdk.threads_enter()
                self.button_RT_play_pause.set_icon_name('gtk-media-play')
                Gdk.threads_leave()
                
        self.serversocket.close()


    def thread_player_manager(self):
        """
            This thread scans the diferent states of the player in order
            to update the GUI and request a new track if necessary.
        """

        while self.keep_threads_alive:

            if self.player.is_playing() or self.player.is_paused():
                """ The player just started playing a new song """

                Gdk.threads_enter()
                self.scale_RT_track_progress.set_sensitive(True)
                Gdk.threads_leave()
                
                track_id=self.current_track_id
                track_length=self.player.get_length()
                track_length_str=FORMAT_miliseconds(track_length)
                
                player_is_playing=self.player.is_playing()
                player_is_paused=self.player.is_paused()
                
                while player_is_playing and self.current_track_id == track_id:
                    
                    track_position=self.player.get_position()
                    
                    if track_length == 0:
                        label="{}%".format(round(track_position*100, 1))
                    else:
                        label="{} - {}".format(FORMAT_miliseconds((track_position*track_length)), track_length_str)

                    Gdk.threads_enter()
                    self.label_track_progress.set_text(label)
                    Gdk.threads_leave()
                    
                    if self.update_scale_RT_track_progress:
                        Gdk.threads_enter()
                        self.scale_RT_track_progress.set_value(track_position)
                        Gdk.threads_leave()
                
                    player_is_playing=self.player.is_playing()
                    player_is_paused=self.player.is_paused()
                    
                    sleep(.5)
                    
                    
                # if the track succsessfully ended update the playcount
                if track_position >= 0.98:
                    print(self.db_tracks_queue.increment_track_playcount(track_id)) # This value should be updated in the GTK LISTSTORE 


            elif len(self.cache_tracks) > 0 and self.player.ended_playing():
                """ The player wants a random song """
                self.NEXT_track()
                
            elif self.player.is_stopped():
                """ The player is not playing """
                
                #
                # If the while loop successfully ends (the track ended):
                #
                Gdk.threads_enter()
                self.scale_RT_track_progress.set_sensitive(False)
                Gdk.threads_leave()
                
                Gdk.threads_enter()
                self.window_root.set_title(TEXT_PROGAM_NAME)
                Gdk.threads_leave()
                
                Gdk.threads_enter()
                self.label_album_title.set_text('')
                Gdk.threads_leave()
                
                Gdk.threads_enter()
                self.label_track_title.set_text('')
                Gdk.threads_leave()
                                
                Gdk.threads_enter()
                self.button_RT_play_pause.set_icon_name('gtk-media-play')
                Gdk.threads_leave()
                
                # replace the album image
                for child in self.box_current_album.get_children():
                    Gdk.threads_enter()
                    self.box_current_album.remove(child)
                    Gdk.threads_leave()
                
                image=Gtk.Image()
                image.set_from_file(PATHS.albums_current_default)
                
                Gdk.threads_enter()
                self.box_current_album.add(image)
                Gdk.threads_leave()
                
                Gdk.threads_enter()
                self.box_current_album.show_all()
                Gdk.threads_leave()
                
                Gdk.threads_enter()
                self.scale_RT_track_progress.set_value(0)
                Gdk.threads_leave()

                Gdk.threads_enter()
                self.label_track_progress.set_text("Iddle")
                Gdk.threads_leave()
    
            sleep(.5)

    def thread_spinner(self):
        spinner_state=False
        while self.keep_threads_alive:
            if not spinner_state:
                if True in self.populating_state:
                    Gdk.threads_enter()
                    self.spinner.start()
                    Gdk.threads_leave()
                    spinner_state=True
            else:
                if not True in self.populating_state:
                    Gdk.threads_enter()
                    self.spinner.stop()
                    Gdk.threads_leave()
                    spinner_state=False
                
            sleep(0.5)

    
    def thread_populator_manager(self):
        """
            The idea of this thread is to:
            
                - Improve the database access when searching/filtering data
                - Always populate the GUI with the last request the user has made
        
            
            To request the GUI be re-populated, it is only necessary to add a new item 
            to the populate_queue list.
            
            In this case I think a persistent loop is good to avoid spawning too many threads.
        """
        self._current_request=(None, None) # dumy tuple to initialize
        while self.keep_threads_alive:
            if len(self._populate_queue) > 0 and (self._populate_queue[-1:][0] != self._current_request):
                
                # Take the last item
                self._current_request=self._populate_queue[-1:][0]
                
                # remove items from the queue, the fact of letting the last item could
                # prevent a more recent item from being deleted
                self._populate_queue=[self._populate_queue[-1:][0]]
            
                # If some thread is already populating the queue,
                # stop it, and wait until it dies.
                if True in self.populating_state:
                    
                    self.populating_abort=True
                    
                    while True in self.populating_state:
                        sleep(.05)
                        
                    self.populating_abort=False
                
                # Populate the GUI
                Thread(target=self._POPULATE_artists_and_genres, args=[self._current_request]).start()
                Thread(target=self._POPULATE_albums,             args=[self._current_request]).start()
                Thread(target=self._POPULATE_tracks,             args=[self._current_request]).start()
            
            sleep(.3)
            

    def _POPULATE_artists_and_genres(self, request, force=False):

        self.populating_state[0]=True
        
        # Populate genres
        #
        genres=self.db_populate_artists_genres.get_genres(*request[0:2])
                
        if self.cache_genres != genres or force:
            self.cache_genres=genres
            selected_genre=gtk_get_first_selected_cell_from_selection(self.treeview_selection_genres, 0)
            
            Gdk.threads_enter()
            self.liststore_genres.clear()
            Gdk.threads_leave()
            
            Gdk.threads_enter()
            self.treeview_RT_genres.set_model(None)
            Gdk.threads_leave()
            
            self.liststore_genres.append(["All Genres ({})".format(len(genres))])
            
            for genre in genres:
                if genre[0] is not None:
                    if self.populating_abort:
                        self.populating_state[0]=False
                        return
                        
                    self.liststore_genres.append([genre[0]])
                    
            Gdk.threads_enter()
            self.treeview_RT_genres.set_model(self.liststore_genres)
            Gdk.threads_leave()
            
            gtk_select_row_from_cell(self.treeview_RT_genres, 0, selected_genre)
            
            
            
        # Populate artists
        # 
        artists=self.db_populate_artists_genres.get_artists(*request[0:3])

        if artists != self.cache_artists or force:
            self.cache_artists=artists
            selected_artist_id=gtk_get_first_selected_cell_from_selection(self.treeview_selection_artists, 0)
            
            Gdk.threads_enter()
            self.treeview_RT_artists.set_model(None)
            Gdk.threads_leave()
            
            self.treeview_RT_artists.freeze_child_notify()
            
            self.liststore_artists.clear()
                


            ## Start populating
            #
            self.liststore_artists.append([-1, "All Artists ({})".format(len(artists))])
            
            for id, artist in artists:
                if self.populating_abort:
                    self.populating_state[0]=False
                    return
                
                self.liststore_artists.append([id, str(artist)])
                
                
            Gdk.threads_enter()
            self.treeview_RT_artists.set_model(self.liststore_artists)
            Gdk.threads_leave()

            gtk_select_row_from_cell(self.treeview_RT_artists, 0, selected_artist_id)
        
        self.populating_state[0]=False

    def POPULATE_plugins(self):
        
        for child in self.plugins_box:
            self.plugins_box.remove(child)
        
        
        for plugin_key, plugin in get_plugins_data().items():
            
            main_box=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            main_box.set_margin_top(10)
            main_box.set_margin_bottom(10)
            main_box.set_margin_left(5)
            main_box.set_margin_right(5)
            
            checkbox=Gtk.CheckButton()
            if self.ccp.get_bool_defval(label_to_configuration_name(plugin_key),False):
                checkbox.set_active(True)
            else:
                checkbox.set_active(False)
                
            checkbox.connect('toggled', self.on_checkbox_ST_plugin_clicked, plugin_key)
                
            
            labels_box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            
            label=Gtk.Label()
            label.set_property('xalign', 0.0)
            label.set_markup("<span font_weight='bold' font_size='large' >{}</span>".format(escape(plugin['name'])))
            labels_box.add(label)

            label=Gtk.Label(label=plugin['description'])
            label.set_property('xalign', 0.0)
            labels_box.add(label)            

            label=Gtk.Label()
            label.set_property('xalign', 0.0)
            label.set_margin_top(10)
            label.set_markup("<span font_size='small'>Version: {}</span>".format(escape(plugin['version'])))
            labels_box.add(label)

            if plugin['date'] != '':
                label=Gtk.Label()
                label.set_property('xalign', 0.0)
                label.set_markup("<span font_size='small'>Date: {}</span>".format(plugin['date']))
                labels_box.add(label)

            if plugin['website'] != '':
                label=Gtk.Label()
                label.set_property('xalign', 0.0)
                label.set_markup("<span font_size='small'>Website: {}</span>".format(escape(plugin['website'])))
                labels_box.add(label)

            label=Gtk.Label()
            label.set_property('xalign', 0.0)
            label.set_markup("<span font_size='small'>Mantainer: {}</span>".format(escape(plugin['mantainer'])))
            labels_box.add(label)             
            
            main_box.pack_start(labels_box, True, True, 0)
            main_box.add(checkbox)

            self.plugins_box.add(main_box)

            
        self.plugins_box.show_all()
        


    def POPULATE_completions(self):
        
        for artist_data in self.db_main_thread.get_artists():
            self.liststore_completion_artists.append(artist_data)
            
        for genre in self.db_main_thread.get_genres():
            self.liststore_completion_genres.append(genre)
        
        for _, album_name, _, album_id in self.db_main_thread.get_albums():
            self.liststore_completion_albums.append([album_id, album_name])
        

    def _POPULATE_albums(self, request, force=False):
         
        self.populating_state[1]=True
        
        albums=self.db_populate_albums.get_albums(*request[0:4])

        if albums != self.cache_albums or force:
            self.cache_albums=albums

                        
            # Populate
            #
            print("Populating albums started, {} albums".format(len(albums)))
            start_benchmark=time()
            

            Gdk.threads_enter()
            self.iconview_RT_albums.set_model(None)
            Gdk.threads_leave()
                            
            self.liststore_albums.clear()
            
            # Add the "all albums" cover
            if len(albums) > 1:
                self.liststore_albums.append([  None, "All Albums ({})".format(len(albums)), None, -1])

            
            for artwork_id, album_title, artist_name, album_id in albums:
        
                if self.populating_abort:
                    self.populating_state[1]=False
                    print("Populating albums aborted")
                    return

                self.liststore_albums.append([artwork_id, album_title, artist_name, album_id])                    
                    

            Gdk.threads_enter()
            self.iconview_RT_albums.set_model(self.liststore_albums)
            Gdk.threads_leave()
                    
            # benchmarks printed at the terminal
            #
            delta=time() - start_benchmark
            print("{} albums populated in {} seconds, {}/s".format(len(albums), round(delta, 2), round(len(albums)/delta), 2))
        
        
        self.populating_state[1]=False


    def _POPULATE_tracks(self, request, force=False):
        
        self.populating_state[2]=True
        
        tracks=self.db_populate_tracks.get_tracks(*request[0:5])

        play_track_at_end=request[5]


        if tracks != self.cache_tracks or force:
            
            self.cache_tracks=tracks
            
            if play_track_at_end and self.menuitem_shuffle_off.get_active():
                Thread(target=self.NEXT_track).start()
                play_track_at_end=False

            
            self.UPDATE_track_label_stats(tracks)

            ## It seems to be better to remove all items and selecting the previous item
            selected_track_id=gtk_get_first_selected_cell_from_selection(self.treeview_selection_tracks, column=0)
    
            # Populate the liststore 
            #
            print("Populating tracks started, {} tracks".format(len(tracks)))
            start_benchmark=time()
                        
            Gdk.threads_enter()
            self.treeview_RT_tracks.set_sensitive(False)
            Gdk.threads_leave()
            Gdk.threads_enter()
            self.treeview_RT_tracks.set_model(None)
            Gdk.threads_leave()
            Gdk.threads_enter()
            self.treeview_RT_tracks.freeze_child_notify()
            Gdk.threads_leave()
        
            sorted_column, sorted_type = self.liststore_tracks.get_sort_column_id()
        
            self.liststore_tracks.clear()
            self.liststore_tracks.set_default_sort_func(lambda *unused: 0)
            self.liststore_tracks.set_sort_column_id(-1, Gtk.SortType.ASCENDING)
            

            for track in tracks:
                if self.populating_abort:
                    self.populating_state[2]=False
                    print("Populating tracks aborted")
                    return
                    

                self.liststore_tracks.append(track)


            if sorted_column is not None:
                self.liststore_tracks.set_sort_column_id(sorted_column, sorted_type)
    
            Gdk.threads_enter()
            self.treeview_RT_tracks.set_model(self.liststore_tracks)
            Gdk.threads_leave()
            
            Gdk.threads_enter()
            self.treeview_RT_tracks.thaw_child_notify()
            Gdk.threads_leave()
            
            Gdk.threads_enter()
            self.treeview_RT_tracks.set_sensitive(True)
            Gdk.threads_leave()
            

            
            # benchmarks printed at the terminal
            #
            delta=time() - start_benchmark
            print("{} tracks populated in {} seconds, {}/s".format(len(tracks), round(delta, 2), round(len(tracks)/delta), 2))

            # select the item that was previously selected (if possible)
            #
            if selected_track_id is not None:
                treeiter = gtk_get_iter_from_liststore_cell(self.liststore_tracks, selected_track_id)
                if treeiter is not None:
                    Gdk.threads_enter()
                    self.treeview_selection_tracks.select_iter(treeiter)
                    Gdk.threads_leave()
                    

        if play_track_at_end:
            Thread(target=self.NEXT_track).start()
        
        self.populating_state[2]=False


    def POPULATE_playlists(self):
        
        Gdk.threads_enter()
        self.liststore_playlists.clear()
        Gdk.threads_leave()
        
        for id, name in self.db_playlists.get_playlists():
            
            image=Gtk.Image()
            image.set_from_file(PATHS.playlist)
            pixbuf = image.get_pixbuf()
            
            Gdk.threads_enter()
            self.liststore_playlists.append([   id, 
                                                False, 
                                                name, 
                                                self.db_playlists.get_playlist_tracks_count(id),
                                                pixbuf])
            Gdk.threads_leave()


    def APPEND_tracks_to_queue(self, track_ids, thread=False):
        
        for track_data in self.db_main_thread.get_tracks_from_ids(track_ids):
            if thread:
                Gdk.threads_enter()
                self.liststore_tracks_queue.append(track_data)
                Gdk.threads_leave()
            else:
                self.liststore_tracks_queue.append(track_data)
                
        if thread:
            Gdk.threads_enter()
            self.liststore_general_playlists[1][2] = len(self.liststore_tracks_queue)
            Gdk.threads_leave()
        else:
            self.liststore_general_playlists[1][2] = len(self.liststore_tracks_queue)

    def DELETE_tracks_from_queue(self, track_ids, thread=False):
        
        if len(self.liststore_tracks_queue) == len(track_ids):
            if thread:
                Gdk.threads_enter()
                self.liststore_tracks_queue.clear()
                Gdk.threads_enter()
                Gdk.threads_enter()
                self.liststore_general_playlists[1][2] = 0
                Gdk.threads_leave()
            else:
                self.liststore_tracks_queue.clear()
                self.liststore_general_playlists[1][2] = 0
        else:
            for track_id in track_ids:
                if thread:
                    Gdk.threads_enter()
                    self.liststore_tracks_queue.remove(gtk_get_iter_from_liststore_cell(self.liststore_tracks_queue, track_id))
                    Gdk.threads_leave()
                else:
                    self.liststore_tracks_queue.remove(gtk_get_iter_from_liststore_cell(self.liststore_tracks_queue, track_id))
                    
            if thread:
                Gdk.threads_enter()
                self.liststore_general_playlists[1][2] = len(self.liststore_tracks_queue)
                Gdk.threads_leave()
            else:
                self.liststore_general_playlists[1][2] = len(self.liststore_tracks_queue)



    def APPEND_request_to_queue(self, play_track=False):
        """
            Read the Genre, Artist, Album, and filter selection from the GUI,
            and append a population request.
        """
        
        filter=self.searchentry.get_text()
        if filter=='':
            filter=None

        # Get the selected genres
        #
        selected_genres=gtk_get_selected_cells_from_selection(self.treeview_selection_genres)

        if selected_genres == []:
            selected_genres=None
        
        elif selected_genres is not None:
            for genre in selected_genres:
                if fnmatch(genre, 'All Genres (*)'):
                    selected_genres=None
                    break

        # Get the selected artsts ids
        #
        selected_artist_ids=gtk_get_selected_cells_from_selection(self.treeview_selection_artists)
        if selected_artist_ids == [] or -1 in selected_artist_ids:
            selected_artist_ids=None


        # Get the selected albums ids
        #
        selected_album_ids=gtk_get_selected_cells_from_iconview_selection(self.iconview_RT_albums, 3)
        
        if selected_album_ids == [] or -1 in selected_album_ids:
            selected_album_ids=None
        
        
        # Get the selected playlist id
        #
        if self.treeview_selection_playlists.count_selected_rows() == 1:
            playlist_id = gtk_get_first_selected_cell_from_selection(self.treeview_selection_playlists)
        else:
            playlist_id = None
        
        # Append the query
        #
        self._populate_queue.append((filter, playlist_id, selected_genres, selected_artist_ids, selected_album_ids, play_track))
    
    def PLAY_track(self, track_id, safe_thread=False):

        # Get the track data
        #

        track=self.db_main_thread.get_tracks_from_ids([track_id])
        if track == []:
            return
        else:
            track=list(track[0])
        
        for i in [2, 3, 4, 14, 17]:
            if track[i] is None:
                track[i]=''
        
        track_id=track[0]
        title=track[2]
        album=track[3]
        artist_name=track[4]
        path=track[14]
        album_id=track[17]
        

        artwork_id=self.db_main_thread.get_artwork_id_from_album_id(album_id)

        path=FORMAT_uri(path)
        
        if safe_thread:
            for child in self.box_current_album.get_children():
                Gdk.threads_enter()
                self.box_current_album.remove(child)
                Gdk.threads_leave()
        else:
            for child in self.box_current_album.get_children():
                self.box_current_album.remove(child)           
        
        
        if os.path.exists(path):
            """
                Play the song and update the GUI, database etc
            """
            
            self.current_track_id=track_id
            self.player.play(path)
            
            album_label="<span size='small' font_weight='light'>By</span> {} <span size='small' font_weight='light'>from</span> {}".format(escape(artist_name), escape(album))

            # Make the album image
            #
            if os.path.exists(PATHS.albums_current.format(artwork_id)):
                image_path=PATHS.albums_current.format(artwork_id)
            else:
                image_path=PATHS.albums_current_default

            image=Gtk.Image()
            image.set_from_file(image_path)
            image.set_property('yalign', 0.5)

            
            if safe_thread:


                # select the current track
                #
                #if self.populating_state[2]==False: # and not self.menu_tracks.get_property('visible'):
                    #print('called')
                    #gtk_select_row_from_cell(self.GET_visible_treeview(), 0, self.current_track_id)
                
                # update the GUI
                #
                Gdk.threads_enter()
                self.label_track_title.set_text(title)
                Gdk.threads_leave()
                Gdk.threads_enter()
                self.label_album_title.set_markup(album_label)
                Gdk.threads_leave()
                Gdk.threads_enter()
                self.button_RT_play_pause.set_icon_name('gtk-media-pause')
                Gdk.threads_leave()
                Gdk.threads_enter()
                self.window_root.set_title("{} - {}".format(title, TEXT_PROGAM_NAME))
                Gdk.threads_leave()
                Gdk.threads_enter()
                self.box_current_album.add(image)
                Gdk.threads_leave()
                Gdk.threads_enter()
                self.box_current_album.show_all()
                Gdk.threads_leave()
                
                
                # Add the track to the historial
                #
                Gdk.threads_enter()
                self.liststore_general_playlists[2][2]=self.liststore_general_playlists[2][2]+1
                Gdk.threads_leave()
                
                Gdk.threads_enter()
                self.liststore_tracks_historial.append(track)
                Gdk.threads_leave()
            else:
                # select the current track if the listore is not populating
                #
                #if self.populating_state[2]==False: # and not self.menu_tracks.get_property('visible'):
                    #print('called2')
                    #gtk_select_row_from_cell(self.GET_visible_treeview(), 0, self.current_track_id)

                # update the GUI
                #
                self.label_track_title.set_text(title)
                self.label_album_title.set_markup(album_label)
                self.button_RT_play_pause.set_icon_name('gtk-media-pause')
                self.window_root.set_title("{} - {}".format(title, TEXT_PROGAM_NAME))
                self.box_current_album.add(image)
                self.box_current_album.show_all()
                
                # add the track to the historial
                #
                self.liststore_general_playlists[2][2]=self.liststore_general_playlists[2][2]+1
                self.liststore_tracks_historial.append(track)
                
                
            """
                Display the notification.
                
                Does it needs to be protected by Gdk.threads?
            """
            if self.checkbutton_display_notifications.get_active() and \
                not self.window_root.get_property('visible') or self.window_root_is_minimized:
                
                try:
                    self._current_notification.close()
                except:
                    pass
                
                self._current_notification = Notify.Notification.new(escape(title), album_label)
                self._current_notification.set_timeout(3000)
                self._current_notification.set_icon_from_pixbuf(Pixbuf.new_from_file(image_path))
                self._current_notification.add_action('next', 'Next', self.on_notification_next_button_clicked)
                self._current_notification.show()
            
        else:
            """
                If the path to the song does not exists
            """
            self.player.pause()
            
            if safe_thread:
                
                Gdk.threads_enter()
                self.button_RT_play_pause.set_icon_name('gtk-media-play')
                Gdk.threads_leave()
                
                Gdk.threads_enter()
                self.label_album_title.set_text('')
                Gdk.threads_leave()
                
                Gdk.threads_enter()
                self.label_track_title.set_text('')
                Gdk.threads_leave()
                
                Gdk.threads_enter()
                self.label_track_progress.set_text('')
                Gdk.threads_leave()
                
                Gdk.threads_enter()
                self.window_root.set_title(TEXT_PROGAM_NAME)
                Gdk.threads_leave()                
            else:
                self.button_RT_play_pause.set_icon_name('gtk-media-play')
                self.label_album_title.set_text('')
                self.label_track_title.set_text('')
                self.label_track_progress.set_text('')
                self.window_root.set_title(TEXT_PROGAM_NAME)
    
    def NEXT_track(self):

        track_id=None
        tracks_cache_len=len(self.cache_tracks)
        
        # play songs from the queue
        #
        if len(self.liststore_tracks_queue) > 0:
            track_id=self.liststore_tracks_queue[0][0]
            Gdk.threads_enter()
            self.liststore_tracks_queue.remove(self.liststore_tracks_queue.get_iter_first())
            Gdk.threads_leave()
            Gdk.threads_enter()
            self.liststore_general_playlists[1][2] = len(self.liststore_tracks_queue)
            Gdk.threads_leave()
            
    
        # Play random tracks
        #
        elif tracks_cache_len > 0:
            
            
            if self.menuitem_shuffle_by_track.get_active():
            
            
                dont_repeat=self.radiomenuitem_repeat_off.get_active()
                skipped=0
                while True:
                    track=choice(self.cache_tracks)
    
                    track_id=track[0]
                    title=track[2]
                    album=track[3]
                    artist_name=track[4]
                    path=track[14]
                    album_id=track[17]
                    
                    if dont_repeat:
                        if not gtk_liststore_has_value(self.liststore_tracks_historial, track_id):
                            break
                        else:
                            skipped += 1
                            
                            # If all the songs have been played stop the player
                            if skipped == tracks_cache_len:
                                self.player.stop()
                                Gdk.threads_enter()
                                self.button_RT_play_pause.set_icon_name('gtk-media-play')
                                Gdk.threads_leave()
                                return
                                
                    elif self.radiomenuitem_repeat_all.get_active():
                        break
                        
    
            elif self.menuitem_shuffle_off.get_active():
                
                if len(self.liststore_tracks) == 0:
                    self.player.stop()
                    Gdk.threads_enter()
                    self.button_RT_play_pause.set_icon_name('gtk-media-play')
                    Gdk.threads_leave()
                    return
                    
                elif len(self.liststore_tracks) == 1:
                    track_id = self.liststore_tracks[0][0]
                    
                    if self.radiomenuitem_repeat_off.get_active():
                        if gtk_liststore_has_value(self.liststore_tracks_historial, track_id):
                            self.player.stop()
                            Gdk.threads_enter()
                            self.button_RT_play_pause.set_icon_name('gtk-media-play')
                            Gdk.threads_leave()
                            return
                else:
                    current_iter = gtk_get_iter_from_liststore_cell(self.liststore_tracks, self.current_track_id)  
                    
                    if current_iter is None:
                        current_iter = self.liststore_tracks.get_iter_first()
                                    
                    next_iter=self.liststore_tracks.iter_next(current_iter)
                    
                    if next_iter is not None:
                        track_id=self.liststore_tracks.get_value(next_iter, 0)
        
        if track_id is not None:
            self.PLAY_track(track_id, True)

    def GET_visible_treeview(self):
        """
            Since the GUI works with many liststores, the idea of this method
            is to return the treeview_selection that is currently seen by the user.
        """
        
        model, treepaths = self.treeview_selection_general_playlists.get_selected_rows()
       
        selection=-2
        for treepath in treepaths:
            selection=int(str(treepath))
            break
            
        if selection <= 0:  # playlist & all music
            return self.treeview_RT_tracks
            
        elif selection == 1: # queue
            return self.treeview_RT_tracks_queue
            
        elif selection == 2: # historial
            return self.treeview_RT_tracks_historial


    def TRACK_Editor_update_dialog(self):

        if len(self._tracks_to_edit)==1:
            self.button_TE_back.set_sensitive(False)
            self.button_TE_foward.set_sensitive(False)
            self.button_TE_foward2.set_sensitive(False)
        
        elif self._track_editor_current_position == 0:
            self.button_TE_back.set_sensitive(False)
            self.button_TE_foward.set_sensitive(True)
            self.button_TE_foward2.set_sensitive(True)
            
        elif self._track_editor_current_position == 1:
            self.button_TE_back.set_sensitive(True)
            
        elif self._track_editor_current_position == len(self._tracks_to_edit)-2:
            self.button_TE_foward.set_sensitive(True)
            self.button_TE_foward2.set_sensitive(True)
            
        elif self._track_editor_current_position == len(self._tracks_to_edit)-1:
            self.button_TE_back.set_sensitive(True)
            self.button_TE_foward.set_sensitive(False)
            self.button_TE_foward2.set_sensitive(False)

        try:
            previous_track_data=self._tracks_to_edit[self._track_editor_current_position-1]
        except:
            previous_track_data=False
            
        track_data=self._tracks_to_edit[self._track_editor_current_position]
        
        # Set the album image
        #
        for child in self.eventbox_TE_album.get_children():
            self.eventbox_TE_album.remove(child)

        artwork_id=self.db_main_thread.get_artwork_id_from_album_id(track_data[17])

        if os.path.exists(PATHS.albums_artwork.format(artwork_id)):
            image_path=PATHS.albums_artwork.format(artwork_id)
        else:
            image_path=PATHS.albums_artwork_default

        image=Gtk.Image()
        image.set_from_file(image_path)

        self.eventbox_TE_album.add(image)
        self.eventbox_TE_album.show_all()


        # Add the track data
        #

        for item, position in TE_STRING_TO_STRING:
            object=getattr(self, item)
            # The try exception is for when the field = None
            if object.get_sensitive() or not previous_track_data:
                data=track_data[position]
            else:
                data=previous_track_data[position]
                
            try:
                object.set_text(data)
            except:
                object.set_text("")

        for item, position in TE_INT_TO_INT:
            object=getattr(self, item)

            if object.get_sensitive() or not previous_track_data:
                data=track_data[position]
            else:
                data=previous_track_data[position]

            object.set_value(data)


        # Update the track label
        #
        self.label_TE_current_track.set_text("{}/{}".format(self._track_editor_current_position+1, len(self._tracks_to_edit)))
        

    def TRACK_EDITOR_update_cache(self):

        track_data=list(self._tracks_to_edit[self._track_editor_current_position])
        
        for item, position in TE_STRING_TO_STRING:
            value=getattr(self, item).get_text()
            if value == '':
                value=None
                
            track_data[position]=value
  
  
        for item, position in TE_INT_TO_INT:
            track_data[position]=getattr(self, item).get_value()
        
        self._tracks_to_edit[self._track_editor_current_position]=track_data
        
        
    def UPDATE_track_liststores(self, tracks_ids_OR_data):

        # Conver the tracks_ids_OR_data in tracks_data if they were id's
        if len(tracks_ids_OR_data[0]) == 1:
            tracks_ids_OR_data=self.db_main_thread.get_tracks_from_ids(tracks_ids_OR_data)


        tracks_dictionary=dict((track_data[0], track_data) for track_data in tracks_ids_OR_data)

        tracks_ids_OR_data=None # this is to free the memory

        ids_to_update=tracks_dictionary.keys()


        # Update all the liststores data.
        #            
        for liststore in (self.liststore_tracks, self.liststore_tracks_queue, self.liststore_tracks_historial):
            for i, row in enumerate(liststore):
                if row[0] in ids_to_update:
                    Gdk.threads_enter()
                    liststore[i]=tracks_dictionary[row[0]]
                    Gdk.threads_leave()
                    
        
    def UPDATE_track_label_stats(self, tracks=None):
 
        if tracks is None:
            tracks=self.GET_visible_treeview().get_model()
        
        if tracks is None or len(tracks) <= 0:
            label_string=""
            
        elif len(tracks) == 1:
            tracks_size=FORMAT_bytes(tracks[0][15])
            play_time_str=str(timedelta(seconds=(tracks[0][19]//1000))).rsplit(':',1)[0]
            label_string="{:,} Song ~ {} ~ {}".format(len(tracks), play_time_str, tracks_size)
        else:
            tracks_size=FORMAT_bytes(sum(row[15] for row in tracks))
            play_time_seconds=sum(row[19] for row in tracks)//1000
            play_time_str=str(timedelta(seconds=play_time_seconds)).rsplit(':',1)[0]
            label_string="{:,} Songs ~ {} ~ {}".format(len(tracks), play_time_str, tracks_size)
        
        Gdk.threads_enter()
        self.label_songs_stats.set_text(label_string)
        Gdk.threads_leave()            

        

    def on_button_RT_play_pause_clicked(self, widget, data=None):
        if self.player.is_playing():
            self.player.pause()
            self.button_RT_play_pause.set_icon_name('gtk-media-play')
        
        elif self.player.is_paused():
            self.player.play()
            self.button_RT_play_pause.set_icon_name('gtk-media-pause')
        else:
            Thread(target=self.NEXT_track).start()

    def on_volumebutton_RT_value_changed(self, widget, value):
        self.player.set_volume(value)

    def on_menuitem_tracks_clicked(self, checkmenuitem, id):

        config_name=label_to_configuration_name('treeview_'+checkmenuitem.get_label())
        treeviewcolumn = getattr(self, 'treeviewcolumn'+str(id))
        treeviewcolumn_q = getattr(self, 'treeviewcolumn_q'+str(id))
        treeviewcolumn_h = getattr(self, 'treeviewcolumn_h'+str(id))
        
        if checkmenuitem.get_active():
            treeviewcolumn.set_visible(True)
            treeviewcolumn_q.set_visible(True)
            treeviewcolumn_h.set_visible(True)
            self.ccp.write(config_name, True)
        else:
            treeviewcolumn.set_visible(False)
            treeviewcolumn_q.set_visible(False)
            treeviewcolumn_h.set_visible(False)
            self.ccp.write(config_name, False)

    def on_menuitem_edit_tracks_activate(self, checkmenuitem, data=None):
        
        if self._current_edit_treeview == 'genres':
            selected_genres=gtk_get_selected_cells_from_selection(self.treeview_selection_genres)
    
            for genre in selected_genres:
                if fnmatch(genre, 'All Genres (*)'):
                    selected_genres=None
                    break
            
            self._tracks_to_edit=self.db_main_thread.get_tracks(genres=selected_genres)

        elif self._current_edit_treeview == 'artists':
            selected_artists_ids=gtk_get_selected_cells_from_selection(self.treeview_selection_artists)
            
            if selected_artists_ids == [] or -1 in selected_artists_ids:
                selected_artists_ids=None
            
            self._tracks_to_edit=self.db_main_thread.get_tracks(artists_ids=selected_artists_ids)
        
        elif self._current_edit_treeview == 'albums':
            selected_album_ids=gtk_get_selected_cells_from_iconview_selection(self.iconview_RT_albums, 3)
            
            if selected_album_ids == [] or -1 in selected_album_ids:
                selected_album_ids=None
            
            
            self._tracks_to_edit=self.db_main_thread.get_tracks(albums_ids=selected_album_ids)

        elif self._current_edit_treeview in ('tracks', 'queue', 'historial'):
            self._tracks_to_edit=self.db_main_thread.get_tracks_from_ids(
                                        gtk_get_selected_cells_from_selection(
                                            self.GET_visible_treeview().get_selection()
                                        )
                                    )
        else:
            print("Error: Wrong choice when selecting tracks to edit")


                                    
        self._track_editor_current_position=0
        
        for togglebutton, _ in TE_checkbuttons_items:
            getattr(self, togglebutton).set_active(False)

        self.TRACK_Editor_update_dialog()
        self.dialog_track_editor.show_all()
        
    def on_treeview_RT_tracks_x_row_activated(self, treeview, path, data=None):
        track_id=treeview.get_model()[path][0]
        if track_id is not None:
            self.PLAY_track(track_id)

    def on_button_RT_suffle_queue_clicked(self, button, data=None):
        if len(self.liststore_tracks_queue) > 1:
            gtk_shuffle_treeview(self.treeview_RT_tracks_queue)
   
        
    def on_scale_RT_track_progress_button_press_event(self, widget, data=None):
        self.update_scale_RT_track_progress=False
        
    def on_scale_RT_track_progress_button_release_event(self, widget, data=None):
        value=widget.get_value()
        self.player.set_position(value)
        self.update_scale_RT_track_progress=True        


    def on_treeview_RT_general_playlists_button_release_event(self, treeview, event, data=None):
        
        if event.button == 1:
            self.treeview_selection_playlists.unselect_all()

            # Display the right box
            #
            model, treepaths = treeview.get_selection().get_selected_rows()
            
            rows=(self.box_playing, self.box_queue, self.box_historial)
            
            treepath=0
            for treepath in treepaths:
                treepath=int(str(treepath))
                break

            playing_boxes=(
                (self.box_playing, self.searchentry),
                (self.box_top_queue_tools, self.box_queue),
                (self.box_historial_tools, self.box_historial)
            )

            for i, (item1, item2) in enumerate(playing_boxes):
                if i != treepath:
                    item1.hide()
                    item2.hide()
                else:
                    item1.show()
                    item2.show()

            if treepaths != []:
                self.APPEND_request_to_queue()
            
            Thread(target=self.UPDATE_track_label_stats).start()

    def on_treeview_RT_playlists_button_press_event(self, treeview, event, data=None):
        
        if event.button == 1 and event.type == Gdk.EventType._2BUTTON_PRESS:
            self._treeview_playlists_double_clicked=True
        else:
            self._treeview_playlists_double_clicked=False
        
            if event.button == 3: # right click
                try:
                    self._playlists_pointing_treepath=treeview.get_path_at_pos(event.x, event.y)[0]
                except:
                    self._playlists_pointing_treepath=None
                    
                self.menu_on_playlist.popup(None, None, None, None, event.button, event.time)
                
                return True


    def on_treeview_RT_playlists_button_release_event(self, treeview, event, data=None):
        if event.button == 1: # left click
            
            # Update the GUI
            #
            self.treeview_selection_general_playlists.unselect_all()
            
            self.box_queue.hide()
            self.box_historial.hide()
            self.box_playing.show()
            
            model, treepaths = treeview.get_selection().get_selected_rows()
            
            if treepaths != []:
                if self._treeview_playlists_double_clicked:
                    self.APPEND_request_to_queue(True)
                else:
                    self.APPEND_request_to_queue()
                

    def on_scale_RT_track_progress_change_value(self, widget, data, value):
        if not self.update_scale_RT_track_progress:
            
            track_length=self.player.get_length()
            track_length_str=FORMAT_miliseconds(track_length)

            if track_length == 0:
                label="{}%".format(round(value*100, 1))
            else:
                label="{} - {}".format(FORMAT_miliseconds((value*track_length)), track_length_str)

            self.label_track_progress.set_text(label)
            
    def on_toolbutton_RT_next_clicked(self, button, data=None):
        print(self.db_main_thread.increment_track_skipcount(self.current_track_id))  ### THE GUI SHOULD BE UPDATED ? ----------------------
        Thread(target=self.NEXT_track).start()

    def on_searchentry_RT_changed(self, searchentry, data=None):
        #self.APPEND_request_to_queue()
        Thread(target=self.thread_user_search, args=[searchentry]).start()

    def thread_user_search(self, searchentry):
        """ This thread is to send an APPEND_request_to_queue only when the user has finished of writing """
        current_val=searchentry.get_text()
        sleep(.3)
        if current_val == searchentry.get_text():
            self.APPEND_request_to_queue()

    def on_treeview_RT_genres_button_press_event(self, treeview, event, data=None):
            
        if event.button == 3: # right click

            gtk_treeview_selection_is_okay(treeview, event)

            self._current_edit_treeview='genres'
            self.menu_tracks.popup(None, None, None, None, event.button, event.time)
            return True

        else:
            if event.button == 1 and event.type == Gdk.EventType._2BUTTON_PRESS:
                self._treeview_RT_genres_double_clicked=True
            else:
                self._treeview_RT_genres_double_clicked=False

            

    def on_treeview_RT_genres_button_release_event(self, widget, event, data=None):
        if event.button == 1:
            if self._treeview_RT_genres_double_clicked:
                self.APPEND_request_to_queue(True)
                self._treeview_RT_genres_double_clicked=False
            else:
                self.APPEND_request_to_queue()


    def on_treeview_RT_artists_button_press_event(self, treeview, event, data=None):

        if event.button == 3: # right click

            gtk_treeview_selection_is_okay(treeview, event)

            self._current_edit_treeview='artists'
            self.menu_tracks.popup(None, None, None, None, event.button, event.time)

            return True

        else:
            if event.button == 1 and event.type == Gdk.EventType._2BUTTON_PRESS:
                self._treeview_RT_artists_double_clicked=True
            else:
                self._treeview_RT_artists_double_clicked=False
                

    def on_treeview_RT_artists_button_release_event(self, widget, event, data=None):
        if event.button == 1:
            if self._treeview_RT_artists_double_clicked:
                self.APPEND_request_to_queue(True)
            else:
                self.APPEND_request_to_queue()

    def on_iconview_RT_albums_button_press_event(self, widget, event, data=None):
        
        if event.button == 1 and event.type == Gdk.EventType._2BUTTON_PRESS:
            self._treeview_albums_double_clicked=True
        else:
            self._treeview_albums_double_clicked=False
            
        if event.button == 3:
            self._current_edit_treeview='albums'
            self.menu_tracks.popup(None, None, None, None, event.button, event.time)

            return True
            
            

    def on_iconview_RT_albums_button_release_event(self, widget, event, data=None):
        if event.button == 1:
            if self._treeview_albums_double_clicked:
                self.APPEND_request_to_queue(True)
            else:
                self.APPEND_request_to_queue()
                
    
    def on_menuitem_repeat_changed(self, widget, data=None):
        if widget.get_active():
            self.menuitem_repeat.set_label(widget.get_label())
    
    def on_menuitem_shuffle_changed(self, widget, data=None):
        if widget.get_active():
            
            if 'Off' in widget.get_label():
                self.toolbutton_RT_next.set_icon_name('media-skip-forward')
                self.ccp.write('shuffle','off')
            else:
                self.toolbutton_RT_next.set_icon_name('media-playlist-shuffle')
                self.ccp.write('shuffle','tracks')

    def on_menuitem_delete_playlist_activate(self, widget, data=None):
        if self._playlists_pointing_treepath is not None:
            
            pointing_iter=self.liststore_playlists.get_iter(self._playlists_pointing_treepath)

            playlist_id=self.liststore_playlists.get_value(pointing_iter, 0)

            self.db_main_thread.delete_playlist(playlist_id)
            Thread(target=self.POPULATE_playlists).start()
    
    def on_indicator_menu_button_button_press_event(self, widget, event):         
        if event.button == 3: # right click
            self.indicator_menu.popup(None, None, None, None, event.button, event.time)
            return True

        elif event.button == 1: # left click
            
            if self.window_root.get_property('visible') and not self.window_root_is_minimized:
                self.window_root.hide()
            else:
                self.window_root.show()
                self.window_root.present()
                
                
        self.indicator_menu_button.popdown()
        return True
        
    def on_window_root_window_state_event(self, window, event):
        if event.changed_mask & Gdk.WindowState.ICONIFIED:
            if event.new_window_state & Gdk.WindowState.ICONIFIED:
                self.window_root_is_minimized=True
            else:
                self.window_root_is_minimized=False

    def on_checkbox_ST_plugin_clicked(self, checkbox, plugin_name):
        self.ccp.write(label_to_configuration_name(plugin_name), checkbox.get_active())
        
        if checkbox.get_active():
            try:
                plugin=__import__(plugin_name)
                plugin.load_imports()
                setattr(self, plugin_name, plugin.Main(self, False))
            except Exception as e:
                print(traceback.format_exc())
                
        else:
            try:
                getattr(self, plugin_name).deactivate_plugin()
            except Exception as e:
                print(traceback.format_exc())
        

    def on_treeview_RT_tracks_header_button_press_event(self, widget, event):
        if event.button == 3: # right click
            self.menu_tracks_header.popup(None, None, None, None, event.button, event.time)
            return True

    def on_treeview_RT_tracks_button_press_event(self, treeview, event, data=None):

        if event.button == 3: # right click

            gtk_treeview_selection_is_okay(treeview, event)

            self._current_edit_treeview='tracks'
            self.menu_tracks.popup(None, None, None, None, event.button, event.time)

            return True
    
    def on_treeview_RT_tracks_queue_button_press_event(self, treeview, event, data=None):
    
        if event.button == 3: # right click
            
            gtk_treeview_selection_is_okay(treeview, event)

            self._current_edit_treeview='queue'
            self.menu_tracks_queue.popup(None, None, None, None, event.button, event.time)

            return True
            
        else:
            if event.button == 1 and event.type == Gdk.EventType._2BUTTON_PRESS:
                self._treeview_tracks_queue_double_clicked=True
            else:
                self._treeview_tracks_queue_double_clicked=False            
                

    def on_treeview_RT_tracks_queue_button_release_event(self, treeview, event, data=None):
        
        if event.button == 1 and self._treeview_tracks_queue_double_clicked:
            
            try:
                pointing_treepath=treeview.get_path_at_pos(event.x, event.y)[0]
            except:
                return
            
            liststore=treeview.get_model()
            
            track_id=liststore[pointing_treepath][0]
            
            if track_id is not None:
                liststore.remove(liststore.get_iter(pointing_treepath))
                self.PLAY_track(track_id)


    def on_menuitem_add_to_queue_activate(self, menuitem, data=None):
        self.APPEND_tracks_to_queue(
            gtk_get_selected_cells_from_selection(
                self.GET_visible_treeview().get_selection()
            )
        )

    def on_menuitem_delete_tracks_from_queue(self, menuitem, data=None):
        self.DELETE_tracks_from_queue(
            gtk_get_selected_cells_from_selection(
                self.treeview_selection_queue
            )
        )
        
    def on_button_RT_settings_clicked(self, button, data=None):
        self.POPULATE_plugins()
        self.dialog_settings.show()

    def on_button_TE_close_settings_clicked(self, button, data=None):
        self.dialog_settings.hide()

    def on_button_about_RT_clicked(self, button, data=None):
        self.dialog_about.run()
        self.dialog_about.hide()

    def on_expander_RT_more_activate(self, widget, data=None):
        if widget.get_expanded():
            widget.set_label("More")
            self.ccp.write('expander_more',False)
        else:
            widget.set_label("")
            self.ccp.write('expander_more',True)
                
    def on_button_TE_back_clicked(self, button, data=None):
        self.TRACK_EDITOR_update_cache()
        self._track_editor_current_position -= 1
        self.TRACK_Editor_update_dialog()
        
    def on_button_TE_foward_clicked(self, button, data=None):
        self.TRACK_EDITOR_update_cache()
        self._track_editor_current_position += 1
        self.TRACK_Editor_update_dialog()

    def on_button_TE_save_clicked(self, button, data=None):
        Thread(target=self.thread_save_track_editor).start()

    def on_button_TE_ALL_X_clicked(self, button, column):
        
        self.TRACK_EDITOR_update_cache()
        value=self._tracks_to_edit[self._track_editor_current_position][column]
        
        for i, row in enumerate(self._tracks_to_edit):
            if isinstance(row, tuple):
                self._tracks_to_edit[i]=list(row)
            
            self._tracks_to_edit[i][column]=value
    
    def on_X_clear_queue_clicked(self, widget=None, data=None):
        self.liststore_tracks_queue.clear()
        
    def on_X_clear_historial_clicked(self, widget=None, data=None):
        self.liststore_tracks_historial.clear()

    def on_togglebutton_TE_clicked(self, togglebutton, entry):
        
        image=Gtk.Image()
        
        if togglebutton.get_active():
            image.set_from_icon_name( 'emblem-readonly', Gtk.IconSize.BUTTON)
            entry.set_sensitive(False)
        else:
            image.set_from_icon_name('gtk-edit', Gtk.IconSize.BUTTON)
            entry.set_sensitive(True)
    
        togglebutton.set_property('image', image)
        
    def thread_save_track_editor(self):
        
        self.TRACK_EDITOR_update_cache()
        
        # spinner ?
        
        Gdk.threads_enter()
        self.menuitem_edit_tracks.set_sensitive(False)
        Gdk.threads_leave()
        
        Gdk.threads_enter()
        self.dialog_track_editor.hide()
        Gdk.threads_leave()
        
        self.db_track_editor.update_full_tracks(self._tracks_to_edit)
        self.UPDATE_track_liststores(self._tracks_to_edit)
        self._tracks_to_edit=[]
        
        Gdk.threads_enter()
        self.menuitem_edit_tracks.set_sensitive(True)
        Gdk.threads_leave()
        
        self._POPULATE_artists_and_genres(self._current_request, True)
        self._POPULATE_albums(self._current_request, True)

    def on_toggle_button_toggled(self, button, data=None):
        self.ccp.write(label_to_configuration_name(button.get_label()), button.get_active())

    def on_button_TE_close_clicked(self, button, data=None):
        self.dialog_track_editor.hide()
        
    def on_notification_next_button_clicked(self, notification, data=None):
        Thread(target=self.NEXT_track()).start()

    def on_root_window_close(self, widget=None, data=None):
        if self.checkbutton_on_close_system_try.get_active():
            self.window_root.unrealize()
            self.window_root.hide()
        else:
            self.exit()

    def on_cellrenderer_rating_changed(self, liststore, treepath, rating):
        track_id=liststore[treepath][0]
        self.db_main_thread.update_track_rating(track_id, rating)

    def exit(self, widget=None, data=None):
        """ Kill the program and exit all the threads """
        
        self.keep_threads_alive=False
        
        # This will send some bytes to the socket listener
        # so the loops ends.
        clientsocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientsocket.connect(('localhost', self.port))
        clientsocket.send(b'1')
        clientsocket.close()
        
        self.player.stop()
        self.db_main_thread.close()
        self.db_playlists.close()
        self.db_tracks_queue.close()
        self.db_populate_albums.close()
        self.db_populate_artists_genres.close()
        self.db_populate_tracks.close()
        self.db_track_editor.close()
        Gtk.main_quit()
        


if __name__ == '__main__':
    
    GObject.threads_init()
    Gdk.threads_init()
    main=GUI()
    Gtk.main()
