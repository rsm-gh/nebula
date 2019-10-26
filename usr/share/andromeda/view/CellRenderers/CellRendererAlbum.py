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


import gi
gi.require_version('Gtk', '3.0')
gi.require_version('PangoCairo', '1.0')
from gi.repository import Gtk, Gdk, GObject
from gi.repository.GdkPixbuf import Pixbuf
from gi.repository.Gdk import cairo_set_source_pixbuf

import os

# This is for the CellRendererAlbum
from Paths import Paths
PATHS=Paths()
DEFAULT_ALBUM_PIXBUF=Pixbuf.new_from_file(PATHS.albums_artwork_default)


class CellRendererAlbum(Gtk.CellRenderer):
    """ CellRenderer to display the album images """
    
    __gproperties__ = {
        'text': (  'gchararray', # type
                    "integer prop", # nick
                    "A property that contains a number in miliseconds", # blurb
                    '', # default
                    GObject.PARAM_READWRITE # flags
                    ),
    }

    def __init__(self):
        super().__init__()
        self.text = ''
        
    def do_set_property(self, pspec, value):
        setattr(self, pspec.name, value)

    def do_get_property(self, pspec):
        return getattr(self, pspec.name)

    def do_get_size(self, widget, cell_area):
        #return (0, 0, cell_area.width, cell_area.height)
        return (0, 0, 95, 95)

    def do_render(self, cr, widget, background_area, cell_area, flags):
        
        if self.text is None:
            Gdk.cairo_set_source_pixbuf(cr, DEFAULT_ALBUM_PIXBUF, cell_area.x, cell_area.y)
            
        else:
            path=PATHS.albums_artwork.format(self.text)
            
            if os.path.exists(path):
                cairo_set_source_pixbuf(cr, Pixbuf.new_from_file(path), cell_area.x, cell_area.y)
            
            else:
                cairo_set_source_pixbuf(cr, DEFAULT_ALBUM_PIXBUF, cell_area.x, cell_area.y)
                
            
        cr.paint()
            
            
GObject.type_register(CellRendererAlbum)


