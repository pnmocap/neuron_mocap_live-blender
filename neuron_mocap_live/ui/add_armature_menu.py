import bpy

def draw_add_armature_menu(self, ctx):
    layout = self.layout
    layout.separator()
    layout.operator('neuron_mocap_live.add_pns_armature', text='Noitom PNS Armature', icon='OUTLINER_OB_ARMATURE')
    layout.operator('neuron_mocap_live.add_pns_thumb_open_armature', text='Noitom PNS(Thumb open) Armature', icon='OUTLINER_OB_ARMATURE')
    layout.operator('neuron_mocap_live.add_pn_pro_armature', text='Noitom PN Pro Armature', icon='OUTLINER_OB_ARMATURE')
