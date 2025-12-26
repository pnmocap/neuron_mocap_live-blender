import bpy
from mathutils import Matrix, Vector

def register_types():
    bpy.types.Scene.nml_server = bpy.props.EnumProperty(
        items = [('Axis Studio', 'Axis Studio', '', 1), ('Axis Neuron / Pro', 'Axis Neruon / Pro', '', 2)], 
        name = 'Server',
        default = 'Axis Studio'
    )

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

    bpy.types.PoseBone.nml_matrix_calculated = bpy.props.BoolProperty()

    def nml_encode_matrix(self, v16, m4x4):
        v16[0:4] = m4x4.row[0]
        v16[4:8] = m4x4.row[1]
        v16[8:12] = m4x4.row[2]
        v16[12:16] = m4x4.row[3]
    bpy.types.PoseBone.nml_encode_matrix = nml_encode_matrix

    def nml_decode_matrix(self, v16, m4x4):
        m4x4.row[0] = v16[0:4]
        m4x4.row[1] = v16[4:8]
        m4x4.row[2] = v16[8:12]
        m4x4.row[3] = v16[12:16]
    bpy.types.PoseBone.nml_decode_matrix = nml_decode_matrix

    bpy.types.PoseBone.nml_matrix_world_tpose = bpy.props.FloatVectorProperty(
        size = 16,
        default = (
            1, 0, 0, 0, 
            0, 1, 0, 0, 
            0, 0, 1, 0, 
            0, 0, 0, 1)
    )

    def nml_set_matrix_world_tpose(self, m):
        self.nml_encode_matrix(self.nml_matrix_world_tpose, m)
    bpy.types.PoseBone.nml_set_matrix_world_tpose = nml_set_matrix_world_tpose

    def nml_get_matrix_world_tpose(self):
        m = Matrix.Identity(4)
        self.nml_decode_matrix(self.nml_matrix_world_tpose, m)
        return m
    bpy.types.PoseBone.nml_get_matrix_world_tpose = nml_get_matrix_world_tpose

    bpy.types.PoseBone.nml_matrix_basis_tpose = bpy.props.FloatVectorProperty(
        size = 16,
        default = (
            1, 0, 0, 0, 
            0, 1, 0, 0, 
            0, 0, 1, 0, 
            0, 0, 0, 1)
    )
    
    def nml_set_matrix_basis_tpose(self, m):
        self.nml_encode_matrix(self.nml_matrix_basis_tpose, m)
    bpy.types.PoseBone.nml_set_matrix_basis_tpose = nml_set_matrix_basis_tpose

    def nml_get_matrix_basis_tpose(self):
        m = Matrix.Identity(4)
        self.nml_decode_matrix(self.nml_matrix_basis_tpose, m)
        return m
    bpy.types.PoseBone.nml_get_matrix_basis_tpose = nml_get_matrix_basis_tpose

    bpy.types.PoseBone.nml_matrix_to_world = bpy.props.FloatVectorProperty(
        size = 16,
        default = (
            1, 0, 0, 0, 
            0, 1, 0, 0, 
            0, 0, 1, 0, 
            0, 0, 0, 1)
    )
    
    def nml_set_matrix_to_world(self, m):
        self.nml_encode_matrix(self.nml_matrix_to_world, m)
    bpy.types.PoseBone.nml_set_matrix_to_world = nml_set_matrix_to_world

    def nml_get_matrix_to_world(self):
        m = Matrix.Identity(4)
        self.nml_decode_matrix(self.nml_matrix_to_world, m)
        return m
    bpy.types.PoseBone.nml_get_matrix_to_world = nml_get_matrix_to_world

    bpy.types.PoseBone.nml_matrix_from_world = bpy.props.FloatVectorProperty(
        size = 16,
        default = (
            1, 0, 0, 0, 
            0, 1, 0, 0, 
            0, 0, 1, 0, 
            0, 0, 0, 1)
    )
    
    def nml_set_matrix_from_world(self, m):
        self.nml_encode_matrix(self.nml_matrix_from_world, m)
    bpy.types.PoseBone.nml_set_matrix_from_world = nml_set_matrix_from_world

    def nml_get_matrix_from_world(self):
        m = Matrix.Identity(4)
        self.nml_decode_matrix(self.nml_matrix_from_world, m)
        return m
    bpy.types.PoseBone.nml_get_matrix_from_world = nml_get_matrix_from_world

    bpy.types.PoseBone.nml_scale_world = bpy.props.FloatVectorProperty(
        size = 3,
        default = (
            1, 1, 1
        )
    )

    def nml_set_scale_world(self, v3):
        self.nml_scale_world[0:3] = v3[0:3]
    bpy.types.PoseBone.nml_set_scale_world = nml_set_scale_world

    def nml_get_scale_world(self):
        v3 = Vector()
        v3[0:3] = self.nml_scale_world[0:3]
        return v3
    bpy.types.PoseBone.nml_get_scale_world = nml_get_scale_world

    bpy.types.PoseBone.nml_translation_world = bpy.props.FloatVectorProperty(
        size = 3,
        default = (
            0, 0, 0
        )
    )

    def nml_set_translation_world(self, v3):
        self.nml_translation_world[0:3] = v3[0:3]
    bpy.types.PoseBone.nml_set_translation_world = nml_set_translation_world

    def nml_get_translation_world(self):
        v3 = Vector()
        v3[0:3] = self.nml_translation_world[0:3]
        return v3
    bpy.types.PoseBone.nml_get_translation_world = nml_get_translation_world