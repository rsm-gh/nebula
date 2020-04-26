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

import os
import traceback

def get_data(directory_path:str):
    plugins_dict={}

    for filename in os.listdir(directory_path):
                
        data={}
        
        if not filename.startswith('_') and filename.endswith('.py'):
            
            try:
            
                module=__import__(filename[:-3])
            
                module_title=module.__title__
            
                data['name']=module_title
                data['description']=module.__description__
                data['version']=module.__version__
                
                data['mantainer']=module.__mantainer__
                
                try:
                    data['website']=module.__website__
                except:
                    data['website']=''
            
                if not module_title in plugins_dict.keys():
                    plugins_dict[filename[:-3]]=data
                    
            except Exception:
                print(traceback.format_exc())
    
    return plugins_dict
