import bpy
import bmesh
import os
import numpy as np
from random import random
from math import sin, cos, acos, degrees, radians, pi
import mathutils
from mathutils import Vector, Matrix

from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty, PointerProperty, StringProperty
from bpy.types import Panel, PropertyGroup, Operator
from . import mynode
def translateColinCol(colname='Collection', myloc=(0, 0, 0)):
    for obj in bpy.data.collections[colname].objects:
        obj.location.x=obj.location.x + myloc[0]
        obj.location.y=obj.location.y + myloc[1]
        obj.location.z=obj.location.z + myloc[2]
    
    for col in bpy.data.collections[colname].children:
        for obj in col.objects:
            obj.location.x=obj.location.x + myloc[0]
            obj.location.y=obj.location.y + myloc[1]
            obj.location.z=obj.location.z + myloc[2]
def update_object(self, context):
    pass
def create_glass_mat():
    mat = bpy.data.materials.new('glasswindow')
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    mat.node_tree.nodes.remove(bsdf)
    my_material_output = mat.node_tree.nodes['Material Output']
    my_material_output.location = (920.0, 290.0)
    my_transparent_0 = mat.node_tree.nodes.new('ShaderNodeBsdfTransparent')
    my_transparent_0.location = (271.0, 112.0)
    my_add_shader = mat.node_tree.nodes.new('ShaderNodeAddShader')
    my_add_shader.location = (545.0, 32.0)
    my_mix_1 = mat.node_tree.nodes.new('ShaderNodeMixShader')
    my_mix_1.location = (690.0, 290.0)
    my_mix_1.inputs['Fac'].default_value = 0.1
    my_glossy_0 = mat.node_tree.nodes.new('ShaderNodeBsdfGlossy')
    my_glossy_0.location = (271.0, 4.0)
    my_glossy_0.inputs['Roughness'].default_value = 0.0
    my_glass_bsdf = mat.node_tree.nodes.new('ShaderNodeBsdfGlass')
    my_glass_bsdf.location = (304.0, 304.0)
    my_glass_bsdf.inputs['Roughness'].default_value = 0.0
    my_glass_bsdf.inputs['IOR'].default_value = 1.45
    my_math = mat.node_tree.nodes.new('ShaderNodeMath')
    my_math.location = (473.0, 483.0)
    my_math.inputs['Value'].default_value = 0.5
    my_math.inputs['Value'].default_value = 0.5
    my_math.inputs['Value'].default_value = 0.0
    my_light_0 = mat.node_tree.nodes.new('ShaderNodeLightPath')
    my_light_0.location = (23.0, 645.0)
    mat.node_tree.links.new(my_mix_1.outputs['Shader'], my_material_output.inputs['Surface'])
    mat.node_tree.links.new(my_glass_bsdf.outputs['BSDF'], my_mix_1.inputs[1])
    mat.node_tree.links.new(my_transparent_0.outputs['BSDF'], my_add_shader.inputs[0])
    mat.node_tree.links.new(my_add_shader.outputs['Shader'], my_mix_1.inputs[2])
    mat.node_tree.links.new(my_math.outputs['Value'], my_mix_1.inputs['Fac'])
    mat.node_tree.links.new(my_light_0.outputs['Is Diffuse Ray'], my_math.inputs[0])
    mat.node_tree.links.new(my_light_0.outputs['Transparent Depth'], my_math.inputs[1])
    mat.node_tree.links.new(my_glossy_0.outputs['BSDF'], my_add_shader.inputs[1])
    return mat

