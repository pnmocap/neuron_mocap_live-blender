import bpy

class RecordPanel(bpy.types.Panel):
    bl_idname = 'NOITOM_PT_RecordPanel'
    bl_label = 'Record'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "NEURON MOCAP"

    @classmethod
    def poll(cls, ctx):
        return ctx.scene.nml_living

    def draw(self, ctx):
        layout = self.layout
        col = layout.column()

        if not ctx.scene.nml_recording:
            row = col.row(align=True)
            row.operator('neuron_mocap_live.start_record', icon='REC')
        else:
            row = col.row(align=True)
            row.operator('neuron_mocap_live.stop_record', icon='REC', depress=True)