import bpy
from .. utils.registration import get_prefs



# MACHIN3tools SUB MENU

class MenuMACHIN3toolsObjectContextMenu(bpy.types.Menu):
    bl_idname = "MACHIN3_MT_machin3tools_object_context_menu"
    bl_label = "MACHIN3tools"

    def draw(self, context):
        layout = self.layout

        if get_prefs().activate_mirror:
            layout.operator("machin3.unmirror", text="Un-Mirror")

        if get_prefs().activate_select:
            layout.operator("machin3.select_center_objects", text="Select Center Objects")
            layout.operator("machin3.select_wire_objects", text="Select Wire Objects")

        if get_prefs().activate_apply:
            layout.operator("machin3.apply_transformations", text="Apply Transformations")

        if get_prefs().activate_mesh_cut:
            layout.operator("machin3.mesh_cut", text="Mesh Cut")

        if get_prefs().activate_material_picker:
            layout.operator("machin3.material_picker", text="Material Picker")


# AppendMaterilas SUB MENU

class MenuAppendMaterials(bpy.types.Menu):
    bl_idname = "MACHIN3_MT_append_materials"
    bl_label = "Append Materials"

    def draw(self, context):
        layout = self.layout

        names = [mat.name for mat in get_prefs().appendmats]

        if names:
            names.insert(0, "ALL")
        else:
            layout.label(text="No Materials added yet!", icon="ERROR")
            layout.label(text="Check MACHIN3tools prefs.", icon="INFO")


        for name in names:
            layout.operator_context = 'INVOKE_DEFAULT'

            if name == "ALL":
                layout.operator("machin3.append_material", text=name, icon="MATERIAL_DATA").name = name
                layout.separator()

            elif name == "---":
                layout.separator()

            else:
                mat = bpy.data.materials.get(name)
                icon_val = layout.icon(mat) if mat else 0

                layout.operator("machin3.append_material", text=name, icon_value=icon_val).name = name


# Group SUB MENU

def get_group_polls(context):
    active_group = bool(context.active_object if context.active_object and context.active_object.M3.is_group_empty and context.active_object.select_get() else None)
    active_child = bool(context.active_object if context.active_object and context.active_object.M3.is_group_object and context.active_object.select_get() else None)
    group_empties = bool([obj for obj in context.visible_objects if obj.M3.is_group_empty])
    groupable = bool(len([obj for obj in context.selected_objects if not obj.parent]) > 1)
    regroupable = bool(len([obj for obj in context.selected_objects if obj.M3.is_group_object]) > 1)
    ungroupable = bool([obj for obj in context.selected_objects if obj.M3.is_group_empty]) if group_empties else False
    addable = bool([obj for obj in context.selected_objects if not obj.M3.is_group_object and not obj.parent and not obj == active_group and not obj == active_child])
    removable = bool([obj for obj in context.selected_objects if obj.M3.is_group_object])
    selectable = bool([obj for obj in context.selected_objects if obj.M3.is_group_empty or obj.M3.is_group_object])
    duplicatable = bool([obj for obj in context.selected_objects if obj.M3.is_group_empty])
    groupifyable = bool([obj for obj in context.selected_objects if obj.type == 'EMPTY' and not obj.M3.is_group_empty and obj.children])

    return active_group, active_child, group_empties, groupable, regroupable, ungroupable, addable, removable, selectable, duplicatable, groupifyable


class MenuGroupObjectContextMenu(bpy.types.Menu):
    bl_idname = "MACHIN3_MT_group_object_context_menu"
    bl_label = "Group"

    def draw(self, context):
        layout = self.layout

        active_group, active_child, group_empties, groupable, regroupable, ungroupable, addable, removable, selectable, duplicatable, groupifyable = get_group_polls(context)


        # SCENE PROPS

        row = layout.row()
        row.active = group_empties
        row.prop(context.scene.M3, "group_select")

        row = layout.row()
        row.active = group_empties
        row.prop(context.scene.M3, "group_hide")

        layout.separator()


        # CREATE / DESTRUCT

        row = layout.row()
        row.active = groupable
        row.operator("machin3.group", text="Group")

        row = layout.row()
        row.active = regroupable
        row.operator("machin3.regroup", text="Re-Group")

        row = layout.row()
        row.active = ungroupable
        row.operator("machin3.ungroup", text="Un-Group")

        row = layout.row()
        row.active = groupifyable
        layout.operator("machin3.groupify", text="Groupify")

        layout.separator()


        # SELECT / DUPLICATE

        row = layout.row()
        row.active = selectable
        row.operator("machin3.select_group", text="Select Group")

        row = layout.row()
        row.active = duplicatable
        row.operator("machin3.duplicate_group", text="Duplicate Group")

        layout.separator()


        # ADD / REMOVE

        row = layout.row()
        row.active = addable and (active_group or active_child)
        row.operator("machin3.add_to_group", text="Add to Group")

        row = layout.row()
        row.active = removable
        row.operator("machin3.remove_from_group", text="Remove from Group")


