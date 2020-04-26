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
    Exemple of how to code a pluggin for the Andromeda Music Player.
"""


"""
    These are the general properties that your plugin should 
    always contain. They will be displayed at the Plugins Dialog.
"""
__title__="Random Playlist"
__description__="Play a random playlist on startup."
__version__="16.02.02-01" # Format YY.MM.DD-XX (Year.Month.Day-Day Version)
__mantainer__="Rafael Senties Martinelli"
__website__="https://senties-martinelli.com/software/andromeda/plugins" # optional


def load_imports():
    """
        The imports must be included in a function called `load_imports`.
        It prevents making unnecessary imports when the plugin is not
        activated.
    """


    # Do not forget to add all the imports to the global scope
    global gi, Gtk, Gdk, Thread, randint, label_to_configuration_name

    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, Gdk

    from threading import Thread
    from random import randint


    from controller.utils import label_to_configuration_name


class Main:
    """
        The plugin must have a `Main` class. This is the one that will be 
        executed by Andromeda at the initialization.
     
        *Threads should always be used so the GUI don't get blocked. 
    """

    
    def __init__(self, parent, main_initialization):
        """
            `parent` is the Andromeda instance. With it you have acces to all the 
             objects of the player.
            
            `main_initialization` is an argument thatcwill inform you if the method is 
            being called from the Andromeda initialization.
            
            It is useful when the initialization must be different when the user activates 
            the plugin from the plugins window.
        """       
        self.__parent=parent
    
        # Add a button to the configuration and initialize it
        #
        self.checkbox=Gtk.CheckButton(label="Play random playlist on startup")
        
        # Try to read its default state from the configuration:
        #
        # Fore more information about `ccp` CustomCCParser look at:
        # https://www.rsm.website/software/gnu-linux/modules/python-ccparser
        
        config_name=label_to_configuration_name(self.checkbox.get_label())
        config_value=self.__parent.ccp.get_bool_defval(config_name, True)  # if the config doesn't exists, we choose to activate it
        
        self.checkbox.set_active(config_value)                           # Set the status of the checkbox
        self.checkbox.connect('toggled', self.on_checkbox_configuration_toggled)
        
            # Add the checkbox to the gui
        
            # To find the id of the objects use Glade on "gui.glade"
        self.config_box=self.__parent.builder.get_object('box30')
        self.config_box.add(self.checkbox)
        self.config_box.show_all()
    
        # Add a button at the bottom of the playlists
        self.button=Gtk.Button(label="Random Playlist")
        self.button.connect('clicked', self.on_button_random_playlist_clicked)
        
        self.playlists_box=self.__parent.builder.get_object('box32') 
        self.playlists_box.add(self.button)
        self.playlists_box.show_all()
    
        # play a random playlist at startup if request
        if config_value and main_initialization:
            Thread(target=self.random_playlist).start()
    
    def on_button_random_playlist_clicked(self, button, data=None):
        # play a random playlist
        Thread(target=self.random_playlist).start()
    
    def random_playlist(self):
        """
            Since we are updating the GUI from a thread, the methods need to be protected.
            Use Gdk.threads_enter(), and Gdk.threads_leave() around your methods. 
            
            ! This is pretty important or the GUI will crash !
            
            * Reading from the GUI does not require the protection.
        """
        
        number_of_playlists=len(self.__parent.liststore_playlists)
        
        if number_of_playlists > 0:
            
            # Select a playlist
            choiced_liststore=randint(0, number_of_playlists-1)
                        
            Gdk.threads_enter()
            self.__parent.treeview_selection_general_playlists.unselect_all()
            Gdk.threads_leave()
            
            Gdk.threads_enter()
            self.__parent.treeview_selection_playlists.select_path(choiced_liststore)
            Gdk.threads_leave()
            
            # Request an update of the tracks and play a track when it ends
            self.__parent.APPEND_request_to_queue(True)

    def on_checkbox_configuration_toggled(self, checkbox, data=None):
        """
            Write its state in to the configuration file
        """
        config_name=label_to_configuration_name(checkbox.get_label())
        button_state=checkbox.get_active()
        
        # Fore more information about `ccp` CustomCCParser look at:
        # https://www.rsm.website/software/gnu-linux/modules/python-ccparser
        self.__parent.ccp.write(config_name, button_state)

    def deactivate_plugin(self):
        """
            Method called when the plugin is deactivated
        """
        self.config_box.remove(self.checkbox)
        self.playlists_box.remove(self.button)