def create_am_glass_mat(matname, replace, rv=0.333, gv=0.342, bv=0.9):
    
    # Avoid duplicate materials
    if replace is False:
        matlist = bpy.data.materials
        for m in matlist:
            if m.name == matname:
                return m
    # Create material
    mat = bpy.data.materials.new(matname)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    mat.blend_method='BLEND'
    mat.use_screen_refraction=True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    mat.node_tree.nodes.remove(bsdf)

    node = nodes.new('ShaderNodeLightPath')
    node.name = 'Light_0'
    node.location = 10, 160

    node = nodes.new('ShaderNodeBsdfRefraction')
    node.name = 'Refraction_0'
    node.inputs[2].default_value = 1  # IOR 1.0
    node.location = 250, 400

    node = nodes.new('ShaderNodeBsdfGlossy')
    node.name = 'Glossy_0'
    node.distribution = 'SHARP'
    node.location = 250, 100

    node = nodes.new('ShaderNodeBsdfTransparent')
    node.name = 'Transparent_0'
    node.location = 500, 10

    node = nodes.new('ShaderNodeMixShader')
    node.name = 'Mix_0'
    node.inputs[0].default_value = 0.035
    node.location = 500, 160

    node = nodes.new('ShaderNodeMixShader')
    node.name = 'Mix_1'
    node.inputs[0].default_value = 0.1
    node.location = 690, 290

    
    #node = nodes[get_node_index(nodes, 'OUTPUT_MATERIAL')]
    node = mat.node_tree.nodes["Material Output"]
    node.location = 920, 290

    # Connect nodes
    outn = nodes['Light_0'].outputs[7]
    inn = nodes['Mix_1'].inputs[0]
    mat.node_tree.links.new(outn, inn)

    outn = nodes['Refraction_0'].outputs[0]
    inn = nodes['Mix_0'].inputs[1]
    mat.node_tree.links.new(outn, inn)

    outn = nodes['Glossy_0'].outputs[0]
    inn = nodes['Mix_0'].inputs[2]
    mat.node_tree.links.new(outn, inn)

    outn = nodes['Mix_0'].outputs[0]
    inn = nodes['Mix_1'].inputs[1]
    mat.node_tree.links.new(outn, inn)

    outn = nodes['Transparent_0'].outputs[0]
    nodes['Transparent_0'].inputs[0].default_value=(rv, gv, bv, 1.0)
    inn = nodes['Mix_1'].inputs[2]
    mat.node_tree.links.new(outn, inn)

    outn = nodes['Mix_1'].outputs[0]
    inn = mat.node_tree.nodes["Material Output"].inputs[0]
    mat.node_tree.links.new(outn, inn)

    return mat
def createtransparentbackgroundphoto(imgpath = r'.\img\earth001.jpg'):
    #图片透明背景通道
    mat = bpy.data.materials.new('transparentBackgroudPhoto')
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    mat.node_tree.nodes.remove(bsdf)

    
    matOutput= mat.node_tree.nodes["Material Output"]
    matOutput.location=(1200,0)
    
    texCoord = mat.node_tree.nodes.new('ShaderNodeTexCoord')
    texCoord.location=(-600,0)
    
    mapping = mat.node_tree.nodes.new('ShaderNodeMapping')
    #mapping.vector_type='NORMAL'
    mapping.location=(-400,0)
    
    
    gradientTexture = mat.node_tree.nodes.new('ShaderNodeTexGradient')
    gradientTexture.location = (-200, 0)
    gradientTexture.gradient_type = 'QUADRATIC_SPHERE'


    colorRamp = mat.node_tree.nodes.new('ShaderNodeValToRGB')
    colorRamp.location = (0, 0)
    colorRamp.color_ramp.elements[1].position=0.01
    colorRamp.color_ramp.elements[0].position=0
    colorRamp.color_ramp.elements[1].color=(1, 1, 1, 1)
    colorRamp.color_ramp.elements[0].color=(0, 0, 0, 1)
    
    
    transparentBSDF = mat.node_tree.nodes.new('ShaderNodeBsdfTransparent')
    transparentBSDF.location=(300, 200)
    
    texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
    texImage.location=(300, -200)
    
    
    img = bpy.data.images.load(filepath=imgpath)
    texImage.image=img
 
    emission = mat.node_tree.nodes.new('ShaderNodeEmission')
    emission.location=(700,-200)
    
    mixShader = mat.node_tree.nodes.new('ShaderNodeMixShader')
    mixShader.location=(1000, 50)
    
    #link
    
    mat.node_tree.links.new(mixShader.outputs[0], matOutput.inputs['Surface'])
    mat.node_tree.links.new(transparentBSDF.outputs[0], mixShader.inputs[1])
    mat.node_tree.links.new(emission.outputs[0], mixShader.inputs[2])
    mat.node_tree.links.new(texImage.outputs[0],emission.inputs[0])
    mat.node_tree.links.new(colorRamp.outputs[0], mixShader.inputs['Fac'])
    mat.node_tree.links.new(gradientTexture.outputs[0], colorRamp.inputs['Fac'])
    mat.node_tree.links.new(mapping.outputs[0], gradientTexture.inputs['Vector'])
    mat.node_tree.links.new(texCoord.outputs[3], mapping.inputs[0])
    return mat  

