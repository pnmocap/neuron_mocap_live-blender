import bpy

class MarkTPose(bpy.types.Operator):
    bl_idname = 'neuron_mocap_live.mark_tpose'
    bl_label = 'Set as T-Pose'

    def execute(self, ctx):
        for bone in ctx.active_object.pose.bones:
            bone.nml_matrix_basis_tpose[0:4] = bone.matrix_basis.row[0]
            bone.nml_matrix_basis_tpose[4:8] = bone.matrix_basis.row[1]
            bone.nml_matrix_basis_tpose[8:12] = bone.matrix_basis.row[2]
            bone.nml_matrix_basis_tpose[12:16] = bone.matrix_basis.row[3]

            bone.nml_matrix_tpose[0:4] = bone.matrix.row[0]
            bone.nml_matrix_tpose[4:8] = bone.matrix.row[1]
            bone.nml_matrix_tpose[8:12] = bone.matrix.row[2]
            bone.nml_matrix_tpose[12:16] = bone.matrix.row[3]

        ctx.active_object.nml_tpose_marked = True
        return {'FINISHED'}

class SetTPose(bpy.types.Operator):
    bl_idname = 'neuron_mocap_live.set_tpose'
    bl_label = 'Set T-Pose'

    def execute(self, ctx):
        if ctx.active_object.nml_tpose_marked:
            for bone in ctx.active_object.pose.bones:
                m = bone.matrix_basis.copy()
                m[0][0:4] = bone.nml_matrix_basis_tpose[0:4]
                m[1][0:4] = bone.nml_matrix_basis_tpose[4:8]
                m[2][0:4] = bone.nml_matrix_basis_tpose[8:12]
                m[3][0:4] = bone.nml_matrix_basis_tpose[12:16]
                bone.matrix_basis = m
        else:
            self.report(type = {'ERROR'}, message = 'T-Pose is not marked')

        return {'FINISHED'}