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
from gi.repository import Gtk, PangoCairo, GObject

from .constants import FONT_COLOR, GENERAL_FONT_DESCRIPTION


def format_long_text(text, length=13):
    """
        Ex: "Anticonstitutionellement" to "Anticonstitu…"
    """
    
    if text is None:
        return ''
        
    elif len(text) > length:
        return text[:length-3]+'…'

    return text


class CellRendererLongText(Gtk.CellRenderer):
    """ CellRenderer to display long text."""
    
    __gproperties__ = {
        'text': (  'gchararray', # type
                    "string prop", # nick
                    "A property that contains formatted long text.", # blurb
                    '', # default
                    GObject.PARAM_READWRITE # flags
                    ),
    }

    def __init__(self):
        super().__init__()
        self.text = ''
        
        # the formatted value is stored to gain in perfomance when calling do_render().
        self.__formated_text = '' 
        
    def do_set_property(self, pspec, value):
        self.__formated_text = format_long_text(self.text)
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
        layout.set_text(self.__formated_text, -1)
        cr.save()
        #PangoCairo.update_layout(cr, layout)
        cr.move_to(cell_area.x, cell_area.y)
        PangoCairo.show_layout(cr, layout)
        cr.restore()
        
#     def activate(self, event, widget, path, background_area, cell_area, flags):
#         print(flags)

GObject.type_register(CellRendererLongText)