def createscifieffectmat(imgpath = r'.\img\frames\caust_001.png'):
    mat = bpy.data.materials.new('SciFiRingEffect')
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.location=(600,0)
    bsdf.inputs['Metallic'].default_value=0
    bsdf.inputs['Specular'].default_value=0.51
    bsdf.inputs['Roughness'].default_value=0.0051
    bsdf.inputs['IOR'].default_value=1.45
    bsdf.inputs['Clearcoat'].default_value=0.5
    bsdf.inputs['Clearcoat Roughness'].default_value=0.03
    bsdf.inputs['Transmission'].default_value=1
    bsdf.inputs['Alpha'].default_value=0.98
    bsdf.inputs['Emission'].default_value=(1,1,1,1)
    
    matOutput= mat.node_tree.nodes["Material Output"]
    matOutput.location=(900,0)
    
    
    mapping = mat.node_tree.nodes.new('ShaderNodeMapping')
    #mapping.vector_type='NORMAL'
    mapping.location=(-400,0)
    
    texCoord = mat.node_tree.nodes.new('ShaderNodeTexCoord')
    texCoord.location=(-600,0)
    texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
    texImage.location=(-200,0)
    
    img = bpy.data.images.load(filepath=imgpath)
    texImage.image=img
    
    layerWeight=mat.node_tree.nodes.new('ShaderNodeLayerWeight')
    layerWeight.location=(-100,150)
    
    
    fresnel=mat.node_tree.nodes.new('ShaderNodeFresnel')
    fresnel.location=(100,150)
    
    mixRGB = mat.node_tree.nodes.new('ShaderNodeMixRGB')
    mixRGB.location=(300,50)
    mixRGB.inputs[1].default_value=(0.07,0.36,0.5,1)
    
    bump01 = mat.node_tree.nodes.new('ShaderNodeBump')
    bump01.location=(300,-150)
    bump01.inputs['Strength'].default_value=1
    bump01.inputs['Distance'].default_value=1   
    
    #link
    mat.node_tree.links.new(layerWeight.outputs[1], mixRGB.inputs[0])
    mat.node_tree.links.new(fresnel.outputs[0], mixRGB.inputs[0])
    
    mat.node_tree.links.new(mixRGB.outputs[0],bsdf.inputs[0])
    
    mat.node_tree.links.new(bump01.outputs[0],bsdf.inputs['Normal'])
    mat.node_tree.links.new(texImage.outputs[0],bump01.inputs[2])
    mat.node_tree.links.new(mapping.outputs[0], texImage.inputs['Vector'])
    mat.node_tree.links.new(texCoord.outputs[2], mapping.inputs[0])

    return mat 
