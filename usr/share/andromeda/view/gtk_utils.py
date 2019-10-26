#!/usr/bin/python3
#

#  Copyright (C) 2016, 2019 Rafael Senties Martinelli 
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
from gi.repository import Gtk, GLib
from random import shuffle

def gtk_dialog_info(parent, text1, text2=None, icon=None):

    dialog = Gtk.MessageDialog(parent,
                               Gtk.DialogFlags.MODAL,
                               Gtk.MessageType.INFO,
                               Gtk.ButtonsType.CLOSE,
                               text1)

    if icon is not None:
        dialog.set_icon_from_file(icon)

    if text2 is not None:
        dialog.format_secondary_text(text2)

    dialog.run()
    dialog.destroy()

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
        liststore_iter=gtk_liststore.get_iter_first()
    else:
        liststore_iter=gtk_get_iter_from_liststore_cell(gtk_liststore, cellvalue, column)
    
        if liststore_iter is None:
            liststore_iter=gtk_liststore.get_iter_first()

    if liststore_iter is not None: # when a liststore is empty
        if not safe_thread:
            GLib.idle_add(gtk_selection.select_iter, liststore_iter)
        else:
            gtk_selection.select_iter(liststore_iter)


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
    _, treepaths = treeview_selection.get_selected_rows()
    
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