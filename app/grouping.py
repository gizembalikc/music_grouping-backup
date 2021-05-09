# -*- coding: utf-8 -*-
"""
Created on Sun May  2 15:46:12 2021

@author: gizem
"""

from collections import OrderedDict
import os
from flask import flash, request
import json 

class Grouping:
    
   __instance = None
   @staticmethod 
   def getInstance():
      """ Static access method. """
      if Grouping.__instance == None:
         Grouping()
      return Grouping.__instance
      
   def initialize_values (self):
      
      self.lookup_dict = return_dict()            
       
      self.main_dict = self.lookup_dict.copy()
      self.g1_dict = OrderedDict()
      self.g2_dict = OrderedDict()
      
      self.g1_name= ""
      self.g2_name= ""
      
      self.phase1_done = False
      self.grouping_done = False
      
      self.regrouping_dict = OrderedDict()
      self.no_child_group_keys = []
      self.regrouping_curr_g = 0
      self.regrouping_curr_group_key = "0.0"
      

      self.grouping_Q = []
      self.groups_dict = OrderedDict()
      self.curr_group_key = "0.0"
      
      self.level = 1

      self.num_of_child_nodes = 2
      self.num_of_active_nodes = 0 
      self.curr_child_index = 2
      
      self.messages = {
          "skip_info": "If you do not want to divide further, please click Skip button when all the elements in the main list.\n\n",
          "save_info": "If you want to save this grouping and continue grouping later please click Save button.\n\n",
          "next_info": "If you complete the grouping for current level, please click Next Step button to continue grouping."          ,
          "regrouping_info": "If you feel that a music piece does not fit any of the group you can add it to re-grouping list for later grouping.",
      }
    
       
   def __init__(self):
 
     self.initialize_values()
     
     if Grouping.__instance != None:
         return Exception("This class is a singleton!")
     else:
         Grouping.__instance = self

   def get_music(self):
    
        music = None
        music_name = take_selected_music()[0]
        if not(music_name == None) :
            music_filename = self.lookup_dict[music_name]
            music = { 'display_name' : music_name, 'filename' : music_filename }
        return music
   def next_step_operations(self):
       #same level
       if self.curr_child_index < self.num_of_child_nodes :
           self.curr_child_index += 2
       #level is changing
       else:
           self.curr_child_index = 2
           self.level += 1
           self.num_of_child_nodes = 2 * self.num_of_active_nodes
           self.num_of_active_nodes = 0         

       self.g1_dict = OrderedDict()
       self.g2_dict = OrderedDict()
    
       if (len(self.grouping_Q)==0 and len(self.regrouping_dict)==0):
           self.grouping_done = True
       elif (len(self.grouping_Q)==0 and not(len(self.regrouping_dict)==0)):
           self.phase1_done = True          
        #flash(messages.regrouping_desc)
       else:
           
        self.g1_name = "Group " + str(self.level) + "-" + str(self.curr_child_index-1);
        self.g2_name = "Group " + str(self.level) + "-" + str(self.curr_child_index);
        
        self.curr_group_key = self.grouping_Q[0]
        self.main_dict = self.groups_dict[self.curr_group_key]["elems"].copy()
        self.grouping_Q.remove(self.grouping_Q[0])
    
   def save_grouping(self, filename, grouping_done):
       
       data_to_write = OrderedDict()        
       data_to_write["grouping"] = self.groups_dict
       
       if(not(grouping_done)):
           application_variables=OrderedDict()
           data_to_write["variables"] = application_variables
           application_variables["level"] = self.level
           application_variables["curr_child_index"] = self.curr_child_index
           application_variables["num_of_child_nodes"] = self.num_of_child_nodes
           application_variables["num_of_active_nodes"] = self.num_of_active_nodes        
           application_variables["curr_group_key"] = self.curr_group_key
           
           application_variables["lookup_dict"] = self.lookup_dict         
           application_variables["main_dict"] = self.main_dict        
           application_variables["g1_dict"] = self.g1_dict        
           application_variables["g2_dict"] = self.g2_dict
