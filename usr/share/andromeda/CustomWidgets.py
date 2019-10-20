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

    This is one part of the code that I'm pretty sure that it could be
    improved. I don't know much about cellrenderers.

    Great doc at:   http://python-gtk-3-tutorial.readthedocs.org/en/latest/objects.html
                    http://zetcode.com/gui/pygtk/signals/
                    https://lazka.github.io/pgi-docs/Gtk-3.0/classes/CellRenderer.html





    Concerning the CellRendererRating, I'm currently stuck for detecting 
    the mouse-click/mouse-over so I can change the stars.

                    

"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('PangoCairo', '1.0')
from gi.repository import Gtk, Gdk, cairo, Pango, PangoCairo, GObject
from gi.repository.GdkPixbuf import Pixbuf
from gi.repository.Gdk import cairo_set_source_pixbuf

import os
from datetime import timedelta, datetime
from urllib.parse import unquote

# This is for the CellRendererAlbum
from Paths import Paths
PATHS=Paths()
DEFAULT_ALBUM_PIXBUF=Pixbuf.new_from_file(PATHS.albums_artwork_default)


def GTK_get_default_font_color():
        
    for color in SETTINGS.get_property('gtk-color-scheme').split('\n'):
        if 'text' in color:
            text_color=color.split(':')[1].strip()
            
            if ';' in text_color:
                text_color=text_color.split(';',1)[0]
            
            return text_color

    return '#000000'


def CONVERT_hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))



"""
    Set some global variables for all the CellRenderers. I didn't wanted to use
    attributes.
"""

SETTINGS=Gtk.Settings.get_default()

FONT_COLOR=CONVERT_hex_to_rgb(GTK_get_default_font_color())
FONT_STR=SETTINGS.get_property('gtk-font-name')
GENERAL_FONT_DESCRIPTION=Pango.font_description_from_string(FONT_STR)

FONT_TYPE=FONT_STR.rsplit(' ',1)[0]
FONT_SIZE=FONT_STR.rsplit(' ',1)[1]

FONT_CELLRATING='{} {}'.format(FONT_TYPE, int(FONT_SIZE)+5)
FONT_CELLRATING_DESCRIPTION=Pango.font_description_from_string(FONT_CELLRATING)


def FORMAT_miliseconds(miliseconds):
    time_string=str(timedelta(milliseconds=miliseconds)).split('.')[0]

    # remove the hours if they are not necessary.
    try:
        if int(time_string.split(':',1)[0]) == 0:  
            time_string=time_string.split(':',1)[1]
    except:
        pass
    
    return time_string

class CellRendererTrackTime(Gtk.CellRenderer):
    """ CellRenderer to display miliseconds to time, ex: 234234 -> 03:54 """
    
    __gproperties__ = {
        'miliseconds': (    'glong', # type
                            "integer prop", # nick
                            "A property that contains a number in miliseconds", # blurb
                            0, # min
                            9223372036854775807, # max
                            0, # default
                            GObject.PARAM_READWRITE # flags
                            ),
    }

    def __init__(self):
        super().__init__()
        self.miliseconds = 0
        
    def activate(event, widget, path, background_area, cell_area, flags):
        print(flags)
        
    def do_set_property(self, pspec, value):
        setattr(self, pspec.name, value)

    def do_get_property(self, pspec):
        return getattr(self, pspec.name)
        
    #def do_get_size(self, widget, cell_area):
        #return (0, 0, cell_area.width, cell_area.height)
        #return (0, 0, self.miliseconds.get_width(), self.miliseconds.get_height())

    def do_render(self, cr, widget, background_area, cell_area, flags):
        
        cr.set_source_rgb (FONT_COLOR[0], FONT_COLOR[1], FONT_COLOR[2])
        layout = PangoCairo.create_layout(cr)
        layout.set_font_description(GENERAL_FONT_DESCRIPTION)
        layout.set_text(FORMAT_miliseconds(self.miliseconds), -1)
        cr.save()
        #PangoCairo.update_layout(cr, layout)
        cr.move_to(cell_area.x, cell_area.y)
        PangoCairo.show_layout(cr, layout)
        cr.restore()

GObject.type_register(CellRendererTrackTime)


def FORMAT_bytes(num):
    """ Format bytes in to human readable """
    
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024:
            return '{0} {1}{2}'.format(round(num,0), unit, 'B')
        num /= 1024
        
    return '{0} {1}{2}'.format(round(num,0), 'Yi', 'B')


