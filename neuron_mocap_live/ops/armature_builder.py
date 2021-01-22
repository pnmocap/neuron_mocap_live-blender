from math import radians, ceil
from mathutils import Vector, Euler, Matrix
import bpy
import bpy_extras
import os

class BVH_Node:
    __slots__ = (
        # Bvh joint name.
        'name',
        # BVH_Node type or None for no parent.
        'parent',
        # A list of children of this type..
        'children',
        # Worldspace rest location for the head of this node.
        'rest_head_world',
        # Localspace rest location for the head of this node.
        'rest_head_local',
        # Worldspace rest location for the tail of this node.
        'rest_tail_world',
        # Worldspace rest location for the tail of this node.
        'rest_tail_local',
        # List of 6 ints, -1 for an unused channel,
        # otherwise an index for the BVH motion data lines,
        # loc triple then rot triple.
        'channels',
        # A triple of indices as to the order rotation is applied.
        # [0,1,2] is x/y/z - [None, None, None] if no rotation..
        'rot_order',
        # Same as above but a string 'XYZ' format..
        'rot_order_str',
        # A list one tuple's one for each frame: (locx, locy, locz, rotx, roty, rotz),
        # euler rotation ALWAYS stored xyz order, even when native used.
        'anim_data',
        # Convenience function, bool, same as: (channels[0] != -1 or channels[1] != -1 or channels[2] != -1).
        'has_loc',
        # Convenience function, bool, same as: (channels[3] != -1 or channels[4] != -1 or channels[5] != -1).
        'has_rot',
        # Index from the file, not strictly needed but nice to maintain order.
        'index',
        # Use this for whatever you want.
        'temp',
    )

    _eul_order_lookup = {
        (None, None, None): 'XYZ',  # XXX Dummy one, no rotation anyway!
        (0, 1, 2): 'XYZ',
        (0, 2, 1): 'XZY',
        (1, 0, 2): 'YXZ',
        (1, 2, 0): 'YZX',
        (2, 0, 1): 'ZXY',
        (2, 1, 0): 'ZYX',
    }

    def __init__(self, name, rest_head_world, rest_head_local, parent, channels, rot_order, index):
        self.name = name
        self.rest_head_world = rest_head_world
        self.rest_head_local = rest_head_local
        self.rest_tail_world = None
        self.rest_tail_local = None
        self.parent = parent
        self.channels = channels
        self.rot_order = tuple(rot_order)
        self.rot_order_str = BVH_Node._eul_order_lookup[self.rot_order]
        self.index = index

        # convenience functions
        self.has_loc = channels[0] != -1 or channels[1] != -1 or channels[2] != -1
        self.has_rot = channels[3] != -1 or channels[4] != -1 or channels[5] != -1

        self.children = []

        # List of 6 length tuples: (lx, ly, lz, rx, ry, rz)
        # even if the channels aren't used they will just be zero.
        self.anim_data = [(0, 0, 0, 0, 0, 0)]

    def __repr__(self):
        return (
            "BVH name: '%s', rest_loc:(%.3f,%.3f,%.3f), rest_tail:(%.3f,%.3f,%.3f)" % (
                self.name,
                *self.rest_head_world,
                *self.rest_head_world,
            )
        )


def sorted_nodes(bvh_nodes):
    bvh_nodes_list = list(bvh_nodes.values())
    bvh_nodes_list.sort(key=lambda bvh_node: bvh_node.index)
    return bvh_nodes_list


