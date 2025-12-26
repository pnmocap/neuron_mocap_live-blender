import bpy

class RecordPanel(bpy.types.Panel):
    bl_idname = 'NOITOM_PT_RecordPanel'
    bl_label = 'Record'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "NEURON MOCAP"

    @classmethod
    def poll(cls, ctx):
        return ctx.scene.nml_living

    def draw(self, ctx):
        layout = self.layout
        col = layout.column()

        if not ctx.scene.nml_recording:
            row = col.row(align=True)
            row.operator('neuron_mocap_live.start_record', icon='REC')
            
            # 显示已保存的动画信息
            col.separator()
            saved_actions = []
            for obj in bpy.data.objects:
                if obj.type == 'ARMATURE' and obj.animation_data and obj.animation_data.action:
                    action_name = obj.animation_data.action.name
                    if action_name.startswith('mocap_'):
                        saved_actions.append((obj.name, action_name))
            
            if saved_actions:
                col.label(text="已保存的动画:", icon='ACTION')
                for obj_name, action_name in saved_actions:
                    row = col.row(align=True)
                    row.label(text=f"  {obj_name}: {action_name}", icon='ARMATURE_DATA')
        else:
            row = col.row(align=True)
            row.operator('neuron_mocap_live.stop_record', icon='REC', depress=True)