def createlightpollutionmat():
    mat = bpy.data.materials.new('LightPollution')
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    mat.node_tree.nodes.remove(bsdf)
    matOutput= mat.node_tree.nodes["Material Output"]
    matOutput.location=(1400,400)    
    emission = mat.node_tree.nodes.new('ShaderNodeEmission')
    
    #emission.inputs['Color'].default_value=(1,0.01,0.016,1)
    emission.inputs['Strength'].default_value=5
    emission.location=(1200,400)

    


    colorRamp01 = mat.node_tree.nodes.new('ShaderNodeValToRGB')
    colorRamp01.color_ramp.elements[1].position=0.727
    colorRamp01.color_ramp.elements[0].position=0.707
    #colorRamp01.color_ramp.elements[1].color=(0.68,0.842,0.10842,1)
    #colorRamp01.color_ramp.elements[0].color=(0.512,0.082956,0.13512,1)
    colorRamp01.color_ramp.elements[1].color=(1,1,1,1)
    colorRamp01.color_ramp.elements[0].color=(0,0,0,1)
    colorRamp01.location=(700,600)

    colorRamp02 = mat.node_tree.nodes.new('ShaderNodeValToRGB')
    colorRamp02.color_ramp.elements[1].position=0.727
    colorRamp02.color_ramp.elements[0].position=0.707
    colorRamp02.color_ramp.elements[1].color=(0.352,0.0256,0.3542,1)
    colorRamp02.color_ramp.elements[0].color=(0,0,0,1)
    colorRamp02.location=(700,300)

    colorRamp03 = mat.node_tree.nodes.new('ShaderNodeValToRGB')
    colorRamp03.color_ramp.elements[1].position=0.727
    colorRamp03.color_ramp.elements[0].position=0.707
    colorRamp03.color_ramp.elements[1].color=(0.852,0.02756,0.0412,1)
    colorRamp03.color_ramp.elements[0].color=(0,0,0,1)
    colorRamp03.location=(700,0)

    
    texNoise01 = mat.node_tree.nodes.new('ShaderNodeTexNoise')
    texNoise01.inputs['Scale'].default_value=15
    texNoise01.inputs['Detail'].default_value=2
    texNoise01.location=(400,600)

    texNoise02 = mat.node_tree.nodes.new('ShaderNodeTexNoise')
    texNoise02.inputs['Scale'].default_value=7
    texNoise02.inputs['Detail'].default_value=2
    texNoise02.location=(400,300)

    texNoise03 = mat.node_tree.nodes.new('ShaderNodeTexNoise')
    texNoise03.inputs['Scale'].default_value=3
    texNoise03.inputs['Detail'].default_value=2
    texNoise03.location=(400,0)

    mapping = mat.node_tree.nodes.new('ShaderNodeMapping')
    #mapping.vector_type='NORMAL'
    mapping.location=(-100,300)

    texCoord = mat.node_tree.nodes.new('ShaderNodeTexCoord')
    texCoord.location=(-500,300)
    
    
    mixRGB01 = mat.node_tree.nodes.new('ShaderNodeMixRGB')
    mixRGB01.location=(1000,500)
    mixRGB02 = mat.node_tree.nodes.new('ShaderNodeMixRGB')
    mixRGB02.location=(1000,200)
   

    mat.node_tree.links.new(emission.outputs[0], matOutput.inputs[0])    
    mat.node_tree.links.new(mixRGB02.outputs[0], emission.inputs[0])    
    mat.node_tree.links.new(mixRGB01.outputs[0], mixRGB02.inputs[1])    

    mat.node_tree.links.new(colorRamp01.outputs[0], mixRGB01.inputs[1])    
    mat.node_tree.links.new(colorRamp02.outputs[0], mixRGB01.inputs[2])    
    mat.node_tree.links.new(colorRamp03.outputs[0], mixRGB02.inputs[2])    

    mat.node_tree.links.new(texNoise01.outputs['Fac'],colorRamp01.inputs['Fac'])
    mat.node_tree.links.new(texNoise02.outputs['Fac'],colorRamp02.inputs['Fac'])
    mat.node_tree.links.new(texNoise03.outputs['Fac'],colorRamp03.inputs['Fac'])
    

    mat.node_tree.links.new(mapping.outputs['Vector'],texNoise01.inputs['Vector'])
    mat.node_tree.links.new(mapping.outputs['Vector'],texNoise02.inputs['Vector'])
    mat.node_tree.links.new(mapping.outputs['Vector'],texNoise03.inputs['Vector'])
    
    mat.node_tree.links.new(texCoord.outputs['UV'],mapping.inputs['Vector'])
    return mat
def build_environment_black_background(hdri_path: str, rotation: float = 0.0) -> None:

    world = bpy.data.worlds['World']

    
    world.use_nodes = True
    node_tree = world.node_tree
    bnodes = node_tree.nodes
    for node in bnodes:
        node_tree.nodes.remove(node)

    background01=node_tree.nodes.new('ShaderNodeBackground')
    background02=node_tree.nodes.new('ShaderNodeBackground')
    background02.inputs[0].default_value=(0,0,0,1)
    mixShader = node_tree.nodes.new('ShaderNodeMixShader')
    
    lightPath = node_tree.nodes.new('ShaderNodeLightPath')
    
    worldOutput=node_tree.nodes.new('ShaderNodeOutputWorld')
    
    environment_texture_node = node_tree.nodes.new(type="ShaderNodeTexEnvironment")
    environment_texture_node.image = bpy.data.images.load(hdri_path)

    mapping_node = node_tree.nodes.new(type="ShaderNodeMapping")
    mapping_node.inputs["Rotation"].default_value = (0.0, 0.0, radians(rotation))   
    
    tex_coord_node = node_tree.nodes.new(type="ShaderNodeTexCoord")

    node_tree.links.new(tex_coord_node.outputs["Generated"], mapping_node.inputs["Vector"])
    node_tree.links.new(mapping_node.outputs["Vector"], environment_texture_node.inputs["Vector"])
    node_tree.links.new(environment_texture_node.outputs["Color"], background01.inputs["Color"])
    
    node_tree.links.new(background01.outputs[0], mixShader.inputs[1])
    node_tree.links.new(background02.outputs[0], mixShader.inputs[2])
    node_tree.links.new(lightPath.outputs[0], mixShader.inputs[0])

    
    node_tree.links.new(mixShader.outputs[0], worldOutput.inputs[0])

    mynode.arrange_nodes(node_tree)