def read_bvh(context, file_path, rotate_mode='XYZ', global_scale=1.0):
    # File loading stuff
    # Open the file for importing
    file = open(file_path, 'rU')

    # Separate into a list of lists, each line a list of words.
    file_lines = file.readlines()
    # Non standard carrage returns?
    if len(file_lines) == 1:
        file_lines = file_lines[0].split('\r')

    # Split by whitespace.
    file_lines = [ll for ll in [l.split() for l in file_lines] if ll]

    # Create hierarchy as empties
    if file_lines[0][0].lower() == 'hierarchy':
        # print 'Importing the BVH Hierarchy for:', file_path
        pass
    else:
        raise Exception("This is not a BVH file")

    bvh_nodes = {None: None}
    bvh_nodes_serial = [None]
    bvh_frame_count = None
    bvh_frame_time = None

    channelIndex = -1

    lineIdx = 0  # An index for the file.
    while lineIdx < len(file_lines) - 1:
        if file_lines[lineIdx][0].lower() in {'root', 'joint'}:

            # Join spaces into 1 word with underscores joining it.
            if len(file_lines[lineIdx]) > 2:
                file_lines[lineIdx][1] = '_'.join(file_lines[lineIdx][1:])
                file_lines[lineIdx] = file_lines[lineIdx][:2]

            # MAY NEED TO SUPPORT MULTIPLE ROOTS HERE! Still unsure weather multiple roots are possible?

            # Make sure the names are unique - Object names will match joint names exactly and both will be unique.
            name = file_lines[lineIdx][1]

            # print '%snode: %s, parent: %s' % (len(bvh_nodes_serial) * '  ', name,  bvh_nodes_serial[-1])

            lineIdx += 2  # Increment to the next line (Offset)
            rest_head_local = global_scale * Vector((
                float(file_lines[lineIdx][1]),
                float(file_lines[lineIdx][2]),
                float(file_lines[lineIdx][3]),
            ))
            lineIdx += 1  # Increment to the next line (Channels)

            # newChannel[Xposition, Yposition, Zposition, Xrotation, Yrotation, Zrotation]
            # newChannel references indices to the motiondata,
            # if not assigned then -1 refers to the last value that will be added on loading at a value of zero, this is appended
            # We'll add a zero value onto the end of the MotionDATA so this always refers to a value.
            my_channel = [-1, -1, -1, -1, -1, -1]
            my_rot_order = [None, None, None]
            rot_count = 0
            for channel in file_lines[lineIdx][2:]:
                channel = channel.lower()
                channelIndex += 1  # So the index points to the right channel
                if channel == 'xposition':
                    my_channel[0] = channelIndex
                elif channel == 'yposition':
                    my_channel[1] = channelIndex
                elif channel == 'zposition':
                    my_channel[2] = channelIndex

                elif channel == 'xrotation':
                    my_channel[3] = channelIndex
                    my_rot_order[rot_count] = 0
                    rot_count += 1
                elif channel == 'yrotation':
                    my_channel[4] = channelIndex
                    my_rot_order[rot_count] = 1
                    rot_count += 1
                elif channel == 'zrotation':
                    my_channel[5] = channelIndex
                    my_rot_order[rot_count] = 2
                    rot_count += 1

            channels = file_lines[lineIdx][2:]

            my_parent = bvh_nodes_serial[-1]  # account for none

            # Apply the parents offset accumulatively
            if my_parent is None:
                rest_head_world = Vector(rest_head_local)
            else:
                rest_head_world = my_parent.rest_head_world + rest_head_local

            bvh_node = bvh_nodes[name] = BVH_Node(
                name,
                rest_head_world,
                rest_head_local,
                my_parent,
                my_channel,
                my_rot_order,
                len(bvh_nodes) - 1,
            )

            # If we have another child then we can call ourselves a parent, else
            bvh_nodes_serial.append(bvh_node)

        # Account for an end node.
        # There is sometimes a name after 'End Site' but we will ignore it.
        if file_lines[lineIdx][0].lower() == 'end' and file_lines[lineIdx][1].lower() == 'site':
            # Increment to the next line (Offset)
            lineIdx += 2
            rest_tail = global_scale * Vector((
                float(file_lines[lineIdx][1]),
                float(file_lines[lineIdx][2]),
                float(file_lines[lineIdx][3]),
            ))

            bvh_nodes_serial[-1].rest_tail_world = bvh_nodes_serial[-1].rest_head_world + rest_tail
            bvh_nodes_serial[-1].rest_tail_local = bvh_nodes_serial[-1].rest_head_local + rest_tail

            # Just so we can remove the parents in a uniform way,
            # the end has kids so this is a placeholder.
            bvh_nodes_serial.append(None)

        if len(file_lines[lineIdx]) == 1 and file_lines[lineIdx][0] == '}':  # == ['}']
            bvh_nodes_serial.pop()  # Remove the last item

        # End of the hierarchy. Begin the animation section of the file with
        # the following header.
        #  MOTION
        #  Frames: n
        #  Frame Time: dt
        if len(file_lines[lineIdx]) == 1 and file_lines[lineIdx][0].lower() == 'motion':
            lineIdx += 1  # Read frame count.
            if (
                    len(file_lines[lineIdx]) == 2 and
                    file_lines[lineIdx][0].lower() == 'frames:'
            ):
                bvh_frame_count = int(file_lines[lineIdx][1])

            lineIdx += 1  # Read frame rate.
            if (
                    len(file_lines[lineIdx]) == 3 and
                    file_lines[lineIdx][0].lower() == 'frame' and
                    file_lines[lineIdx][1].lower() == 'time:'
            ):
                bvh_frame_time = float(file_lines[lineIdx][2])

            lineIdx += 1  # Set the cursor to the first frame

            break

        lineIdx += 1

    # Remove the None value used for easy parent reference
    del bvh_nodes[None]
    # Don't use anymore
    del bvh_nodes_serial

    # importing world with any order but nicer to maintain order
    # second life expects it, which isn't to spec.
    bvh_nodes_list = sorted_nodes(bvh_nodes)

    while lineIdx < len(file_lines):
        line = file_lines[lineIdx]
        for bvh_node in bvh_nodes_list:
            # for bvh_node in bvh_nodes_serial:
            lx = ly = lz = rx = ry = rz = 0.0
            channels = bvh_node.channels
            anim_data = bvh_node.anim_data
            if channels[0] != -1:
                lx = global_scale * float(line[channels[0]])

            if channels[1] != -1:
                ly = global_scale * float(line[channels[1]])

            if channels[2] != -1:
                lz = global_scale * float(line[channels[2]])

            if channels[3] != -1 or channels[4] != -1 or channels[5] != -1:

                rx = radians(float(line[channels[3]]))
                ry = radians(float(line[channels[4]]))
                rz = radians(float(line[channels[5]]))

            # Done importing motion data #
            anim_data.append((lx, ly, lz, rx, ry, rz))
        lineIdx += 1

    # Assign children
    for bvh_node in bvh_nodes_list:
        bvh_node_parent = bvh_node.parent
        if bvh_node_parent:
            bvh_node_parent.children.append(bvh_node)

    # Now set the tip of each bvh_node
    for bvh_node in bvh_nodes_list:

        if not bvh_node.rest_tail_world:
            if len(bvh_node.children) == 0:
                # could just fail here, but rare BVH files have childless nodes
                bvh_node.rest_tail_world = Vector(bvh_node.rest_head_world)
                bvh_node.rest_tail_local = Vector(bvh_node.rest_head_local)
            elif len(bvh_node.children) == 1:
                bvh_node.rest_tail_world = Vector(bvh_node.children[0].rest_head_world)
                bvh_node.rest_tail_local = bvh_node.rest_head_local + bvh_node.children[0].rest_head_local
            else:
                # allow this, see above
                # if not bvh_node.children:
                #	raise Exception("bvh node has no end and no children. bad file")

                # Removed temp for now
                rest_tail_world = Vector((0.0, 0.0, 0.0))
                rest_tail_local = Vector((0.0, 0.0, 0.0))
                for bvh_node_child in bvh_node.children:
                    rest_tail_world += bvh_node_child.rest_head_world
                    rest_tail_local += bvh_node_child.rest_head_local

                bvh_node.rest_tail_world = rest_tail_world * (1.0 / len(bvh_node.children))
                bvh_node.rest_tail_local = rest_tail_local * (1.0 / len(bvh_node.children))

        # Make sure tail isn't the same location as the head.
        if (bvh_node.rest_tail_local - bvh_node.rest_head_local).length <= 0.001 * global_scale:
            print("\tzero length node found:", bvh_node.name)
            bvh_node.rest_tail_local.y = bvh_node.rest_tail_local.y + global_scale / 10
            bvh_node.rest_tail_world.y = bvh_node.rest_tail_world.y + global_scale / 10

    return bvh_nodes, bvh_frame_time, bvh_frame_count