# OBJECT CONTEXT MENU

def object_context_menu(self, context):
    layout = self.layout

    if get_prefs().activate_object_context_menu:
        layout.menu("MACHIN3_MT_machin3tools_object_context_menu")
        layout.separator()

    if get_prefs().activate_group:

        if get_prefs().use_group_sub_menu:
            layout.menu("MACHIN3_MT_group_object_context_menu")
            layout.separator()

        else:
            active_group, active_child, group_empties, groupable, regroupable, ungroupable, addable, removable, selectable, duplicatable, groupifyable = get_group_polls(context)


            # SCENE PROPS

            if group_empties:
                layout.prop(context.scene.M3, "group_select")
                layout.prop(context.scene.M3, "group_hide")

                if groupable or group_empties or selectable or duplicatable or groupifyable or (addable and (active_group or active_child)) or removable:

                    # custom spacer
                    row = layout.row()
                    row.scale_y = 0.3
                    row.label(text="")


            # GROUP

            if groupable:
                layout.operator("machin3.group", text="Group")

            # RE-GROUP

            if regroupable:
                layout.operator("machin3.regroup", text="Re-Group")


            # UN-GROUP

            if ungroupable:
                # set op context
                # NOTE: why the the op context necessary here, and not in the MACHIN3tools sub menu?
                # ####: looks like the menue is automatically INVOKE_REGION_WIN for some reason
                layout.operator_context = "INVOKE_REGION_WIN"

                layout.operator("machin3.ungroup", text="Un-Group")

                # reset op context just to be sure
                layout.operator_context = "EXEC_REGION_WIN"


            # GROUPIFY

            if groupifyable:
                layout.operator("machin3.groupify", text="Groupify")


            # SELECT

            if selectable:
                # custom spacer
                row = layout.row()
                row.scale_y = 0.3
                row.label(text="")

                layout.operator_context = "INVOKE_REGION_WIN"
                layout.operator("machin3.select_group", text="Select Group")
                layout.operator_context = "EXEC_REGION_WIN"

            if duplicatable:

                if not selectable:
                    # custom spacer
                    row = layout.row()
                    row.scale_y = 0.3
                    row.label(text="")

                layout.operator_context = "INVOKE_REGION_WIN"
                layout.operator("machin3.duplicate_group", text="Duplicate Group")
                layout.operator_context = "EXEC_REGION_WIN"


            # ADD and REMOVE

            if (addable and (active_group or active_child)) or removable:

                # custom spacer
                row = layout.row()
                row.scale_y = 0.3
                row.label(text="")

                if addable and (active_group or active_child):
                    layout.operator("machin3.add_to_group", text="Add to Group")

                if removable:
                    layout.operator("machin3.remove_from_group", text="Remove from Group")

            if group_empties or groupable or (addable and (active_group or active_child)) or removable or groupifyable:
                layout.separator()


# ADD OBJECTS MENU

def add_object_buttons(self, context):
    self.layout.operator("machin3.quadsphere", text="Quad Sphere", icon='SPHERE')


# MATERIAL PICKER HEADER

def material_pick_button(self, context):
    workspaces = [ws.strip() for ws in get_prefs().matpick_workspace_names.split(',')]

    if any([s in context.workspace.name for s in workspaces]):
        if getattr(bpy.types, 'MACHIN3_OT_material_picker', False):
            row = self.layout.row()
            row.scale_x = 1.25
            row.scale_y = 1.1
            # row.separator_spacer()
            row.separator(factor=get_prefs().matpick_spacing_obj if context.mode == 'OBJECT' else get_prefs().matpick_spacing_edit)
            row.operator("machin3.material_picker", text="", icon="EYEDROPPER")