def genSkyTexutreBackground():
    bpy.context.scene.world.use_nodes=True

    bnodes=bpy.data.worlds['World'].node_tree.nodes
    for node in bnodes:
        bpy.data.worlds['World'].node_tree.nodes.remove(node)
    btree=bpy.data.worlds['World'].node_tree

    my_world_output = btree.nodes.new('ShaderNodeOutputWorld')
    my_world_output.location = (610.0, 219.0)
    my_gamma = btree.nodes.new('ShaderNodeGamma')
    my_gamma.location = (233.0, 219.0)
    my_gamma.inputs['Gamma'].default_value = 1.2
    my_sky_texture = btree.nodes.new('ShaderNodeTexSky')
    my_sky_texture.sky_type = 'HOSEK_WILKIE'
    my_sky_texture.turbidity = 6
    my_sky_texture.ground_albedo = 0.3
    my_sky_texture.location = (-240.0, 231.0)
    my_hue_saturation_value = btree.nodes.new('ShaderNodeHueSaturation')
    my_hue_saturation_value.location = (11.0, 227.0)
    my_hue_saturation_value.inputs['Hue'].default_value = 0.5
    my_hue_saturation_value.inputs['Saturation'].default_value = 1.8
    my_hue_saturation_value.inputs['Value'].default_value = 2.0
    my_hue_saturation_value.inputs['Fac'].default_value = 1.0
    my_background = btree.nodes.new('ShaderNodeBackground')
    my_background.location = (413.0, 220.0)
    my_background.inputs['Strength'].default_value = 1.0
    btree.links.new(my_background.outputs['Background'], my_world_output.inputs['Surface'])
    btree.links.new(my_hue_saturation_value.outputs['Color'], my_gamma.inputs['Color'])
    btree.links.new(my_sky_texture.outputs['Color'], my_hue_saturation_value.inputs['Color'])
    btree.links.new(my_gamma.outputs['Color'], my_background.inputs['Color'])
def myadd_bezier(v0, v1):
    v0, v1 = Vector(v0), Vector(v1)  
    o = (v1 + v0) / 2  
    curve = bpy.data.curves.new('Curve', 'CURVE')
    spline = curve.splines.new('BEZIER')
    bp0 = spline.bezier_points[0]
    bp0.co = v0 - o
    bp0.handle_left_type = bp0.handle_right_type = 'AUTO'

    spline.bezier_points.add(count=1)
    bp1 = spline.bezier_points[1]
    bp1.co = v1 - o
    bp1.handle_left_type = bp1.handle_right_type = 'AUTO'
    ob = bpy.data.objects.new('Curve', curve)
    ob.matrix_world.translation = o
    curve = ob.data    
    curve.dimensions = '3D'
    curve.bevel_depth = 0.0095
    curve.bevel_resolution = 3
    bpy.context.scene.collection.objects.link(ob)    

    return ob
def genKDTree001(obj, co_find=(0.20, 0.30, 0.0)):
    
    mesh = obj.data
    size = len(mesh.vertices)
    kd = mathutils.kdtree.KDTree(size)

    for i, v in enumerate(mesh.vertices):
        kd.insert(obj.matrix_world @ v.co, i)

    kd.balance()

    co, index, dist = kd.find(co_find)
    print("物体上最短距离的点坐标，点索引，距离:", co, index, dist)
    mylineobj = myadd_bezier(co_find, (co[0],co[1],co[2]))

def createText(text='星月掩映云瞳胧 月落星稀天欲明',myloc=(-1.8,6,0.41),myrotation_euler=(radians(90),0,0),myscale=(0.321,0.321,0.321),myextrude=0.05,mybeveldepth=0.01,isMesh=True):
    flength=8
    rflength=60

    x=random()*flength
    y=random()*flength
    z=random()*flength
    rx=random()*rflength
    ry=random()*rflength*0.01
    rz=random()*rflength*0.01
    #bpy.ops.object.text_add(location=(x, y, z), rotation=(rx,ry,rz))
    bpy.ops.object.text_add(location=myloc, rotation=(0,0,0))
    text_obj = bpy.context.object
    text_obj.name = "Text" #Objectname
    #STXinwei/STZHONGS/STXingkai/STFangsong
    fnt = bpy.data.fonts.load('C:\\Windows\\Fonts\\STXinwei.TTF')
    
    
    text_obj.data.font = fnt
    
    text_obj.rotation_euler = myrotation_euler # Rotate text by 90 degrees along X axis
    text_obj.scale=myscale
    text_obj.data.extrude     = myextrude        # Add depth to the text
    text_obj.data.bevel_depth = mybeveldepth        # Add a nice bevel effect to smooth the text's edges
    text_obj.data.body         = text        # Set the text to be the current row's date
    
    
    if isMesh==True:
        bpy.ops.object.convert(target='MESH') 
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')     
        bpy.ops.object.transform_apply(location=False, scale=True, rotation=True)
    mytxtmat = genEmissionMat(emissioncolor=(1, 1, 1, 1))
    text_obj.data.materials.append(mytxtmat)
    return text_obj 
