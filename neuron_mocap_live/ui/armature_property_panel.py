import bpy

class ArmaturePropertyPanel(bpy.types.Panel):
    bl_idname = 'NOITOM_PT_ArmaturePropertyPanel'
    bl_label = 'Armature'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "NEURON MOCAP"

    @classmethod
    def poll(cls, ctx):
        return ctx.active_object != None and ctx.active_object.type == 'ARMATURE'

    def draw(self, ctx):
        layout = self.layout
        col = layout.column()
        row = col.row(align=True)

        if ctx.scene.nml_recording:
            row.label(text = 'Drive Type')
            row.label(text = ctx.active_object.nml_drive_type)
        else:
            row.label(text = 'Drive Type')
            row.prop(ctx.active_object, 'nml_drive_type', text = '')

        if ctx.active_object.nml_drive_type == 'DIRECT':
            self.draw_direct_drive_settings(ctx)
        else:
            self.draw_retarget_drive_settings(ctx)


    def draw_direct_drive_settings(self, ctx):
        layout = self.layout
        col = layout.column()

        if ctx.scene.nml_recording:
            row = col.row(align = True)
            row.label(text='Character Name')
            row.label(text=ctx.active_object.nml_chr_name)
        else:
            row = col.row(align = True)
            row.label(text='Live')
            row.prop(ctx.active_object, 'nml_active', text = '')

            row = col.row(align = True)
            row.label(text='Character Name')
            row.prop(ctx.active_object, 'nml_chr_name', text = '')

    def draw_retarget_drive_settings(self, ctx):
        layout = self.layout
        col = layout.column()

        row = col.row(align = True)
        row.label(text='Live')
        row.prop(ctx.active_object, 'nml_active', text = '')

        row = col.row(align = True)
        row.operator('neuron_mocap_live.mark_tpose', text = 'Mark T-Pose', icon='OUTLINER_DATA_ARMATURE')
        row.operator('neuron_mocap_live.set_tpose', text = 'Set T-Pose', icon='ARMATURE_DATA')

        if not ctx.active_object.nml_tpose_marked:
            row = col.row(align = True)
            row.label(text="Mark T-Pose is required", icon='ERROR')

        row = col.row()
        row.label(text='Source')
        row.prop_search(ctx.active_object, 'nml_source_armature', ctx.scene, 'objects', text='')

        source = bpy.data.objects.get(ctx.active_object.nml_source_armature)
        if source and source.type == 'ARMATURE':
            col = layout.column()
            row = col.row()
            row.operator('neuron_mocap_live.auto_map_bone', text = 'Auto Detect', icon='BONE_DATA')
            row = col.row()
            row.operator('neuron_mocap_live.clear_bone_map', text = 'Clear', icon='PANEL_CLOSE')
            row = col.row()
            row.operator('neuron_mocap_live.load_bone_map', text = 'Load', icon='FILEBROWSER')
            row = col.row()
            row.operator('neuron_mocap_live.save_bone_map', text = 'Save', icon='FILE_TICK')

            for bone in ctx.active_object.pose.bones:
                row = col.row()
                row.label(text = bone.name)
                row.prop_search(bone, 'nml_source_bone', source.pose, 'bones', text='')