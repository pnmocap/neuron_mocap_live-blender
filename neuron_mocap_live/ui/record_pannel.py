import bpy

class RecordPanel(bpy.types.Panel):
    bl_idname = 'NOITOM_PT_RecordPanel'
    bl_label = 'Record'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Neuron Mocap"

    @classmethod
    def poll(cls, ctx):
        return ctx.scene.neuron_mocap_live_living

    def draw(self, ctx):
        layout = self.layout
        col = layout.column()

        if not ctx.scene.neuron_mocap_live_recording:
            row = col.row(align=True)
            row.operator('neuron_mocap_live.start_record')
        else:
            row = col.row(align=True)
            row.operator('neuron_mocap_live.stop_record')