def bvh_node_dict2armature(
        context,
        bvh_name,
        bvh_nodes,
        rotate_mode='XYZ',
        global_matrix=None
):
    # Add the new armature,
    scene = context.scene
    for obj in scene.objects:
        obj.select_set(False)

    arm_data = bpy.data.armatures.new(bvh_name)
    arm_ob = bpy.data.objects.new(bvh_name, arm_data)

    context.collection.objects.link(arm_ob)

    arm_ob.select_set(True)
    context.view_layer.objects.active = arm_ob

    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)

    bvh_nodes_list = sorted_nodes(bvh_nodes)

    # Get the average bone length for zero length bones, we may not use this.
    average_bone_length = 0.0
    nonzero_count = 0
    for bvh_node in bvh_nodes_list:
        l = (bvh_node.rest_head_local - bvh_node.rest_tail_local).length
        if l:
            average_bone_length += l
            nonzero_count += 1

    # Very rare cases all bones could be zero length???
    if not average_bone_length:
        average_bone_length = 0.1
    else:
        # Normal operation
        average_bone_length = average_bone_length / nonzero_count

    # XXX, annoying, remove bone.
    while arm_data.edit_bones:
        arm_ob.edit_bones.remove(arm_data.edit_bones[-1])

    ZERO_AREA_BONES = []
    for bvh_node in bvh_nodes_list:

        # New editbone
        bone = bvh_node.temp = arm_data.edit_bones.new(bvh_node.name)

        bone.head = bvh_node.rest_head_world
        bone.tail = bvh_node.rest_tail_world

        # Zero Length Bones! (an exceptional case)
        if (bone.head - bone.tail).length < 0.001:
            print("\tzero length bone found:", bone.name)
            if bvh_node.parent:
                ofs = bvh_node.parent.rest_head_local - bvh_node.parent.rest_tail_local
                if ofs.length:  # is our parent zero length also?? unlikely
                    bone.tail = bone.tail - ofs
                else:
                    bone.tail.y = bone.tail.y + average_bone_length
            else:
                bone.tail.y = bone.tail.y + average_bone_length

            ZERO_AREA_BONES.append(bone.name)

    for bvh_node in bvh_nodes_list:
        if bvh_node.parent:
            # bvh_node.temp is the Editbone

            # Set the bone parent
            bvh_node.temp.parent = bvh_node.parent.temp

            # Set the connection state
            if(
                    (not bvh_node.has_loc) and
                    (bvh_node.parent.temp.name not in ZERO_AREA_BONES) and
                    (bvh_node.parent.rest_tail_local == bvh_node.rest_head_local)
            ):
                bvh_node.temp.use_connect = True

    # Replace the editbone with the editbone name,
    # to avoid memory errors accessing the editbone outside editmode
    for bvh_node in bvh_nodes_list:
        bvh_node.temp = bvh_node.temp.name

    # Now Apply the animation to the armature

    # Get armature animation data
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    pose = arm_ob.pose
    pose_bones = pose.bones

    if rotate_mode == 'NATIVE':
        for bvh_node in bvh_nodes_list:
            bone_name = bvh_node.temp  # may not be the same name as the bvh_node, could have been shortened.
            pose_bone = pose_bones[bone_name]
            pose_bone.rotation_mode = bvh_node.rot_order_str

    elif rotate_mode != 'QUATERNION':
        for pose_bone in pose_bones:
            pose_bone.rotation_mode = rotate_mode
    else:
        # Quats default
        pass

    context.view_layer.update()

    # finally apply matrix
    arm_ob.matrix_world = global_matrix
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

    return arm_ob

