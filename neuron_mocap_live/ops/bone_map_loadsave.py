import bpy
import json
from bpy_extras.io_utils import ExportHelper, ImportHelper

class LoadBoneMap(bpy.types.Operator, ImportHelper):
	bl_idname = 'neuron_mocap_live.load_bone_map'
	bl_label = 'Load Bone Map'

	filter_glob: bpy.props.StringProperty(
		default='*.nlbmap',
		options={'HIDDEN'},
		maxlen=255
	)

	@classmethod
	def poll(cls, ctx):
		return bpy.data.objects.get(ctx.active_object.nml_source_armature) != None

	def execute(self, ctx):
		bone_map = dict()
		with open(self.filepath, 'r') as f:
			bone_map = json.loads(f.read())
		for bone in ctx.active_object.pose.bones:
			value = bone_map.get(bone.name)
			if value:
				bone.nml_source_bone = value
			else:
				bone.nml_source_bone = str()
		return {'FINISHED'}

class SaveBoneMap(bpy.types.Operator, ExportHelper):
	bl_idname = 'neuron_mocap_live.save_bone_map'
	bl_label = 'Save Bone Map'
	filename_ext = '.nlbmap'

	filter_glob: bpy.props.StringProperty(
		default='*.nlbmap',
		options={'HIDDEN'},
		maxlen=255
	)

	@classmethod
	def poll(cls, ctx):
		return bpy.data.objects.get(ctx.active_object.nml_source_armature) != None

	def execute(self, ctx):
		bone_map = dict()
		for bone in ctx.active_object.pose.bones:
			if bone.nml_source_bone and len(bone.nml_source_bone) > 0:
				bone_map[bone.name] = bone.nml_source_bone
		with open(self.filepath, 'w') as f:
			f.write(json.dumps(bone_map, indent=4))
			f.close()

		return {'FINISHED'}
