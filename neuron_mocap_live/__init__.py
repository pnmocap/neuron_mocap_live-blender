import bpy
from . import core
from . import ops
from . import ui

bl_info = {
    "name" : "NEURON MOCAP LIVE",
    "author" : "Noitom",
    "description" : "",
    "blender" : (2, 80, 0),
    "version" : (1, 0, '2 (BETA)'),
    "location" : "",
    "warning" : "",
    "doc_url" : "https://github.com/pnmocap/neuron_mocap_live-blender",
    "tracker_url" : "https://github.com/pnmocap/neuron_mocap_live-blender/issues",
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
    ops.MarkTPose,
    ops.SetTPose,
    ops.AutoMapBone,
    ops.ClearBoneMap,
    ops.LoadBoneMap,
    ops.SaveBoneMap,
    ui.ConnectionPanel,
    ui.RecordPanel,
    ui.ArmaturePropertyPanel
]

def register():
    ops.init_mocap_api()

    core.register_types()

    for item in class_list:
        bpy.utils.register_class(item)

    bpy.types.VIEW3D_MT_add.append(ui.draw_add_armature_menu)

def unregister():
    for item in class_list:
        bpy.utils.unregister_class(item)

    bpy.types.VIEW3D_MT_add.remove(ui.draw_add_armature_menu)

    ops.uninit_mocap_api()