def add_armature_by_bvh(ctx, name):
    file_path = os.path.join(os.path.dirname(__file__), 'armature', name + '.bvh')
    bvh_nodes, bvh_frame_time, bvh_frame_count = read_bvh(
        ctx, file_path, global_scale=0.01
    )
    bvh_node_dict2armature(
        ctx,
        name,
        bvh_nodes,
        global_matrix=Matrix.Translation(ctx.scene.cursor.location).to_4x4() @ bpy_extras.io_utils.axis_conversion(
            from_forward='-Z',
            from_up='Y'
        ).to_4x4()
    )


class AddPNSArmature(bpy.types.Operator):
    bl_idname = 'neuron_mocap_live.add_pns_armature'
    bl_label = 'Noitom PNS Armature'

    def execute(self, ctx):
        add_armature_by_bvh(ctx, 'PNS')
        return {'FINISHED'}

class AddPNSThumbOpenArmature(bpy.types.Operator):
    bl_idname = 'neuron_mocap_live.add_pns_thumb_open_armature'
    bl_label = 'Noitom PNS(Thumb open) Armature'

    def execute(self, ctx):
        print('add pns armature')
        add_armature_by_bvh(ctx, 'PNS - Thumb open')
        return {'FINISHED'}

class AddPNProArmature(bpy.types.Operator):
    bl_idname = 'neuron_mocap_live.add_pn_pro_armature'
    bl_label = 'Noitom PN Pro Armature'

    def execute(self, ctx):
        add_armature_by_bvh(ctx, 'PN Pro')
        return {'FINISHED'}