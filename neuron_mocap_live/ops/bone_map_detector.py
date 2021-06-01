import bpy

class AutoMapBone(bpy.types.Operator):
    bl_idname = 'neuron_mocap_live.auto_map_bone'
    bl_label = 'Auto Map Bone'

    @classmethod
    def poll(cls, ctx):
        return bpy.data.objects.get(ctx.active_object.nml_source_armature) != None

    def execute(self, ctx):
        bones = ctx.active_object.pose.bones
        source_bones = bpy.data.objects.get(ctx.active_object.nml_source_armature).pose.bones
        for bone in bones:
            for source_bone in source_bones:
                if bone.name.endswith(source_bone.name):
                    bone.nml_source_bone = source_bone.name

        return {'FINISHED'}

class ClearBoneMap(bpy.types.Operator):
    bl_idname = 'neuron_mocap_live.clear_bone_map'
    bl_label = 'Clear Bone Map'

    @classmethod
    def poll(cls, ctx):
        return bpy.data.objects.get(ctx.active_object.nml_source_armature) != None

    def execute(self, ctx):
        bones = ctx.active_object.pose.bones
        source_bones = bpy.data.objects.get(ctx.active_object.nml_source_armature).pose.bones
        for bone in bones:
            bone.nml_source_bone = str()

        return {'FINISHED'}