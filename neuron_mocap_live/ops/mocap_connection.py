import bpy
from mathutils import Vector, Matrix, Quaternion, Euler
from ..mocap_api import *
import math

mocap_app = MCPApplication()
render_settings = MCPRenderSettings()
render_settings.set_up_vector(MCPUpVector.ZAxis, 1)
render_settings.set_coord_system(MCPCoordSystem.RightHanded)
render_settings.set_front_vector(MCPFrontVector.ParityEven, -1)
render_settings.set_rotating_direction(MCPRotatingDirection.CounterClockwise)
render_settings.set_unit(MCPUnit.Meter)
mocap_app.set_render_settings(render_settings)

mocap_timer = None

# {key:object_name, value:{key:bone_name, value:[(time_delta, location, rotation_quaternion, scale)]}}
record_data = None

def animate_bone(ctx, obj, parent_global_position, parent_rest_matrix_inv, parent_scalable, joint):
    obj_matrix = obj.matrix_world
    parent_scale = Vector((1, 1, 1))
    pose_bone = obj.pose.bones.get(joint.get_name())
    rest_matrix = Matrix()
    rest_matrix_inv = Matrix()

    if pose_bone != None:
        bone = obj.data.bones.get(joint.get_name())
        bone.inherit_scale = 'NONE'

        rest_matrix = obj_matrix @ bone.matrix_local
        rest_matrix_inv = Matrix(rest_matrix).to_3x3()
        rest_matrix_inv.invert()
        rest_matrix_inv.resize_4x4()

        location = joint.get_local_position()
        if location:
            location_in_parent_coord = parent_rest_matrix_inv @ Vector(location)
            location = rest_matrix_inv @ Vector(location)

            ofs = rest_matrix.to_translation() - parent_global_position
            ofs_in_parent_coord = parent_rest_matrix_inv @ ofs
            ofs = rest_matrix_inv @ ofs

            if pose_bone.parent and parent_scalable:
                for i in range(3):
                    if not math.isclose(ofs_in_parent_coord[i], 0, abs_tol=1e-4):
                        parent_scale[i] = location_in_parent_coord[i] / ofs_in_parent_coord[i]
                    scale = 1
                    if not math.isclose(ofs[i], 0, abs_tol=1e-4):
                        scale = location[i] / ofs[i]
                    if not pose_bone.parent.lock_scale[i]:
                        location[i] = location[i] - ofs[i] * scale
            else:
                location = location - ofs

            for i in range(3):
                if not pose_bone.lock_location[i]:
                    pose_bone.location[i] = location[i]

        if pose_bone.rotation_mode != 'QUATERNION':
            pose_bone.rotation_mode = 'QUATERNION'

        rot_matrix = Quaternion(joint.get_local_rotation()).to_matrix()
        rot_matrix.resize_4x4()
        rot_matrix = rest_matrix_inv @ rot_matrix @ rest_matrix
        rotation_quaternion = rot_matrix.to_quaternion()
        for i in range(3):
            if not pose_bone.lock_rotation[i]:
                pose_bone.rotation_quaternion[i + 1] = rotation_quaternion[i + 1]

        if not pose_bone.lock_rotation_w:
            pose_bone.rotation_quaternion.w = rotation_quaternion.w

    scale = Vector((1, 1, 1))
    children = joint.get_children()
    scalable = (pose_bone != None) and (len(children) == 1)
    for child in children:
        scale = animate_bone(ctx, obj, rest_matrix.to_translation(), rest_matrix_inv, scalable, child)

    if scalable:
        for i in range(3):
            if not pose_bone.lock_scale[i]:
                pose_bone.scale[i] = scale[i]

    return parent_scale

def record_frame(ctx, obj):
    bones_data = record_data.get(obj.name)
    if bones_data == None:
        return
    for bone in obj.pose.bones:
        bone_data = bones_data.get(bone.name)
        if bone_data == None:
            continue
        bone_data.append((mocap_timer.time_delta, Vector(bone.location), Quaternion(bone.rotation_quaternion), Vector(bone.scale)))

