import bpy
from . import core
from . import ops
from . import ui

bl_info = {
    "name" : "Neuron Mocap Live",
    "author" : "Noitom",
    "description" : "",
    "blender" : (2, 80, 0),
    "version" : (1, 0, 0),
    "location" : "",
    "warning" : "",
    "category" : "Noitom"
}

class_list = [
    ops.AddPNSArmature,
    ops.AddPNSThumbOpenArmature,
    ops.AddPNProArmature,
    ops.MocapConnect,
    ops.MocapDisconnect,
    ops.MocapStartRecord,
    ops.MocapStopRecord,
    ui.ConnectionPanel,
    ui.ArmaturePropertyPanel,
    ui.RecordPanel
]

def register():
    core.register_types()

    for item in class_list:
        bpy.utils.register_class(item)

    bpy.types.VIEW3D_MT_add.append(ui.draw_add_armature_menu)

def unregister():
    for item in class_list:
        bpy.utils.unregister_class(item)

    bpy.types.VIEW3D_MT_add.remove(ui.draw_add_armature_menu)
