bl_info = {
    "name": "EasyTools",
    "author": "Derek Wang",
    "version": (4, 7, 6),
    "blender": (2, 93, 0),
    "location": "N Panel",
    "warning": "",
    "description": "blender中文社区添加方便快捷功能,欢迎在些基础上广泛添加功能",
    "doc_url": "",
    "category": "EasyTools",
}
import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty, PointerProperty, StringProperty
from . import myeasytools

classes = (
    myeasytools.MISCSettings,
    myeasytools.MISC_PT_PropsPanel,
    myeasytools.Translate_OT_Col_to_New_Location,
    myeasytools.Add_OT_Non_PBR_Mat,
    myeasytools.Add_OT_HDRI_Texture,
    myeasytools.Find_OT_KD_Tree_Shortest_Distance,
    myeasytools.Write_OT_Text_to_New_Location,
    myeasytools.Add_OT_Cam_by_Image,
    )        
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.misc_settings = PointerProperty(type=myeasytools.MISCSettings)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