def createCSGridImg(imgpath = r"E:\documents\Blender\插件\jpg\hdri\01_03_64.jpg",texCoordType=5,myloc=(0,8,0),myrot=(3.14/2,0,0),myscale=(2.5,4.4,1)):
        
    
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=1,y_subdivisions=1,calc_uvs=True,rotation=myrot,location=myloc)  
    mygrid = bpy.context.object
    mygrid.scale=myscale
    mygrid.location = myloc
    mygrid.rotation_euler = myrot
    mat = bpy.data.materials.new('GridImageMaterial')
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    mat.node_tree.nodes.remove(bsdf)
    matOutput= mat.node_tree.nodes["Material Output"]
    
    matOutput.location = (600, 0)
    mixShader = mat.node_tree.nodes.new('ShaderNodeMixShader')
    mixShader.location = (400, 0)

    #BSDFTransparent = mat.node_tree.nodes.new('ShaderNodeBsdfTransparent')
    BSDFTransparent = mat.node_tree.nodes.new('ShaderNodeBsdfGlass')
    BSDFTransparent.location = (100, -300)
    BSDFTransparent.inputs[1].default_value = 0.5

    emission = mat.node_tree.nodes.new('ShaderNodeEmission')
    emission.location = (100, -150)

    mapping = mat.node_tree.nodes.new('ShaderNodeMapping')
    mapping.location = (-400, 0)

    texCoord = mat.node_tree.nodes.new('ShaderNodeTexCoord')
    texCoord.location = (-600, 0)

    texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
    texImage.location = (-200, 0)
    
    img = bpy.data.images.load(filepath=imgpath)
    
    
    texImage.image=img
    #link
    mat.node_tree.links.new(mixShader.outputs[0], matOutput.inputs[0])
    #2-emission,1-BSDFTransparent
    mat.node_tree.links.new(emission.outputs[0], mixShader.inputs[2])
    mat.node_tree.links.new(BSDFTransparent.outputs[0], mixShader.inputs[1])
    
    mat.node_tree.links.new(texImage.outputs[0],emission.inputs[0])
    mat.node_tree.links.new(texImage.outputs[1],mixShader.inputs[0])
    mat.node_tree.links.new(mapping.outputs[0], texImage.inputs['Vector'])
    
    mat.node_tree.links.new(texCoord.outputs[texCoordType], mapping.inputs[0])
    
    mygrid.data.materials.append(mat)   
    bpy.context.view_layer.objects.active =mygrid
    
    return mygrid

def genCamLightButton(myimgpath = r"E:\pic\universe001.jpg",isVertical=False,isButton=True,isImg=True,bText='EasyTools'):
    totalmoves=120
    bpy.context.scene.frame_end=totalmoves
    isCamExisted=False
    for obj in bpy.context.collection.objects:
        if obj.name[0:3]=='Cam' or obj.name[0:2]=='相机':
            print('camhere')    
            cam = obj
            isCamExisted=True
    if isCamExisted==False:
        bpy.ops.object.camera_add(align='VIEW',rotation=(3.14/2,0,0),location=(0,-4,0))
        cam = bpy.data.objects["Camera"]

    if isVertical==False:
        res_x = 1920
        res_y = 1080
    else:
        res_x = 1080
        res_y = 1920


    scene = bpy.data.scenes["Scene"]
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    cam.rotation_mode = 'XYZ'
    
    if isButton==True:
        isize = 3
        if isImg:
            myplane=createCSGridImg(imgpath=myimgpath, texCoordType=2, myloc=(-0.35, 0.15, -1.3), myrot=(0, 0, 0), myscale=(0.1, 0.1, 1))
            myplane.parent=cam
            
        mytxtobj=createText(text=bText, myloc=(0,-0.36,-2.14), myrotation_euler=(radians(0),0,0), myscale=(0.216/isize,0.216/isize,0.039),myextrude=0.00585,mybeveldepth=0.013691,isMesh=False)
        mytxtobj.name='Textbutton'
        mytxtobj.parent=cam
