import bpy

class ArmaturePropertyPanel(bpy.types.Panel):
    bl_idname = 'NOITOM_PT_ArmaturePropertyPanel'
    bl_label = 'Armature'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Neuron Mocap"

    @classmethod
    def poll(cls, ctx):
        return ctx.active_object != None and ctx.active_object.type == 'ARMATURE'

    def draw(self, ctx):
        layout = self.layout
        col = layout.column()

        if ctx.scene.neuron_mocap_live_recording:
            row = col.row(align = True)
            row.label(text='Character Name')
            row.label(text=ctx.active_object.neuron_mocap_live_chr_name)
        else:
            row = col.row(align = True)
            row.label(text='Live')
            row.prop(ctx.active_object, 'neuron_mocap_live_active', text = '')

            row = col.row(align = True)
            row.label(text='Character Name')
            row.prop(ctx.active_object, 'neuron_mocap_live_chr_name', text = '')