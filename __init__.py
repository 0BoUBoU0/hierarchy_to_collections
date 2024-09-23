# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Hierarchy To Collections",
    "author": "Yannick 'BoUBoU' Castaing",
    "description": "Allows you to switch between collection and empties hierarchy",
    "location": "View3D > UI > Workflow panel",
    "doc_url": "",
    "warning": "",
    "category": "Workflow",
    "blender": (2,90,0),
    "version": (1,2,93)
}

# get addon name and version to use them automaticaly in the addon
Addon_Name = str(bl_info["name"])
Addon_Version = str(bl_info["version"])
Addon_Version = Addon_Version[1:8].replace(",",".")

### import modules ###
import bpy
import random

### define global variables ###
debug_mode = False
separator = "-" * 20

### create functions ###
def createColl(collName,clean,link): # variable, remove collection ?, link collection ?
    if clean == True:
        if collName in bpy.data.collections.keys(): # clean to avoid doubles
            bpy.data.collections.remove(bpy.data.collections[collName])
    if collName not in bpy.data.collections.keys():
        bpy.data.collections.new(collName)
    if link == True:
        if collName not in bpy.context.scene.collection.children.keys():
            bpy.context.scene.collection.children.link(bpy.data.collections[collName])

def collections_list(collection, coll_list): # collection name, collection list
    coll_list.append(collection)
    for sub_collection in collection.children:
        collections_list(sub_collection, coll_list)
        
def getChildren(obj_parent):
    children_list = []
    for obj in bpy.data.objects:
        if obj.parent == obj_parent:
            children_list.append(obj)
            #print(obj.name)
    return children_list

### create property ###
class HIERTOCOL_properties (bpy.types.PropertyGroup):
    hiertocol_transformobjecttype_options = [("ALL OBJECTS","ALL OBJECTS","ALL OBJECTS",0),("EMPTIES ONLY","EMPTIES ONLY","EMPTIES ONLY",1)]
    hiertocol_transformobjecttype : bpy.props.EnumProperty (items = hiertocol_transformobjecttype_options,name = "Apply transforms",description = "choose selection type",default=0)
    hiertocol_resetscale : bpy.props.BoolProperty (default=True,name="Scale (recommended)",description="clean by applying the scale from any value to 1")
    hiertocol_resetrotation : bpy.props.BoolProperty (default=True,name="Rotation (recommanded)",description="clean by applying the rotation")
    hiertocol_resetlocation : bpy.props.BoolProperty (default=False,name="Location",description="clean by applying the location")
    

### create panels ###
# create panel UPPER_PT_lower
class OBJECT_PT_hiertocolpanelall(bpy.types.Panel):
    bl_label = f"{Addon_Name} - {Addon_Version}"
    bl_idname = "OBJECT_PT_hiertocolpanelall"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Workflow"
    
    def draw(self, context):
        hiertocol_props = context.scene.hiertocol_props
        col = self.layout.column()
        row = col.row()
        row.operator("hiertocol.emptiestocollections",text="Empties to Collections",emboss=True,depress=False,icon="COLLECTION_NEW")
        row = col.row()
        col.operator("hiertocol.collectionstoempties",text="Collections to Empties",emboss=True,depress=False,icon="EMPTY_AXIS")
        

class OBJECT_PT_hiertocolpanelAdvanced(bpy.types.Panel):
    bl_label = f"Advanced"
    bl_idname = "OBJECT_PT_hiertocolpanelAdvanced"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tool"
    bl_parent_id = "OBJECT_PT_hiertocolpanelall"

    def draw(self, context):
        col = self.layout.column()
        hiertocol_props = context.scene.hiertocol_props
        row = col.row()
        row.prop(hiertocol_props, "hiertocol_transformobjecttype")
        row = col.row()
        row.prop(hiertocol_props, "hiertocol_resetscale")
        row.prop(hiertocol_props, "hiertocol_resetrotation")
        row.prop(hiertocol_props, "hiertocol_resetlocation")

