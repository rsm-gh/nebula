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
    This is one part of the code that I’m pretty sure that it could be improved.
    I don’t know much about cellrenderers. Great doc at: 
    
        - http://python-gtk-3-tutorial.readthedocs.org/en/latest/objects.html
        - http://zetcode.com/gui/pygtk/signals/ https://lazka.github.io/pgi-docs/Gtk-3.0/classes/CellRenderer.html

"""


import gi
gi.require_version('Gtk', '3.0')
gi.require_version('PangoCairo', '1.0')
from gi.repository import Gtk


from CellRenderers.CellRendererRating import CellRendererRating
from CellRenderers.CellRendererTrackTime import CellRendererTrackTime
from CellRenderers.CellRendererBytes import CellRendererBytes
from CellRenderers.CellRendererTimeStamp import CellRendererTimeStamp
from CellRenderers.CellRendererURI import CellRendererURI
from CellRenderers.CellRendererLongText import CellRendererLongText
from CellRenderers.CellRendererAlbum import CellRendererAlbum

class Window(Gtk.Window):
    
    def on_rating_changed(self, liststore, treepath, rating):
        print('rating changed', treepath, rating)
    
    def __init__(self):
        Gtk.Window.__init__(self)
        self.connect('destroy', self.on_quit)
        
        box=Gtk.Box()

        liststore = Gtk.ListStore(int, 'glong', str)
        liststore.append([0, 100,           '/home/rsm/desktop/abc.ogg'])
        liststore.append([1, 23400,         '/home/rsm/desktop/abc.ogg'])
        liststore.append([2, 342342,        '/home/rsm/desktop/abc.ogg'])
        liststore.append([3, 5424334,       '/home/rsm/desktop/abc.ogg'])
        liststore.append([4, 83994234,      '/home/rsm/desktop/abc.ogg'])
        liststore.append([5, 9223375807,    '/home/rsm/desktop/abc.ogg'])

        treeview = Gtk.TreeView(liststore)
        
        treeviewcolumn = Gtk.TreeViewColumn("Rating")
        treeviewcolumn.set_resizable(True)
        cellrenderer = CellRendererRating()

        treeviewcolumn.pack_start(cellrenderer, True)
        treeviewcolumn.add_attribute(cellrenderer, 'rating', 0)
        treeview.append_column(treeviewcolumn)
        cellrenderer.connect_rating(treeviewcolumn, 0, self.on_rating_changed)
        
        treeviewcolumn = Gtk.TreeViewColumn("Time")
        treeviewcolumn.set_resizable(True)
        cellrenderer = CellRendererTrackTime()
        treeviewcolumn.pack_start(cellrenderer, True)
        treeviewcolumn.add_attribute(cellrenderer, 'miliseconds', 1)
        treeview.append_column(treeviewcolumn)

        treeviewcolumn = Gtk.TreeViewColumn("Bytes")
        treeviewcolumn.set_resizable(True)
        cellrenderer = CellRendererBytes()
        treeviewcolumn.pack_start(cellrenderer, True)
        treeviewcolumn.add_attribute(cellrenderer, 'bytes', 1)
        treeview.append_column(treeviewcolumn)

        treeviewcolumn = Gtk.TreeViewColumn("Time Stamp")
        treeviewcolumn.set_resizable(True)
        cellrenderer = CellRendererTimeStamp()
        treeviewcolumn.pack_start(cellrenderer, True)
        treeviewcolumn.add_attribute(cellrenderer, 'timestamp', 1)
        treeview.append_column(treeviewcolumn)

        treeviewcolumn = Gtk.TreeViewColumn("URI")
        treeviewcolumn.set_resizable(True)
        cellrenderer = CellRendererURI()
        treeviewcolumn.pack_start(cellrenderer, True)
        treeviewcolumn.add_attribute(cellrenderer, 'uri', 2)
        treeview.append_column(treeviewcolumn)

        box.add(treeview)
        
        
        #self.set_default_size(200, 200)        
        liststore = Gtk.ListStore(str)
        iconview = Gtk.IconView.new()
        iconview.set_model(liststore)
        
        cellrenderer = CellRendererAlbum()
        iconview.pack_start(cellrenderer, True)
        iconview.add_attribute(cellrenderer, 'text', 0)

        cellrenderer = CellRendererLongText()
        iconview.pack_start(cellrenderer, True)
        iconview.add_attribute(cellrenderer, 'text', 0)
        

        albums_ids=(
            'album-6d78a94f8a4b69df3c19f156656ef6c8',
            'album-5459e192058c81039572a0f4fb0b8024',
            'album-41137facf94fcf8b066ef0bf094f5ab0',
        )

        for icon_name in albums_ids:
            liststore.append([icon_name])

        box.add(iconview)
        
        
        self.add(box)
        self.show_all()

    def on_quit(self, widget, data=None):
        Gtk.main_quit()

w = Window()
Gtk.main()
