import bpy

class MarkTPose(bpy.types.Operator):
    bl_idname = 'neuron_mocap_live.mark_tpose'
    bl_label = 'Set as T-Pose'

    def execute(self, ctx):
        for bone in ctx.active_object.pose.bones:
            matrix_basis_tpose = bone.matrix_basis
            bone.nml_set_matrix_basis_tpose(matrix_basis_tpose)

            matrix_world_tpose = bone.matrix @ ctx.active_object.matrix_world
            bone.nml_set_matrix_world_tpose(matrix_world_tpose)

            matrix_to_world = (bone.matrix.to_3x3().inverted() @ ctx.active_object.matrix_world.to_3x3().inverted()).to_4x4()
            bone.nml_set_matrix_to_world(matrix_to_world)
            
            bone.nml_set_matrix_from_world(matrix_to_world.inverted())
            scale = matrix_world_tpose.to_scale()
            bone.nml_scale_world = scale
            bone.nml_translation_world = matrix_world_tpose.to_quaternion() @ (matrix_world_tpose.to_translation() * scale)

        ctx.active_object.nml_tpose_marked = True
        return {'FINISHED'}

class SetTPose(bpy.types.Operator):
    bl_idname = 'neuron_mocap_live.set_tpose'
    bl_label = 'Set T-Pose'

    @classmethod
    def poll(cls, ctx):
        return ctx.active_object.nml_tpose_marked

    def execute(self, ctx):
        if ctx.active_object.nml_tpose_marked:
            for bone in ctx.active_object.pose.bones:
                bone.matrix_basis = bone.nml_get_matrix_basis_tpose()
        else:
            self.report(type = {'ERROR'}, message = 'T-Pose is not marked')

        return {'FINISHED'}