class CellRendererBytes(Gtk.CellRenderer):
    """ CellRenderer to display kilobytes, ex: 234234 -> 03:54 """
    
    __gproperties__ = {
        'bytes': (      'glong', # type
                        "integer prop", # nick
                        "A property that contains a number in miliseconds", # blurb
                        0, # min
                        9223372036854775807, # max
                        0, # default
                        GObject.PARAM_READWRITE # flags
                        ),
    }

    def __init__(self):
        super().__init__()
        self.bytes = 0
        
    def activate(event, widget, path, background_area, cell_area, flags):
        print(flags)
        
    def do_set_property(self, pspec, value):
        setattr(self, pspec.name, value)

    def do_get_property(self, pspec):
        return getattr(self, pspec.name)
        
    #def do_get_size(self, widget, cell_area):
        #return (0, 0, cell_area.width, cell_area.height)
        #return (0, 0, self.kilobytes.get_width(), self.kilobytes.get_height())

    def do_render(self, cr, widget, background_area, cell_area, flags):
        
        cr.set_source_rgb (FONT_COLOR[0], FONT_COLOR[1], FONT_COLOR[2])
        layout = PangoCairo.create_layout(cr)
        layout.set_font_description(GENERAL_FONT_DESCRIPTION)
        layout.set_text(FORMAT_bytes(self.bytes), -1)
        cr.save()
        #PangoCairo.update_layout(cr, layout)
        cr.move_to(cell_area.x, cell_area.y)
        PangoCairo.show_layout(cr, layout)
        cr.restore()

GObject.type_register(CellRendererTrackTime)


def FORMAT_timestamp(number):
    
    if number == 0: 
        return ''
    
    return str(datetime.fromtimestamp(number))


class CellRendererTimeStamp(Gtk.CellRenderer):
    """ CellRenderer to display timestamps, Ex: 10000 to '1970-01-01 01:16:40' """
    
    __gproperties__ = {
        'timestamp': (  'glong', # type
                        "integer prop", # nick
                        "A property that contains a number in miliseconds", # blurb
                        0, # min
                        9223372036854775807, # max
                        0, # default
                        GObject.PARAM_READWRITE # flags
                        ),
    }

    def __init__(self):
        super().__init__()
        self.timestamp = 0
        
    def activate(event, widget, path, background_area, cell_area, flags):
        print(flags)
        
    def do_set_property(self, pspec, value):
        setattr(self, pspec.name, value)

    def do_get_property(self, pspec):
        return getattr(self, pspec.name)
        
    #def do_get_size(self, widget, cell_area):
        #return (0, 0, cell_area.width, cell_area.height)
        #return (0, 0, self.kilobytes.get_width(), self.kilobytes.get_height())

    def do_render(self, cr, widget, background_area, cell_area, flags):
        
        cr.set_source_rgb (FONT_COLOR[0], FONT_COLOR[1], FONT_COLOR[2])
        layout = PangoCairo.create_layout(cr)
        layout.set_font_description(GENERAL_FONT_DESCRIPTION)
        layout.set_text(FORMAT_timestamp(self.timestamp), -1)
        cr.save()
        #PangoCairo.update_layout(cr, layout)
        cr.move_to(cell_area.x, cell_area.y)
        PangoCairo.show_layout(cr, layout)
        cr.restore()

GObject.type_register(CellRendererTimeStamp)


def FORMAT_uri(path):
    """
        This will format an uri to a path, and it will try to find the
        path to the song in case it doesn't exists.
    """
    return unquote(path).replace('file://','')


class CellRendererURI(Gtk.CellRenderer):
    """ CellRenderer to display timestamps, Ex: 10000 to '1970-01-01 01:16:40' """
    
    __gproperties__ = {
        'uri': (  'gchararray', # type
                    "integer prop", # nick
                    "A property that contains a number in miliseconds", # blurb
                    '', # default
                    GObject.PARAM_READWRITE # flags
                    ),
    }

    def __init__(self):
        super().__init__()
        self.uri = ''
        
    def activate(event, widget, path, background_area, cell_area, flags):
        print(flags)
        
    def do_set_property(self, pspec, value):
        setattr(self, pspec.name, value)

    def do_get_property(self, pspec):
        return getattr(self, pspec.name)

    #def do_get_size(self, widget, cell_area):
        #return (0, 0, cell_area.width, cell_area.height)
        #return (0, 0, self.kilobytes.get_width(), self.kilobytes.get_height())

    def do_render(self, cr, widget, background_area, cell_area, flags):
            
        cr.set_source_rgb (FONT_COLOR[0], FONT_COLOR[1], FONT_COLOR[2])
        layout = PangoCairo.create_layout(cr)
        layout.set_font_description(GENERAL_FONT_DESCRIPTION)
        layout.set_text(FORMAT_uri(self.uri), -1)
        cr.save()
        #PangoCairo.update_layout(cr, layout)
        cr.move_to(cell_area.x, cell_area.y)
        PangoCairo.show_layout(cr, layout)
        cr.restore()

GObject.type_register(CellRendererURI)


def FORMAT_long_text(text, length=13):
    """
        Ex: "Anticonstitutionellement" to "Anticonstitu…"
    """
    
    if text is None:
        return ''
        
    elif len(text) > length:
        return text[:length-3]+'…'

    return text