#           application_variables["g1_name"] = self.g1_name
#           application_variables["g2_name"] = self.g2_name
           
           application_variables["phase1_done"] = self.phase1_done 
           application_variables["grouping_done"] = self.grouping_done
            
           application_variables["regrouping_dict"] = self.regrouping_dict
           application_variables["no_child_group_keys"] = self.no_child_group_keys
           application_variables["regrouping_curr_g"] = self.regrouping_curr_g
           application_variables["regrouping_curr_group_key"] = self.regrouping_curr_group_key
           
           application_variables["grouping_Q"] = self.grouping_Q
       
       if not os.path.exists('app/outputs'):
           os.mkdir('app/outputs')
    
      
       with open('app/outputs/' + filename, 'w+') as json_file:
           json.dump(data_to_write, json_file)
    
       
   def save_completed_level(self):
       g1_key = str(self.level) + "-" + str(self.curr_child_index-1) 
       g2_key = str(self.level) + "-" + str(self.curr_child_index)

       g_1_temp_dict = OrderedDict()
       g_2_temp_dict = OrderedDict()
       
       g_1_temp_dict["elems"] = self.g1_dict.copy()
       g_2_temp_dict["elems"] = self.g2_dict.copy()
       
       
       
       g_1_temp_dict["has_child"] = self.add_to_queue(self.g1_dict, g1_key)
       if(not(g_1_temp_dict["has_child"])):
           self.no_child_group_keys.append(g1_key)
       
       g_2_temp_dict["has_child"] = self.add_to_queue(self.g2_dict, g2_key)
       if(not(g_2_temp_dict["has_child"])):
           self.no_child_group_keys.append(g2_key)
       
       self.groups_dict[g1_key] = g_1_temp_dict
       self.groups_dict[g2_key] = g_2_temp_dict

   def skip_operations(self):
       #print(self.curr_group_key)
       self.groups_dict[self.curr_group_key]["has_child"] = False
       #print(self.groups_dict[self.curr_group_key]["has_child"])       
       self.no_child_group_keys.append(self.curr_group_key)
       self.curr_child_index-=2
       self.num_of_child_nodes-=2
       self.next_step_operations()
   
   def reload_operations(self,filepath):
       
       
        temp_dict = OrderedDict()
    
        with open(filepath) as json_file:
            data = json.load(json_file)
            ##completed groups
            grouping_data = data["grouping"]

            for temp_key in sorted(grouping_data.keys()):
                temp_dict[temp_key] = grouping_data[temp_key]
            self.groups_dict = temp_dict 

            ##application variables
            application_variables = data["variables"]
      
            self.level = application_variables["level"]        
            self.curr_child_index = application_variables["curr_child_index"] 
            self.num_of_child_nodes = application_variables["num_of_child_nodes"]
            self.num_of_active_nodes = application_variables["num_of_active_nodes"] 
            self.curr_group_key = application_variables["curr_group_key"] 
            
            self.group_Q = application_variables["grouping_Q"]
        
        
            self.lookup_dict = application_variables["lookup_dict"]   
            self.main_dict = application_variables["main_dict"]
            self.g1_dict = application_variables["g1_dict"]
            self.g2_dict = application_variables["g2_dict"]
#            self.g1_name = application_variables["g1_name"]
#            self.g2_name = application_variables["g2_name"]            
        
            self.regrouping_dict = application_variables["regrouping_dict"] 
            self.regrouping_curr_g = application_variables["regrouping_curr_g"]        
            self.no_child_group_keys = application_variables["no_child_group_keys"]        
            self.regrouping_curr_group_key = application_variables["regrouping_curr_group_key"]
            
            self.phase1_done = application_variables["phase1_done"]
            self.grouping_done = application_variables["grouping_done"]
            
#            if(self.phase1_done):
#                print("regrouping reload")
#                #group_elems = regrouping_get_next_group(grouping) 
#                #return render_template('regrouping.html',display_name = None, musicname = None,regrouping_list_entries=grouping.regrouping_dict,g_name=grouping.regrouping_curr_group_key,g_entries=group_elems);
            if not(self.phase1_done):
                self.g1_name = "Group " + str(self.level) + "-" + str(self.curr_child_index-1);
                self.g2_name = "Group " + str(self.level) + "-" + str(self.curr_child_index);
   
   def regrouping_next_group(self):
       if self.regrouping_curr_g == len(self.no_child_group_keys):
           self.regrouping_curr_g = 0
       self.regrouping_curr_group_key = self.no_child_group_keys[self.regrouping_curr_g]
       return self.groups_dict[self.regrouping_curr_group_key]["elems"]
       
   def add_to_queue(self, g_dict, g_key):       
       if(len(g_dict)>1):
           self.grouping_Q.append(g_key)
           self.num_of_active_nodes+=1
           return True
       else:
           return False
   