def animate_armatures_indirect(ctx, source_obj):
    for target_obj in bpy.data.objects:
        if not target_obj.nml_active:
            continue
        if target_obj.type == 'ARMATURE' and target_obj.nml_source_armature == source_obj.name:
            for target_pose_bone in target_obj.pose.bones: 
                source_pose_bone = source_obj.pose.bones.get(target_pose_bone.nml_source_bone)
                if not source_pose_bone:
                    continue
                target_pose_bone.bone.inherit_scale = 'NONE'
                if target_pose_bone.rotation_mode != 'QUATERNION':
                    target_pose_bone.rotation_mode = 'QUATERNION'

                target_matrix_tpose = Matrix.Identity(4)
                target_matrix_tpose[0][0:4] = target_pose_bone.nml_matrix_tpose[0:4]
                target_matrix_tpose[1][0:4] = target_pose_bone.nml_matrix_tpose[4:8]
                target_matrix_tpose[2][0:4] = target_pose_bone.nml_matrix_tpose[8:12]
                target_matrix_tpose[3][0:4] = target_pose_bone.nml_matrix_tpose[12:16]

                target_matrix_basis_tpose = Matrix.Identity(4)
                target_matrix_basis_tpose[0][0:4] = target_pose_bone.nml_matrix_basis_tpose[0:4]
                target_matrix_basis_tpose[1][0:4] = target_pose_bone.nml_matrix_basis_tpose[4:8]
                target_matrix_basis_tpose[2][0:4] = target_pose_bone.nml_matrix_basis_tpose[8:12]
                target_matrix_basis_tpose[3][0:4] = target_pose_bone.nml_matrix_basis_tpose[12:16]

                target_matrix_world_tpose = target_matrix_tpose.to_3x3().inverted() @ target_obj.matrix_world.to_3x3().inverted()
                source_matrix_world_tpose = source_pose_bone.bone.matrix_local.to_3x3().inverted() @ source_obj.matrix_world.to_3x3().inverted()
                matrix_source_to_target = target_matrix_world_tpose @ source_matrix_world_tpose.inverted()

                target_matrix_world = matrix_source_to_target.to_4x4() @ source_pose_bone.matrix_basis @ source_matrix_world_tpose.to_4x4()
                target_pose_bone.matrix_basis = target_matrix_world @ target_matrix_world_tpose.to_4x4().inverted() @ target_matrix_basis_tpose

                factor = 1
                if source_pose_bone.name == 'Hips':
                    target_pos = (target_matrix_tpose @ target_obj.matrix_world).to_translation() 
                    target_pos = target_matrix_world_tpose.to_quaternion() @ target_pos
                    scale = (target_matrix_tpose @ target_obj.matrix_world).to_scale()
                    scale = target_matrix_world_tpose.to_quaternion() @ scale
                    target_pos = target_pos * scale
                    source_pos = (source_pose_bone.bone.matrix_local @ source_obj.matrix_world).to_translation()
                    factor = target_pos.z / source_pos.z
                else:
                    target_pos = (target_matrix_tpose @ target_obj.matrix_world).to_translation() 
                    target_parent_matrix_tpose = Matrix.Identity(4)
                    target_parent_matrix_tpose[0][0:4] = target_pose_bone.parent.nml_matrix_tpose[0:4]
                    target_parent_matrix_tpose[1][0:4] = target_pose_bone.parent.nml_matrix_tpose[4:8]
                    target_parent_matrix_tpose[2][0:4] = target_pose_bone.parent.nml_matrix_tpose[8:12]
                    target_parent_matrix_tpose[3][0:4] = target_pose_bone.parent.nml_matrix_tpose[12:16]
                    scale = (target_parent_matrix_tpose @ target_obj.matrix_world).to_scale()
                    target_pos = target_pos * scale
                    target_parent_pos = (target_parent_matrix_tpose @ target_obj.matrix_world).to_translation() * scale
                    target_len = (target_pos - target_parent_pos).length

                    source_pos = (source_pose_bone.bone.matrix_local @ source_obj.matrix_world).to_translation()
                    source_parent_pos = (source_pose_bone.bone.parent.matrix_local @ source_obj.matrix_world).to_translation()
                    source_len = (source_pos - source_parent_pos).length
                    factor = target_len / source_len

                target_pose_bone.matrix_basis[0][3] = target_pose_bone.matrix_basis[0][3] * factor
                target_pose_bone.matrix_basis[1][3] = target_pose_bone.matrix_basis[1][3] * factor
                target_pose_bone.matrix_basis[2][3] = target_pose_bone.matrix_basis[2][3] * factor

            if ctx.scene.nml_recording:
                record_frame(ctx, target_obj)

def animate_armatures(ctx, mcp_avatar):
    for obj in bpy.data.objects:
        if not obj.nml_active:
            continue
        if obj.type == 'ARMATURE' and obj.nml_chr_name == mcp_avatar.get_name():
            animate_bone(ctx, obj, Vector(), Matrix(), False, mcp_avatar.get_root_joint())
            if ctx.scene.nml_recording:
                record_frame(ctx, obj)
            animate_armatures_indirect(ctx, obj)

def poll_data(ctx):
    mcp_evts = mocap_app.poll_next_event()
    for mcp_evt in mcp_evts:
        if mcp_evt.event_type == MCPEventType.AvatarUpdated:
            avatar = MCPAvatar(mcp_evt.event_data.avatar_handle)
            animate_armatures(ctx, avatar)