class CellRendererLongText(Gtk.CellRenderer):
    """ CellRenderer to display timestamps, Ex: 10000 to '1970-01-01 01:16:40' """
    
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
        
    def activate(event, widget, path, background_area, cell_area, flags):
        print(flags)
        
    def do_set_property(self, pspec, value):
        setattr(self, pspec.name, value)

    def do_get_property(self, pspec):
        return getattr(self, pspec.name)

    def do_get_size(self, widget, cell_area):
        #return (0, 0, cell_area.width, cell_area.height)
        return (0, 0, 90, 20)

    def do_render(self, cr, widget, background_area, cell_area, flags):
            
        cr.set_source_rgb (FONT_COLOR[0], FONT_COLOR[1], FONT_COLOR[2])
        layout = PangoCairo.create_layout(cr)
        layout.set_font_description(GENERAL_FONT_DESCRIPTION)
        layout.set_text(FORMAT_long_text(self.text), -1)
        cr.save()
        #PangoCairo.update_layout(cr, layout)
        cr.move_to(cell_area.x, cell_area.y)
        PangoCairo.show_layout(cr, layout)
        cr.restore()

GObject.type_register(CellRendererLongText)


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





class CellRendererRating(Gtk.CellRenderer):
    """ Cellrenderer to display ratings from 0 to 5: ★★★★★, ★★★☆☆, etc """
    
    __gproperties__ = {
        'rating': ( int, # type
                    "integer prop", # nick
                    "A property that contains an integer", # blurb
                    0, # min
                    5, # max
                    0, # default
                    GObject.PARAM_READWRITE # flags
                    ),
    }

    def __init__(self, treeview=False):
        super().__init__()
        self.font_size=15
        self.font="Sans Bold {}".format(self.font_size)
        self.rating = 0
        
        self._clicked=()
        self._clicked_function=False
        
        if treeview:
            self.connect_treeview(treeview)

    def connect_rating(self, treeviewcolumn, column=0, func=False):
        """
            This should be conected once the cellrendere has been
            added to the treeviewcolumn.
            
            column=0, is the number of the rating column at the
            treeview liststore.
            
            func is a function to be called when a rating is edited,
            it must accept the arguments (treeview, treepath, rating)
            
        """
        treeview=treeviewcolumn.get_tree_view()
        treeview.connect('cursor-changed', self.update_from_click)
        self._column=column
        self._liststore=treeview.get_model()
        self._clicked_function=func

    def do_render(self, cr, treeview, background_area, cell_area, flags):
        mouse_x, mouse_y = treeview.get_pointer()
        cell_render_x = mouse_x - cell_area.x
        
        #
        # Update the rating if it was clicked (the liststore is updated too)
        #
        if self._clicked != ():
            x_click_coord=self._clicked[0]
            self._clicked=()
            
            # Check if the click was inside the cell
            #
            if x_click_coord >= cell_area.x and x_click_coord <= cell_area.x+self.font_size*5 and 'SELECTED' in str(flags):
                rating=round(cell_render_x/self.font_size)
                
                if rating >= 0 and rating <= 5 and rating != self.rating:
                    self.rating=rating

                    try:
                        pointing_treepath=treeview.get_path_at_pos(mouse_x, mouse_y-self.font_size)[0]
                        self._liststore[pointing_treepath][self._column]=self.rating
                        
                    except Exception as e:
                        print(e)

                    if self._clicked_function:
                        self._clicked_function(self._liststore, pointing_treepath, rating)

        #
        # Draw the rating
        #
        cr.translate (0, 0)
        layout = PangoCairo.create_layout(cr)
        layout.set_font_description(FONT_CELLRATING_DESCRIPTION)
    
        y_height_correction=self.font_size/3
        cell_height=self.font_size+1
    
        if 'GTK_CELL_RENDERER_FOCUSED' in str(flags) and self.rating < 5:
            for i in range(5):
                if i < self.rating:
                    layout.set_text("★", -1)
                else:
                    layout.set_text("☆", -1)
                  
                cr.save()
                PangoCairo.update_layout (cr, layout)
                cr.move_to (cell_area.x+i*cell_height, cell_area.y-y_height_correction)
                PangoCairo.show_layout (cr, layout)
                cr.restore()
            
        else:
            for i in range(self.rating):
                layout.set_text("★", -1)
                cr.save()
                PangoCairo.update_layout (cr, layout)
                cr.move_to (cell_area.x+i*cell_height, cell_area.y-y_height_correction)
                PangoCairo.show_layout (cr, layout)
                cr.restore()

    def update_from_click(self, treeview, data=None):
        self._clicked=treeview.get_pointer()

    def do_set_property(self, pspec, value):
        setattr(self, pspec.name, value)

    def do_get_property(self, pspec):
        return getattr(self, pspec.name)
        
    def do_get_size(self, widget, cell_area):
        return (0, 0, self.font_size*5, self.font_size+5)


GObject.type_register(CellRendererRating)




if __name__ == '__main__':


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