def genEmissionMat(emissioncolor=(0.1, 0.69, 0.8, 1)):
    mat = bpy.data.materials.new('EmissionMat')
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    mat.node_tree.nodes.remove(bsdf)
    matOutput= mat.node_tree.nodes["Material Output"]
    matOutput.location=(600,0)
    
    mixShader = mat.node_tree.nodes.new('ShaderNodeMixShader')
    mixShader.location=(400,0)

    diffuseBSDF = mat.node_tree.nodes.new('ShaderNodeBsdfDiffuse')
    diffuseBSDF.location=(200,0)
    diffuseBSDF.inputs['Color'].default_value=(1,1,1,1)
    
    emission = mat.node_tree.nodes.new('ShaderNodeEmission')
    emission.location=(200,-200)
    
    lightPath = mat.node_tree.nodes.new('ShaderNodeLightPath')
    lightPath.location=(0,300)

    shaderRGB= mat.node_tree.nodes.new('ShaderNodeRGB')
    shaderRGB.outputs[0].default_value=emissioncolor
    shaderRGB.location=(0,-200)
    #link
    mat.node_tree.links.new(mixShader.outputs[0], matOutput.inputs[0])
    mat.node_tree.links.new(lightPath.outputs[0], mixShader.inputs[0])
    mat.node_tree.links.new(diffuseBSDF.outputs[0], mixShader.inputs[1])
    mat.node_tree.links.new(emission.outputs[0], mixShader.inputs[2])
    mat.node_tree.links.new(shaderRGB.outputs[0],emission.inputs[0])
    return mat        
#properties class
class MISCSettings(PropertyGroup):
    # FOR MISC SETTINGS
    
    collectionName : StringProperty(
        name = "集合名称",
        default = ""
    )
    boolName : BoolProperty(
        name = "黑色背景",
        default = True
    )
    locx : FloatProperty(
        name = "fx",
        description = "translate x",
        min = -100,
        max = 100,
        default = 0.0,
        )
    locy : FloatProperty(
        name = "fy",
        description = "translate y",
        min = -100,
        max = 100,
        default = 0.0,
        )
    locz : FloatProperty(
        name = "fz",
        description = "translate z",
        min = -100,
        max = 100,
        default = 0.0,
        )
    mattype: EnumProperty(
        items=(
            ('1', "玻璃01", ""),
            ('2', "玻璃02", ""),
            ('3', "透明背景", ""),
            ('4', "光污染", "")),
        name="材质类型",
        description="定义材质类型",
        update=update_object,
        )
    textContent : StringProperty(
        name = "文字",
        default = "EasyTools"
    )

class MISC_PT_PropsPanel(Panel):
    bl_label = "快捷操作集合"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "EasyTools"
    def draw(self, context):
        settings = bpy.context.scene.misc_settings
        layout = self.layout
        
        row = layout.row()
        col = row.column(align=True)
        col.prop(settings, 'collectionName')

        
        row = layout.row()
        col = row.column(align=True)
        col.prop(settings, 'locx')
        col = row.column(align=True)
        col.prop(settings, 'locy')
        col = row.column(align=True)
        col.prop(settings, 'locz')
        
        row = layout.row()        
        col = row.column(align=True)
        col.operator("object.translatecol", text='移动集合')
        
        row = layout.row()        
        col = row.column(align=True)
        col.prop(settings, 'mattype')

        row = layout.row()        
        col = row.column(align=True)
        col.operator("object.addnonpbrmat", text='添加材质')

        row = layout.row()
        col = row.column(align=True)
        col.prop(settings, 'boolName')
        
        row = layout.row()        
        col = row.column(align=True)
        col.operator("object.addhdritexture", text='添加黑色HDRI贴图')

        row = layout.row()        
        col = row.column(align=True)
        col.operator("object.findshortestdistbykdtree", text='kd树最短距离')
        
        row = layout.row()        
        col = row.column(align=True)
        col.prop(settings, 'textContent')

        row = layout.row()        
        col = row.column(align=True)
        col.operator("object.writetext", text='生成文字')
        
        row = layout.row()        
        col = row.column(align=True)
        col.operator("object.addcameblenderimg", text='相机绑定图片')
class Translate_OT_Col_to_New_Location(Operator):
    bl_label = "TranslateColNewLoc"
    bl_idname = "object.translatecol"
    bl_description = "TranslateColNewLoc"
    
    @classmethod
    def poll(cls, context):
        settings = bpy.context.scene.misc_settings
        mycolname = settings.collectionName
        
        return len(mycolname) > 0
    def execute(self, context):
        #1.挪位置
        miscsettings = bpy.context.scene.misc_settings
        myfx = miscsettings.locx
        myfy = miscsettings.locy
        myfz = miscsettings.locz
        mycolname = miscsettings.collectionName
        mybool = miscsettings.boolName
        
        translateColinCol(colname=mycolname, myloc=(myfx, myfy, myfz))
        
        return {'FINISHED'}
        