class MocapConnect(bpy.types.Operator):
    bl_idname = 'neuron_mocap_live.connect'
    bl_label = 'Connect'

    def execute(self, ctx):
        global mocap_timer
        settings = MCPSettings()
        if ctx.scene.nml_protocol == 'TCP':
            settings.set_tcp(ctx.scene.nml_ip, ctx.scene.nml_port)
        else:
            settings.set_udp(ctx.scene.nml_port)
        mocap_app.set_settings(settings)
        status, msg = mocap_app.open()
        if status:
            ctx.scene.nml_living = True
        else:
            self.report({'ERROR'}, 'Connect failed: {0}'.format(msg))
        ctx.window_manager.modal_handler_add(self)
        mocap_timer = ctx.window_manager.event_timer_add(1 / 60, window = ctx.window)
        return {'RUNNING_MODAL'}

    def modal(self, ctx, evt):
        if evt.type == 'TIMER':
            poll_data(ctx)
        if not ctx.scene.nml_living:
            return {'FINISHED'}
        return {'PASS_THROUGH'}

class MocapDisconnect(bpy.types.Operator):
    bl_idname = 'neuron_mocap_live.disconnect'
    bl_label = 'Disconnect'

    def execute(self, ctx):
        global mocap_timer
        ctx.scene.nml_living = False
        status, msg = mocap_app.close()
        if not status:
            self.report({'ERROR'}, 'Disconnect failed: {0}'.format(msg))
        ctx.window_manager.event_timer_remove(mocap_timer)
        return {'FINISHED'}

class MocapStartRecord(bpy.types.Operator):
    bl_idname = 'neuron_mocap_live.start_record'
    bl_label = 'Start Record'

    def execute(self, ctx):
        global record_data
        record_data = dict()
        for obj in bpy.data.objects:
            if not obj.nml_active:
                continue
            if obj.type == 'ARMATURE':
                bones_data = dict()
                for bone in obj.data.bones:
                    bones_data[bone.name] = list()
                record_data[obj.name] = bones_data

        ctx.scene.nml_recording = True
        return {'FINISHED'}

def save_animation_data(ctx, obj, bones_data):
    obj.animation_data_create()
    action = bpy.data.actions.new(name='mocap')
    obj.animation_data.action = action
    dt = 1 / ctx.scene.render.fps
    for bone in obj.pose.bones:
        bone_data = bones_data.get(bone.name)
        if bone_data == None:
            continue

        data_path = 'pose.bones["%s"].location' % bone.name
        for axis_i in range(3):
            curve = action.fcurves.new(data_path = data_path, index = axis_i)
            keyframe_points = curve.keyframe_points
            frame_count = len(bone_data)
            keyframe_points.add(frame_count)
            frame_time = 0
            for frame_i in range(frame_count):
                keyframe_points[frame_i].co = (
                    frame_time / dt + 1,
                    bone_data[frame_i][1][axis_i]
                )
                frame_time = frame_time + bone_data[frame_i][0]

        data_path = 'pose.bones["%s"].rotation_quaternion' % bone.name
        for axis_i in range(4):
            curve = action.fcurves.new(data_path = data_path, index = axis_i)
            keyframe_points = curve.keyframe_points
            frame_count = len(bone_data)
            keyframe_points.add(frame_count)
            frame_time = 0
            for frame_i in range(frame_count):
                keyframe_points[frame_i].co = (
                    frame_time / dt + 1,
                    bone_data[frame_i][2][axis_i]
                )
                frame_time = frame_time + bone_data[frame_i][0]

        data_path = 'pose.bones["%s"].scale' % bone.name
        for axis_i in range(3):
            curve = action.fcurves.new(data_path = data_path, index = axis_i)
            keyframe_points = curve.keyframe_points
            frame_count = len(bone_data)
            keyframe_points.add(frame_count)
            frame_time = 0
            for frame_i in range(frame_count):
                keyframe_points[frame_i].co = (
                    frame_time / dt + 1,
                    bone_data[frame_i][3][axis_i]
                )
                frame_time = frame_time + bone_data[frame_i][0]

    for cu in action.fcurves:
        for bez in cu.keyframe_points:
            bez.interpolation = 'LINEAR'

class MocapStopRecord(bpy.types.Operator):
    bl_idname = 'neuron_mocap_live.stop_record'
    bl_label = 'Stop Record'

    def execute(self, ctx):
        global record_data
        ctx.scene.nml_recording = False
        for obj in bpy.data.objects:
            if not obj.nml_active:
                continue
            bones_data = record_data.get(obj.name)
            if bones_data != None:
                save_animation_data(ctx, obj, bones_data)

        record_data = None
        return {'FINISHED'}