### create operators ###        
# create operator UPPER_OT_lower and idname = upper.lower         
class OBJECT_OT_hiertocolemptiestocollections(bpy.types.Operator):
    bl_idname = 'hiertocol.emptiestocollections'
    bl_label = Addon_Name + "empty to collections"
    bl_description = "Allows you to take an empty hierarchy to a collection hierarchy. The easiest way is to select only the root empty \n\n /!\ WARNING : If nothing is selected, it will use the complete scene !"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        print(f"\n {separator} Begin {Addon_Name} (empty to collections) {separator} \n")
        
        color_tag = f"COLOR_0{random.randrange(1,9)}"

        ## create "selected objects" set
        selected_obj = []
        if len(bpy.context.selected_objects)==1: # select only root empty
            print("root empty")
            root_parent = bpy.context.selected_objects[0]
            selected_obj.append(root_parent)
            children_list = getChildren(root_parent)
            for children in children_list:
                selected_obj.append(children)
                children_list_tmp = getChildren(children)
                for children in children_list_tmp:
                    children_list.append(children)
        elif len(bpy.context.selected_objects)==0: # select all
            print("all objects")
            for obj in bpy.context.scene.objects:
                selected_obj.append(obj)
        elif len(bpy.context.selected_objects)>1: # selected elements
            print("selected elements")
            selected_obj = bpy.context.selected_objects

        #print(f"{selected_obj=}")
        ### deselect
        bpy.ops.object.select_all(action='DESELECT')
        ### select 
        
        
        ## clean transform if user wants:
        # create selection
        obj_to_clean = []
        if bpy.context.scene.hiertocol_props.hiertocol_transformobjecttype == "EMPTIES ONLY":
            for obj in selected_obj:
                if obj.type == "EMPTY":
                    obj_to_clean.append(obj)
                    obj.select_set(True)
        else:
            for obj in selected_obj:
                obj_to_clean.append(obj)
                obj.select_set(True)
        #print(f"{obj_to_clean=}")
        # apply selections
        for obj in obj_to_clean:
            apply_scale = False
            apply_rotation = False
            apply_location = False           
            if bpy.context.scene.hiertocol_props.hiertocol_resetscale == True:
                apply_scale = True
            if bpy.context.scene.hiertocol_props.hiertocol_resetrotation == True:
                apply_rotation = True
            if bpy.context.scene.hiertocol_props.hiertocol_resetlocation == True:
                apply_location = True 
            bpy.ops.object.transform_apply(location=apply_location, rotation=apply_rotation, scale=apply_scale)
        
        ## create dictionnary about collection hierarchy IN THE WHOLE SCENE : (keys: collection, values: objects)
        coll_from_empty = {}      
        for obj in selected_obj:
            if obj.type == "EMPTY" or obj.type == 'ARMATURE':
                #print(obj.name)
                createColl(obj.name,True,False) # use class to create collection : object name, clear before, don't link
                coll = bpy.data.collections[obj.name]
                coll.color_tag = color_tag
                coll_from_empty[obj] = coll
        ## create root collection, and storage collection
        for obj, coll in coll_from_empty.items():
            parent = coll_from_empty.get(obj.parent)
            if parent == None:
                root_coll_name = obj.name
        createColl(root_coll_name,False,True) #create root coll and link coll
        root_coll = bpy.data.collections[root_coll_name]
        ## create a random color for hierarchy or take the random color existing
        if root_coll.color_tag == "NONE":
            root_coll.color_tag = color_tag
        else:
            color_tag = root_coll.color_tag 
            
        ## build collection hierarchy
        for obj, coll in coll_from_empty.items():
            parent = coll_from_empty.get(obj.parent)    
            if parent:
                parent.children.link (coll)

        ## create empties collection to select original hierarchy
        empties_storage_coll_name = f"{root_coll.name}-EmptiesHierarchy" #storage
        createColl(empties_storage_coll_name,True,True) #create coll
        empties_storage_coll = bpy.data.collections[empties_storage_coll_name]
        empties_storage_coll.color_tag = color_tag

        ## unlink all selected objects in scene
        for obj in selected_obj:
            if obj in bpy.context.scene.collection.objects.values():
                bpy.context.scene.collection.objects.unlink(bpy.data.objects[obj.name])
        for obj in bpy.context.selected_objects:
            for col in bpy.context.scene.objects[obj.name].users_collection:
                bpy.data.collections[col.name].objects.unlink(bpy.data.objects[obj.name])

        ## put objects in the right collection     
        for obj in selected_obj:
            if obj.type != 'EMPTY':
                if obj.parent != None:
                    coll_parent = coll_from_empty.get(obj.parent)
                    coll_parent.objects.link(obj)
                else:
                    root_coll.objects.link(obj)
            else:
                empties_storage_coll.objects.link(obj)
        
        print(f"{Addon_Name} done on : {str(selected_obj)} \n")
        print(f"\n {separator} {Addon_Name} (empty to collections) Finished {separator} \n")
        
        return {"FINISHED"}

