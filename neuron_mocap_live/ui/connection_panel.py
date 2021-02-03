import bpy

class ConnectionPanel(bpy.types.Panel):
    bl_idname = 'NOITOM_PT_ConnectionPanel'
    bl_label = 'Connection'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "NEURON MOCAP"

    def draw(self, ctx):
        layout = self.layout
        col = layout.column()

        if not ctx.scene.nml_living:
            row = col.row(align=True)
            row.label(text = 'Server')
            row.prop(ctx.scene, 'nml_server', text = '')

            row = col.row(align=True)
            row.label(text = 'Protocol')
            row.prop(ctx.scene, 'nml_protocol', text = '')

            if ctx.scene.nml_protocol == 'TCP':
                row = col.row(align=True)
                row.label(text = 'IP')
                row.prop(ctx.scene, 'nml_ip', text = '')

            row = col.row(align=True)
            row.label(text = 'Port')
            row.prop(ctx.scene, 'nml_port', text = '')

            row = col.row(align=True)
            row.operator('neuron_mocap_live.connect', icon='URL')
        else:
            row = col.row(align=True)
            row.label(text = 'Server')
            row.label(text = ctx.scene.nml_server)

            row = col.row(align=True)
            row.label(text = 'Protocol')
            row.label(text = ctx.scene.nml_protocol)

            if ctx.scene.nml_protocol == 'TCP':
                row = col.row(align=True)
                row.label(text = 'IP')
                row.label(text = ctx.scene.nml_ip)

            row = col.row(align=True)
            row.label(text = 'Port')
            row.label(text = str(ctx.scene.nml_port))

            if not ctx.scene.nml_recording:
                row = col.row(align=True)
                row.operator('neuron_mocap_live.disconnect', icon='MOD_WAVE')