class Add_OT_Non_PBR_Mat(Operator):
    bl_label = "AddNonPBRMat"
    bl_idname = "object.addnonpbrmat"
    bl_description = "AddNonPBRMat"
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == "MESH"
    def execute(self, context):
        miscsettings = bpy.context.scene.misc_settings
        mymattypeidx = miscsettings.mattype
        print(mymattypeidx)
        myfx = miscsettings.locx
        myfy = miscsettings.locy
        myfz = miscsettings.locz
        myobject = bpy.context.object
        if mymattypeidx == "1":
            mymat = create_glass_mat()
            myobject.data.materials.clear()
            myobject.data.materials.append(mymat)
        elif mymattypeidx == "2":
            mymat = create_am_glass_mat('amglass', True, rv=myfx, gv=myfy, bv=myfz)
        
            myobject.data.materials.clear()
            myobject.data.materials.append(mymat)
        elif mymattypeidx == "3":
            dir_path = os.path.dirname(os.path.realpath(__file__))
            sub_path = r'.\img\earth001.png'
            myimg_path = os.path.join(dir_path, sub_path)
            print(myimg_path)
            mymat = createtransparentbackgroundphoto(imgpath=myimg_path)
            myobject.data.materials.clear()
            myobject.data.materials.append(mymat)
        elif mymattypeidx == "4":
            dir_path = os.path.dirname(os.path.realpath(__file__))
            sub_path = r'.\img\frames\caust_001.png'
            myimg_path = os.path.join(dir_path, sub_path)
            print(myimg_path)
            #mymat = createscifieffectmat(imgpath=myimg_path)
            mymat = createlightpollutionmat()
            myobject.data.materials.clear()
            myobject.data.materials.append(mymat)

        return {'FINISHED'}
        
class Add_OT_HDRI_Texture(Operator):
    bl_label = "AddHDRITexture"
    bl_idname = "object.addhdritexture"
    bl_description = "AddHDRITexture"
    

    
    def execute(self, context):
        miscsettings = bpy.context.scene.misc_settings
        mybool = miscsettings.boolName
        if mybool == True:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            sub_path = r'.\assets\HDRIs\rooitou_park_1k.hdr'
            myhdri_path = os.path.join(dir_path, sub_path)
            build_environment_black_background(hdri_path=myhdri_path, rotation=90.0)    
        else:
            genSkyTexutreBackground()
        return {'FINISHED'}

class Find_OT_KD_Tree_Shortest_Distance(Operator):
    bl_label = "FindKDTreeShortestDist"
    bl_idname = "object.findshortestdistbykdtree"
    bl_description = "FindKDTreeShortestDist"
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == "MESH"
    def execute(self, context):
        miscsettings = bpy.context.scene.misc_settings
        myfx = miscsettings.locx
        myfy = miscsettings.locy
        myfz = miscsettings.locz
        myobject = bpy.context.object
        
        genKDTree001(myobject, co_find=(myfx, myfy, myfz))
        return {'FINISHED'}

class Write_OT_Text_to_New_Location(Operator):
    bl_label = "WriteTextbyLoc"
    bl_idname = "object.writetext"
    bl_description = "WriteTextbyLoc"
    
    @classmethod
    def poll(cls, context):
        settings = bpy.context.scene.misc_settings
        mytxt = settings.textContent
        
        return len(mytxt) > 0
    
    def execute(self, context):
        miscsettings = bpy.context.scene.misc_settings
        myfx = miscsettings.locx
        myfy = miscsettings.locy
        myfz = miscsettings.locz
        mytxt = miscsettings.textContent
        mybool = miscsettings.boolName
        createText(text=mytxt, myloc=(myfx, myfy, myfz), myrotation_euler=(radians(90),0,0), myscale=(0.321,0.321,0.321), myextrude=0.05, mybeveldepth=0.01, isMesh=True)

        return {'FINISHED'}

class Add_OT_Cam_by_Image(Operator):
    bl_label = "AddCamImage"
    bl_idname = "object.addcameblenderimg"
    bl_description = "AddCamImage"
    
    def execute(self, context):
        miscsettings = bpy.context.scene.misc_settings
        myfx = miscsettings.locx
        myfy = miscsettings.locy
        myfz = miscsettings.locz
        mytxt = miscsettings.textContent
        mybool = miscsettings.boolName

        dir_path = os.path.dirname(os.path.realpath(__file__))
        sub_path = r'.\img\blender.png'
        myimg_path = os.path.join(dir_path, sub_path)

        genCamLightButton(myimgpath=myimg_path, isVertical=False, isButton=True, isImg=True, bText=mytxt)

        
        return {'FINISHED'}