# create operator UPPER_OT_lower and idname = upper.lower         
class OBJECT_OT_hiertocolcollectionstoempties(bpy.types.Operator):
    bl_idname = 'hiertocol.collectionstoempties'
    bl_label = Addon_Name + "(collections to empties)"
    bl_description = "create empty hierarchy from active collection's hierarchy"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):       
        print(f"\n {separator} Begin {Addon_Name} (collections to empties) {separator} \n")
        
        ## define random color tag
        color_tag = f"COLOR_0{random.randrange(1,9)}"
        
        ## put cursor at origin 
        cursor_loc = bpy.context.scene.cursor.location
        cursor_rot = bpy.context.scene.cursor.rotation_euler
        bpy.context.scene.cursor.location = (0,0,0)
        bpy.context.scene.cursor.rotation_euler = (0,0,0)
        
        ## deselect all in scene  
        bpy.ops.object.select_all(action='DESELECT')
        
        ## list  collections only in scene
        root_collection = bpy.context.view_layer.active_layer_collection 
        #= bpy.context.view_layer.layer_collection
        master_collection = bpy.context.scene.collection
        
        ## list all collections in the current scenes 
        coll_in_scene_list = []
        collections_list(bpy.context.collection, coll_in_scene_list)
        coll_in_scene_list.pop(0) # erase master collection
           
        ## create storage collection by scene
        # createColl(root_coll_name,False,True) #create and link coll
        root_coll = bpy.data.collections[root_collection.name]
        color_tag = root_coll.color_tag 

        ## create empties collection to select original hierarchy
        empties_storage_coll_name = f"{root_coll.name}-EmptiesHierarchy" #storage
        createColl(empties_storage_coll_name,True,True) #create coll
        empties_storage_coll = bpy.data.collections[empties_storage_coll_name]
        empties_storage_coll.color_tag = color_tag
        
        #print(f"{root_coll.name=}")
        #print(f"{empties_storage_coll.name=}")

        ## select storage collection
        bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[empties_storage_coll.name]
        
        ## create dictionnary about collection hierarchy : (keys: parents, values: children) and if no child = None
        coll_relation = {}
        for key, value in bpy.data.collections.items():
            if key != empties_storage_coll.name:
                if value.children.keys() == []:
                    coll_relation[key] = ['None']
                else:
                    coll_relation[key] = value.children.keys()

        #print(f"{coll_relation=}")
        
        ## empties creation
        empties_list = []
        for coll in coll_relation.keys():
            if coll in bpy.data.objects.keys() and bpy.data.objects[coll].type == 'EMPTY':
                bpy.data.objects.remove(bpy.data.objects[coll], do_unlink=True)        
            bpy.ops.object.add()
            obj = bpy.context.active_object
            obj.name = coll
            empties_list.append(obj)

        #print(f"{empties_list=}")
               
        ## create 'None' empty
        bpy.ops.object.add()
        obj = bpy.context.active_object
        obj.name = 'None'
        
        ## creation lists (keys = parents, values = children)
        keys_list = list(coll_relation.keys())
        values_list = list(coll_relation.values())
        
        # def variables
        iter = 0
        sub_iter = ()
        values_length = len(coll_relation.values())
        
        ## create empties hierarchy
        empty_from_coll = []
        for value in coll_relation.values():
            if iter + 1 <= values_length:
                sub_iter = 0
                for subvalue in values_list:
                    if sub_iter + 1  <= len(values_list[iter]):
                        empty_parent = bpy.data.objects[keys_list[iter]]
                        empty_child = bpy.data.objects[values_list[iter][sub_iter]]
                        empty_child.parent = empty_parent
                        sub_iter += 1
                        empty_from_coll.append(empty_parent)
            iter += 1 
        
        #print(coll_relation)
        
        ## create dictionnary : keys = collection, values = objects in collection)
        obj_in_col = {}
        for coll in bpy.data.collections:
            if coll != empties_storage_coll :
                coll_name = coll.name_full
                for obj in coll.objects:
                    obj_in_col[coll_name] = coll.objects.keys()
        
        # deselect all in scene  
        bpy.ops.object.select_all(action='DESELECT')
        
        # variables list col/obj
        iter = 0
        coll_list = list(obj_in_col.keys())
        obj_list = list(obj_in_col.values())
        values_obj_length = len(obj_in_col.values())
        
        # put meshes under right empties
        for value in obj_in_col.values():
            if iter + 1 <= values_obj_length:
                if debug_mode == True:
                    print(str(obj_list[iter]) + ' >>> ' + 'length : ' + str(len(obj_list[iter])))
                sub_iter = 0
                while sub_iter + 1 <= len(obj_list[iter]):
                    obj_parent = bpy.data.objects[coll_list[iter]]
                    obj_child = bpy.data.objects[obj_list[iter][sub_iter]]
                    if obj_child not in empties_list and obj_child != obj_parent:
                        obj_child.parent = obj_parent
                    sub_iter += 1
            iter += 1 
        
        # remove unuseful objects ('None' and 'SELECT_hierarchy')
        for obj in bpy.data.objects:
            if obj.name.find('None') != -1 and obj.type == 'EMPTY':
                bpy.data.objects.remove(bpy.data.objects['None'], do_unlink=True)
        for obj in bpy.data.objects:
            if obj.name.find(empties_storage_coll.name) != -1 and obj.type == 'EMPTY':
                bpy.data.objects.remove(bpy.data.objects[obj.name], do_unlink=True)
        for obj in bpy.data.objects:
            if len(obj.children) is 0 and obj.type == 'EMPTY':
                bpy.data.objects.remove(bpy.data.objects[obj.name], do_unlink=True)
        
        #put cursor in the same place it was before
        bpy.context.scene.cursor.location = cursor_loc
        bpy.context.scene.cursor.rotation_euler = cursor_rot
        
        if debug_mode == True:
            print('coll_in_scene: \n >>> ' + str(coll_in_scene_list))
            print('collection relation (keys: parent collection, values: Children collections) : \n >>> ' + str(coll_relation))
            print('list of empties created = collections in scene : \n >>> ' + str(empties_list))
            print('list of objects in collections (keys: collection parent, value: objects in the parent collection) : \n >>> ' + str(obj_in_col))
            print('>>>> items in obj in col : \n >>> ' + str(values_obj_length))         
                   
        print(f"{Addon_Name} (collections to empties) done on : {str(coll_in_scene_list)} \n")
        print(f"\n {separator} {Addon_Name} (collections to empties) Finished {separator} \n")

        return {"FINISHED"}


# list all classes
classes = (
    HIERTOCOL_properties,
    OBJECT_PT_hiertocolpanelall,
    OBJECT_PT_hiertocolpanelAdvanced,
    OBJECT_OT_hiertocolemptiestocollections,
    OBJECT_OT_hiertocolcollectionstoempties,
    )

# register classes
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.hiertocol_props = bpy.props.PointerProperty (type = HIERTOCOL_properties)

#unregister classes 
def unregister():    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.hiertocol_props
        

## todo
# select root element > select hierarchy
# EmptiesHierarchy > out of the root collection