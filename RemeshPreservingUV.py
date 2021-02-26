bl_info = {
    "name": "Remesh Preserving UV",
    "author": "terracottahaniwa",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "Call from F3 Search",
    "description": "Remesh Preserving UV",
    "category": "Remesh",
}


import bpy


def adjust_mode_strings(mode_when_called):
    if mode_when_called == 'EDIT_MESH':
        mode_when_called = 'EDIT'
    if mode_when_called == 'PAINT_VERTEX':
        mode_when_called = 'VERTEX_PAINT'
    if mode_when_called == 'PAINT_WEIGHT':
        mode_when_called = 'WEIGHT_PAINT'
    if mode_when_called == 'PAINT_TEXTURE':
        mode_when_called = 'TEXTURE_PAINT'
    return mode_when_called


def activate_object(context, object):
    bpy.ops.object.select_all(action='DESELECT')
    object.select_set(True)
    context.view_layer.objects.active = object


def find_temporal_modifire(context):
    for modifire in context.object.modifiers:
        if modifire.type == 'DATA_TRANSFER':
            latest_modifire = modifire
    return latest_modifire


def main(self, context):
    if context.active_object.type == 'MESH':

        mode_when_called = adjust_mode_strings(context.mode)        
        bpy.ops.object.mode_set(mode = 'OBJECT')

        original_object = context.active_object
        bpy.ops.object.duplicate()
        temporal_object = context.active_object

        activate_object(context, original_object)
        bpy.ops.object.voxel_remesh()
        bpy.ops.mesh.uv_texture_add()

        bpy.ops.object.modifier_add(type='DATA_TRANSFER')
        temporal_modifire = find_temporal_modifire(context)
        temporal_modifire.object = temporal_object
        temporal_modifire.use_loop_data = True
        temporal_modifire.data_types_loops = {'UV'}
        temporal_modifire.loop_mapping = 'POLYINTERP_NEAREST'
        bpy.ops.object.modifier_apply(modifier=temporal_modifire.name)

        activate_object(context, temporal_object)
        bpy.ops.object.delete()

        activate_object(context, original_object)
        bpy.ops.object.mode_set(mode=mode_when_called)


class REMESH_OT_PreservingUV(bpy.types.Operator):
    """Remesh Preserving UV"""
    bl_idname = "object.remesh_preserving_vcol"
    bl_label = "Remesh Preserving UV"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        main(self, context)
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(REMESH_OT_PreservingUV.bl_idname, icon='MOD_REMESH')


def register():
    bpy.utils.register_class(REMESH_OT_PreservingUV)
    bpy.types.TOPBAR_MT_app_system.append(menu_func)


def unregister():
    bpy.utils.unregister_class(REMESH_OT_PreservingUV)
    bpy.types.TOPBAR_MT_app_system.append(menu_func)


if __name__ == "__main__":
    register()