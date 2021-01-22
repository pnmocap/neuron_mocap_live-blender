import bpy

class ConnectionPanel(bpy.types.Panel):
    bl_idname = 'NOITOM_PT_ConnectionPanel'
    bl_label = 'Connection'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Neuron Mocap"

    def draw(self, ctx):
        layout = self.layout
        col = layout.column()

        if not ctx.scene.neuron_mocap_live_living:
            row = col.row(align=True)
            row.label(text = 'Protocol')
            row.prop(ctx.scene, 'neuron_mocap_live_protocol', text = '')

            if ctx.scene.neuron_mocap_live_protocol == 'TCP':
                row = col.row(align=True)
                row.label(text = 'IP')
                row.prop(ctx.scene, 'neuron_mocap_live_ip', text = '')

            row = col.row(align=True)
            row.label(text = 'Port')
            row.prop(ctx.scene, 'neuron_mocap_live_port', text = '')

            row = col.row(align=True)
            row.operator('neuron_mocap_live.connect')
        else:
            row = col.row(align=True)
            row.label(text = 'Protocol')
            row.label(text = ctx.scene.neuron_mocap_live_protocol)

            if ctx.scene.neuron_mocap_live_protocol == 'TCP':
                row = col.row(align=True)
                row.label(text = 'IP')
                row.label(text = ctx.scene.neuron_mocap_live_ip)

            row = col.row(align=True)
            row.label(text = 'Port')
            row.label(text = str(ctx.scene.neuron_mocap_live_port))

            if not ctx.scene.neuron_mocap_live_recording:
                row = col.row(align=True)
                row.operator('neuron_mocap_live.disconnect')