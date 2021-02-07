import bpy

def draw_add_armature_menu(self, ctx):
    layout = self.layout
    layout.separator()
    layout.operator('neuron_mocap_live.add_pns_armature', text='Axis Studio Armature', icon='OUTLINER_OB_ARMATURE')
    layout.operator('neuron_mocap_live.add_pns_thumb_open_armature', text='Axis Studio(Thumb open) Armature', icon='OUTLINER_OB_ARMATURE')
    layout.operator('neuron_mocap_live.add_pn_pro_armature', text='Axis Legacy Armature', icon='OUTLINER_OB_ARMATURE')