def regrouping_next(grouping):   
    if len(grouping.regrouping_dict) == 0:
        grouping.grouping_done = True
        return None
    else:
        grouping.regrouping_curr_g += 1
        return grouping.regrouping_next_group()

def return_dict():
    music_file_info = OrderedDict()
    music_id = 1
    path = "app/static/music"
    for f in sorted(os.listdir(path)):
        if f.endswith(".mp3"):
            name = "Music_" + str(music_id)
            music_file_info[name] = f
            music_id+=1
    return music_file_info 

def take_selected_music():    
    if not (request.form.get('main_play_list') == None):
        return request.form.get('main_play_list'), 0
    elif not (request.form.get('g1_play_list') == None):
        return request.form.get('g1_play_list') , 1
    elif not (request.form.get('g2_play_list') == None):
        return request.form.get('g2_play_list') , 2
    elif not (request.form.get('ungrouped_play_list') == None):
        return request.form.get('ungrouped_play_list') , 3
    elif not (request.form.get('g_play_list') == None):
        return request.form.get('g_play_list') , 4
    else:
        return None , -1

def add_ToGroup(reference_dict_id, reference_dict, target_dict):
       music_name, selected_group_id = take_selected_music()
       if selected_group_id == reference_dict_id and not(music_name==None):
           target_dict[music_name] = reference_dict.pop(music_name)
           return True
       else:
            #TODO mesaj eklenebilir returnler kalkabilir kullanan yok returnleri
            return False

def add_for_regrouping(grouping, reference_dict_id):

    music_name, selected_group_id = take_selected_music()    
    if not(music_name == None):
        if reference_dict_id == 0 and selected_group_id == reference_dict_id and grouping.level > 1:
            grouping.regrouping_dict[music_name] = grouping.main_dict.pop(music_name)
            grouping.groups_dict[grouping.curr_group_key]["elems"].pop(music_name)
            
        elif reference_dict_id == 0 and selected_group_id == reference_dict_id and grouping.level == 1:
            grouping.regrouping_dict[music_name] = grouping.main_dict.pop(music_name)
            
        elif reference_dict_id == 4 and reference_dict_id == selected_group_id:
            grouping.regrouping_dict[music_name] = grouping.groups_dict[grouping.regrouping_curr_group_key]["elems"].pop(music_name)

def next_step(grouping):

   if(len(grouping.g1_dict)==0  or (len(grouping.g2_dict)==0)):
        flash("Please put at least one song in each group,");
        flash(grouping.messages["skip_info"])        
   elif(not(len(grouping.main_dict) == 0)):
        flash("Please group every song in the music list!\n\n")
        flash(grouping.messages["skip_info"])
        flash(grouping.messages["save_info"])
        flash(grouping.messages["regrouping_info"])
   else:
        grouping.save_completed_level()
        if(len(grouping.grouping_Q)==0 and grouping.level>2 and not(len(grouping.regrouping_dict)==0)):
            grouping.phase1_done = True            
        elif(len(grouping.grouping_Q)==0 and grouping.level>2):
            grouping.grouping_done = True
        else:
            grouping.next_step_operations()

def skip_grouping(grouping):    
    if grouping.level==1 :    
        flash("You can not skip grouping at the first level")
    elif len(grouping.g1_dict)==0 and len(grouping.g2_dict)==0:
        grouping.skip_operations()
    elif len(grouping.main_dict)==0:
        flash("The \"Grouping List\" is empty, you completed grouping for this level")
        #flash(grouping.messages["next_info"])
        #flash(grouping.messages["save_info"])
        
    else:
        flash("You have uncompleted grouping,main list not empty")
        flash(grouping.messages["regrouping_info"])
        
def save(grouping, filename, grouping_done = False):
    if (grouping_done):
        grouping.save_grouping(filename, grouping_done)
    elif not(grouping.phase1_done) and len(grouping.groups_dict)==0 and len(grouping.g1_dict) == 0 and len(grouping.g2_dict) == 0 and len(grouping.regrouping_dict)==0:
        flash("There is no gruouping in progress for saving.")
    else:
        grouping.save_grouping(filename, grouping_done)
        flash("Please click the reload this grouping later to continue with grouping. Thank you!")
        
def reload_saved_grouping(grouping,filename) :
    path = "app/outputs"
    filepath = path + "/" + filename
    if(len(os.listdir(path))==0):
        flash("There is no saved grouping!")
    else:
        with open(filepath) as json_file:
            data = json.load(json_file)
            if(len(data)==1):
                flash('There is no uncompleted grouping!')
            else:
                grouping.reload_operations(filepath)

