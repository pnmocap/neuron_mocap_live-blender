import bpy

def register_types():
    bpy.types.Scene.neuron_mocap_live_protocol = bpy.props.EnumProperty(
        items = [('TCP', 'TCP', '', 1), ('UDP', 'UDP', '', 2)], 
        name = 'Protocol',
        default = 'UDP'
    )

    bpy.types.Scene.neuron_mocap_live_ip = bpy.props.StringProperty(
        name = 'IP', 
        default = '127.0.0.1'
    )

    bpy.types.Scene.neuron_mocap_live_port = bpy.props.IntProperty(
        name = 'Port',
        default = 7001,
        max = 65535,
        min = 0
    )

    bpy.types.Scene.neuron_mocap_live_living = bpy.props.BoolProperty(
        name = 'Living',
        default = False
    )

    bpy.types.Object.neuron_mocap_live_active = bpy.props.BoolProperty(
        name = 'Live',
        default = False
    )

    bpy.types.Object.neuron_mocap_live_chr_name = bpy.props.StringProperty(
        name = 'Character'
    )

    bpy.types.Scene.neuron_mocap_live_recording = bpy.props.BoolProperty(
        name = 'Recording',
        default = False
    )
    