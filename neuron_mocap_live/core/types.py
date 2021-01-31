import bpy

def register_types():
    bpy.types.Scene.nml_protocol = bpy.props.EnumProperty(
        items = [('TCP', 'TCP', '', 1), ('UDP', 'UDP', '', 2)], 
        name = 'Protocol',
        default = 'UDP'
    )

    bpy.types.Scene.nml_ip = bpy.props.StringProperty(
        name = 'IP', 
        default = '127.0.0.1'
    )

    bpy.types.Scene.nml_port = bpy.props.IntProperty(
        name = 'Port',
        default = 7001,
        max = 65535,
        min = 0
    )

    bpy.types.Scene.nml_living = bpy.props.BoolProperty(
        name = 'Living',
        default = False
    )

    bpy.types.Object.nml_active = bpy.props.BoolProperty(
        name = 'Live',
        default = False
    )

    bpy.types.Object.nml_chr_name = bpy.props.StringProperty(
        name = 'Character'
    )

    bpy.types.Scene.nml_recording = bpy.props.BoolProperty(
        name = 'Recording',
        default = False
    )

    bpy.types.Object.nml_drive_type = bpy.props.EnumProperty(
        items = [('DIRECT', 'Direct', '', 1), ('RETARGET', 'Retarget', '', 2)],
        name = 'Drive Type',
        default = 'DIRECT'
    )

    # retarget source
    bpy.types.Object.nml_source_armature = bpy.props.StringProperty(
        name = 'Armature Source'
    )

    bpy.types.PoseBone.nml_source_bone = bpy.props.StringProperty(
        name = 'Bone Source'
    )

    bpy.types.Object.nml_tpose_marked = bpy.props.BoolProperty(
        name = 'T-Pose Marked'
    )

    bpy.types.PoseBone.nml_matrix_tpose = bpy.props.FloatVectorProperty(
        name = 'T-Pose Matrix',
        size = 16,
        default = (
            1, 0, 0, 0, 
            0, 1, 0, 0, 
            0, 0, 1, 0, 
            0, 0, 0, 1)
    )

    bpy.types.PoseBone.nml_matrix_basis_tpose = bpy.props.FloatVectorProperty(
        name = 'T-Pose Matrix Basis',
        size = 16,
        default = (
            1, 0, 0, 0, 
            0, 1, 0, 0, 
            0, 0, 1, 0, 
            0, 0, 0, 1)
    )
    