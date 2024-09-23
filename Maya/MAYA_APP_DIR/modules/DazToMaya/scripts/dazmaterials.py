import os, sys
import math

import pymel.core as pm
import maya.cmds  as cmds

from Definitions import EXPORT_DIR
from DtuLoader import DtuLoader
from TextureLib import texture_library, texture_maps


def cosinePowerToRoughness(cosinePower):
    if cosinePower <= 2:
        return 1.0
    return math.sqrt(2 / (cosinePower + 2))

def roughnessToCosinePower(roughness):
    if roughness <= 0:
        return 100
    return (2 / (roughness ** 2)) - 2

class DazMaterials:
    material_dict = {}
    keep_phong = False

    def __init__(self, keep_phong):
        self.keep_phong = keep_phong

    def convert_color(self, color):
        '''Takes a hex rgb string (e.g. #ffffff) and returns an RGB tuple (float, float, float).'''
        return tuple(int(color[i:i + 2], 16) / 255. for i in (1, 3, 5)) # skip '#'

    def load_materials(self):
        """
        Load materials from Dtu file
        """
        dtu_path = os.path.abspath(EXPORT_DIR + "/FIG/FIG0")
        dtu_loader = DtuLoader(dtu_path)
        mats = dtu_loader.get_materials_list()
        for mat in mats:
            asset_name = mat["Asset Name"]
            asset_name = asset_name.replace(" ", "_")
            mat_name = mat["Material Name"].replace(" ", "_")
            if asset_name not in self.material_dict.keys():
                self.material_dict[asset_name] = {}
            self.material_dict[asset_name][mat_name] = mat

    def get_materials_in_scene(self):
        # No need to pass in a string to `type`, if you don't want to.
        for shading_engine in pm.ls(type=pm.nt.ShadingEngine):
            # ShadingEngines are collections, so you can check against their length
            if len(shading_engine):
                # You can call listConnections directly on the attribute you're looking for.
                for material in shading_engine.surfaceShader.listConnections():
                    yield material

    def find_mat_properties(self, obj, mat):
        if obj not in self.material_dict.keys():
            return
        if mat not in self.material_dict[obj].keys():
            alt_mat = mat.split("_")[0]
            if alt_mat not in self.material_dict[obj].keys():
                return
            print("WARNING: Unable to find material: " + str(mat) + " in object: " + str(obj) + ", using: " + str(alt_mat))
            mat = alt_mat
        properties = {}
        for prop in self.material_dict[obj][mat]["Properties"]:
            if "Texture" in prop.keys():
                if (not os.path.isabs(prop["Texture"])) and (prop["Texture"] != ""):
                    prop["Texture"] = os.path.join(EXPORT_DIR, prop["Texture"])
            properties[prop["Name"]] = prop
        return properties

    ## DB 2024-09-21: update to work with new Bake Makeup feature in Daz Bridge Library, check for existence of weight and base color maps
    ## DB 2023-July-17: find if any HD makeup properties are present
    def has_hd_makeup(self):
        self.load_materials()
        bMakeupEnabled = False
        bHasWeightMap = False
        bHasBaseColorMap = False
        for obj in self.material_dict.keys():
            # print("DEBUG: HD Makeup check, obj=" + str(obj) )
            for mat in self.material_dict[obj].keys():
                # print("DEBUG: HD Makeup check, mat=" + str(mat) )
                for prop in self.material_dict[obj][mat]["Properties"]:
                    # print("DEBUG: HD Makeup check, prop=" + prop["Name"])
                    if "Name" in prop.keys() and prop["Name"] == "Makeup Enable":
                        if "Value" in prop.keys() and prop["Value"] == 1:
                            bMakeupEnabled = True
                    if "Name" in prop.keys() and prop["Name"] == "Makeup Weight":
                        if "Texture" in prop.keys() and prop["Texture"] != "":
                            bHasWeightMap = True
                    if "Name" in prop.keys() and prop["Name"] == "Makeup Base Color":
                        if "Texture" in prop.keys() and prop["Texture"] != "":
                            bHasBaseColorMap = True

        if (bMakeupEnabled and bHasWeightMap and bHasBaseColorMap):
            #print("DEBUG: HD Makeup found")
            return True
        else:
            return False

    """
    Reference for the standard followed.
    https://substance3d.adobe.com/tutorials/courses/Substance-guide-to-Rendering-in-Arnold
    """   
    
    def convert_to_arnold(self):
        allshaders = self.get_materials_in_scene()
        self.load_materials()
        
        for shader in allshaders:
            #print("DEBUG: convert_to_arnold(): shader=" + str(shader) )
            # get shading engine
            se = shader.shadingGroups()[0]
            shader_connections = shader.listConnections()
            # get assigned shapes
            members = se.members()
            
            if len(members) > 0:
                split = members[0].split("Shape")
                if len(split) > 1:
                    obj_name = split[0]
                    props = self.find_mat_properties(obj_name, shader.name())
                    #print("    - obj_name=" + str(obj_name) + ", shader.name()=" + str(shader.name()) + ", props=" + str(props) )

                    if props:
                        # create shader and connect shader
                        surface = pm.shadingNode("aiStandardSurface", n = shader.name() + "_ai", asShader = True)
                        #print("    - surface=" + str(surface) )
                        
                        # set material to shader
                        surface.outColor >> se.aiSurfaceShader
                        if not self.keep_phong:
                            surface.outColor >> se.surfaceShader
                        surface.base.set(1)

                        avail_tex = {}
                        for tex_type in texture_library.keys():
                            for tex_name in texture_library[tex_type]["Name"]:
                                if tex_name in props.keys():
                                    if tex_type in avail_tex.keys():
                                        existing_texture = props[avail_tex[tex_type]]["Texture"]
                                        # if tex_type already in lookup table, only override if tex_name has a texture or non-zero value
                                        if props[tex_name]["Texture"] == "" and existing_texture != "":
                                            continue
                                        elif props[tex_name]["Value"] == 0.0:
                                            continue
                                    avail_tex[tex_type] = tex_name

                        blend_color_node = None
                        clr_node = None
                        uv_tile = None

                        # set up UV tile scale
                        if "Horizontal Tiles" in props.keys() and "Vertical Tiles" in props.keys():
                            horizontal_tiles = props["Horizontal Tiles"]["Value"]
                            vertical_tiles = props["Vertical Tiles"]["Value"]
                            if horizontal_tiles != 1.0 or vertical_tiles != 1.0:
                                # print("DEBUG: update_phong_shaders_safe(): UV Tile found for material: " + str(shader.name()) + ", horizontal_tiles=" + str(horizontal_tiles) + ", vertical_tiles=" + str(vertical_tiles))
                                uv_tile = pm.shadingNode("place2dTexture", asUtility=True)
                                uv_tile.setAttr('repeatU', horizontal_tiles)
                                uv_tile.setAttr('repeatV', vertical_tiles)

                        if "makeup-weight" in avail_tex.keys() and "makeup-base" in avail_tex.keys() and "color" in avail_tex.keys():
                            makeup_weight = avail_tex["makeup-weight"]
                            makeup_base = avail_tex["makeup-base"]
                            skin_color = avail_tex["color"]
                            if props[makeup_weight]["Texture"] != "" and props[makeup_base]["Texture"] != "" and props[skin_color]["Texture"] != "":
                                # create blend color
                                blend_color_node = pm.shadingNode("blendColors", n = "makeup_blend", asUtility = True)
                                blend_color_node.output >> surface.baseColor
                                blend_color_node.output >> shader.color
                                # weight
                                weight_node = pm.shadingNode("file", n=makeup_weight, asTexture = True)
                                weight_node.setAttr('fileTextureName', props[makeup_weight]["Texture"])
                                scalar = float(props[makeup_weight]["Value"])
                                weight_node.setAttr('colorGain', [scalar, scalar, scalar])
                                weight_node.setAttr('colorSpace', 'Raw', type='string')
                                rgb_to_hsv_node = pm.shadingNode("rgbToHsv", n = "rgbToHsv", asUtility = True)
                                weight_node.outColor >> rgb_to_hsv_node.inRgb
                                rgb_to_hsv_node.outHsvV >> blend_color_node.blender
                                # makeup base
                                base_node = pm.shadingNode("file", n=makeup_base, asTexture = True)
                                base_node.setAttr('fileTextureName', props[makeup_base]["Texture"])
                                color_as_vector = self.convert_color(props[makeup_base]["Value"])
                                base_node.setAttr('colorGain', color_as_vector)
                                base_node.outColor >> blend_color_node.color1
                                # skin color
                                skin_node = pm.shadingNode("file", n = skin_color, asTexture = True)
                                skin_node.setAttr('fileTextureName',props[skin_color]["Texture"])
                                color_as_vector = self.convert_color(props[skin_color]["Value"])
                                skin_node.setAttr('colorGain', color_as_vector)
                                skin_node.outColor >> blend_color_node.color2
                                if uv_tile is not None:
                                    uv_tile.outUV >> weight_node.uvCoord
                                    uv_tile.outUV >> base_node.uvCoord
                                    uv_tile.outUV >> skin_node.uvCoord

                        if "color" in avail_tex.keys() and blend_color_node is None:
                            prop = avail_tex["color"]
                            if props[prop]["Texture"] != "":
                                clr_node = pm.shadingNode("file", n = prop, asTexture = True)
                                clr_node.setAttr('fileTextureName',props[prop]["Texture"])
                                color_as_vector = self.convert_color(props[prop]["Value"])
                                clr_node.setAttr('colorGain', color_as_vector)
                                clr_node.outColor >> surface.baseColor
                                if uv_tile is not None:
                                    uv_tile.outUV >> clr_node.uvCoord
                            else:
                                color_as_vector = self.convert_color(props[prop]["Value"])
                                surface.setAttr('baseColor', color_as_vector)
                        
                        if "opacity" in avail_tex.keys():
                            prop = avail_tex["opacity"]
                            if props[prop]["Texture"] != "":
                                file_node = pm.shadingNode("file", n = prop, asTexture = True)
                                file_node.setAttr('fileTextureName',props[prop]["Texture"])
                                scalar = float(props[prop]["Value"])
                                file_node.setAttr('colorGain', [scalar, scalar, scalar])
                                file_node.setAttr('colorSpace', 'Raw', type='string')
                                file_node.setAttr('alphaIsLuminance', True)
                                file_node.outColor >> surface.opacity
                                if uv_tile is not None:
                                    uv_tile.outUV >> file_node.uvCoord
                                cmds.setAttr('hardwareRenderingGlobals.transparencyAlgorithm', 5)

                        if "transparency" in avail_tex.keys():
                            prop = avail_tex["transparency"]
                            surface.setAttr('transmission', props[prop]["Value"])
                            color_as_vector = self.convert_color(props[avail_tex["color"]]["Value"])
                            surface.setAttr('transmissionColor', color_as_vector)

                        if "ior" in avail_tex.keys():
                            prop = avail_tex["ior"]
                            surface.setAttr('specularIOR', props[prop]["Value"])                            

                        if "metalness" in avail_tex.keys():
                            prop = avail_tex["metalness"]
                            if props[prop]["Texture"] != "":
                                file_node = pm.shadingNode("file", n = prop, asTexture = True)
                                file_node.setAttr('fileTextureName', props[prop]["Texture"])
                                file_node.setAttr('colorSpace', 'Raw', type='string')
                                file_node.setAttr('alphaIsLuminance', True)
                                file_node.outAlpha >> surface.metalness
                                if uv_tile is not None:
                                    uv_tile.outUV >> file_node.uvCoord
                        
                        if "roughness" in avail_tex.keys():
                            prop = avail_tex["roughness"]
                            if props[prop]["Texture"] != "":
                                file_node = pm.shadingNode("file", n = prop, asTexture = True)
                                file_node.setAttr('fileTextureName', props[prop]["Texture"])
                                file_node.setAttr('colorSpace', 'Raw', type='string')
                                file_node.setAttr('alphaIsLuminance', True)
                                file_node.outAlpha >> surface.specularRoughness
                                if uv_tile is not None:
                                    uv_tile.outUV >> file_node.uvCoord
                            else:
                                surface.setAttr('specularRoughness', props[prop]["Value"])

                        if "specular" in avail_tex.keys():
                            prop = avail_tex["specular"]
                            if props[prop]["Texture"] != "":
                                file_node = pm.shadingNode("file", n = prop, asTexture = True)
                                file_node.setAttr('fileTextureName', props[prop]["Texture"]) 
                                file_node.setAttr('colorSpace', 'Raw', type='string')
                                file_node.setAttr('alphaIsLuminance', True)
                                file_node.outColor >> surface.specularColor
                                if uv_tile is not None:
                                    uv_tile.outUV >> file_node.uvCoord

                        if "normal" in avail_tex.keys():
                            prop = avail_tex["normal"]
                            if props[prop]["Texture"] != "":
                                normal_map = pm.shadingNode("aiNormalMap", asUtility = True)
                                file_node = pm.shadingNode("file", n = prop, asTexture = True)
                                file_node.setAttr('fileTextureName', props[prop]["Texture"])
                                file_node.setAttr('colorSpace', 'Raw', type='string')
                                file_node.outColor >> normal_map.input
                                if uv_tile is not None:
                                    uv_tile.outUV >> file_node.uvCoord
                                normal_strength = props[prop]["Value"]
                                # detect if normal_strength is a hexadecimal string and convert to float
                                if type(normal_strength) == str:
                                    try:
                                        normal_strength = self.convert_color(normal_strength)[0]
                                    except Exception as e:
                                        print("Error: convert_to_arnold(): Error processing normal map: " + str(e) + ", setting normal_strength to 1.0")
                                        normal_strength = 1.0
                                if float(normal_strength) < 0:
                                   normal_map.setAttr('strength', (-1* float(normal_strength))) 
                                   normal_map.setAttr('invertY', 1)
                                else:
                                    normal_map.setAttr('strength', float(normal_strength))
                                normal_map.outValue >> surface.normalCamera             

                        if "bump" in avail_tex.keys():
                            prop = avail_tex["bump"]
                            if props[prop]["Texture"] != "":
                                bump_node = pm.shadingNode("aiBump2d", asUtility = True)
                                file_node = pm.shadingNode("file", n = shader.name() + "_" + prop + "_tx", asTexture = True)
                                file_node.setAttr('fileTextureName', props[prop]["Texture"])
                                file_node.setAttr('colorSpace', 'Raw', type='string')
                                file_node.setAttr('alphaIsLuminance', True)
                                file_node.outAlpha >> bump_node.bumpMap
                                if uv_tile is not None:
                                    uv_tile.outUV >> file_node.uvCoord
                                if "normal" in avail_tex.keys():
                                    if props[avail_tex["normal"]]["Texture"] != "":
                                        normal_map.outValue >> bump_node.normal
                                bump_node.outValue >> surface.normalCamera           
                        
                        if "detail-mask" in avail_tex.keys():
                            uv_tile2 = pm.shadingNode("place2dTexture", asUtility = True)
                            uv_tile2.setAttr('repeatU', props["Detail Horizontal Tiles"]['Value'])
                            uv_tile2.setAttr('repeatV', props["Detail Vertical Tiles"]['Value'])

                            detail_normal_map = pm.shadingNode("aiNormalMap", asUtility = True)
                            nrm_node = pm.shadingNode("file", n = shader.name() + "_detail_nrm_tx", asTexture = True)
                            nrm_node.setAttr('fileTextureName', props[avail_tex['detail-normal']]["Texture"])
                            nrm_node.setAttr('colorSpace', 'Raw', type='string')
                            nrm_node.outColor >> detail_normal_map.input
                            uv_tile2.outUV >> nrm_node.uvCoord

                            rgh_node = pm.shadingNode("file", n = shader.name() + "_detail_rough_tx", asTexture = True)
                            rgh_node.setAttr('fileTextureName', props[avail_tex['detail-roughness']]["Texture"])
                            rgh_node.setAttr('colorSpace', 'Raw', type='string')
                            rgh_node.setAttr('alphaIsLuminance', True)
                            uv_tile2.outUV >> rgh_node.uvCoord
                            
                            detail = pm.shadingNode("aiStandardSurface", n = shader.name() + "_detail_ai", asShader = True)
                            detail.base.set(1)
                            if clr_node:
                                clr_node.outColor >> detail.baseColor
                            elif blend_color_node:
                                blend_color_node.output >> detail.baseColor
                            normal_map.outValue >> detail.normalCamera 
                            rgh_node.outAlpha >> detail.specularRoughness

                            mix = pm.shadingNode("aiMixShader", n = shader.name() + "_mix_ai", asShader = True)
                            surface.outColor >> mix.shader1
                            detail.outColor >> mix.shader2
                            mix.setAttr('mode', 1)

                            if props[avail_tex['detail-mask']]["Texture"] != "":
                                msk_node = pm.shadingNode("file", asTexture = True)
                                msk_node.setAttr('fileTextureName', props[avail_tex['detail-mask']]["Texture"])
                                msk_node.setAttr('colorSpace', 'Raw', type='string')
                                msk_node.setAttr('alphaIsLuminance', True)
                                msk_node.setAttr('invert', 1)
                                msk_node.outAlpha >> mix.mix
                            else:
                                mix.setAttr('mix', props[avail_tex['detail-mask']]['Value'])

                            mix.outColor >> se.aiSurfaceShader

                        if "sss-radius" in avail_tex.keys():
                            if props[avail_tex["color"]]["Texture"] != "":
                                if clr_node:
                                    clr_node.outColor >> surface.subsurfaceColor
                                elif blend_color_node:
                                    blend_color_node.output >> surface.subsurfaceColor
                                if "detail-mask" in avail_tex.keys():
                                    if clr_node:
                                        clr_node.outColor >> detail.subsurfaceColor
                                    elif blend_color_node:
                                        blend_color_node.output >> detail.subsurfaceColor
                            else:
                                color_as_vector = self.convert_color(props[avail_tex["color"]]["Value"])
                                surface.setAttr("subsurfaceColor", color_as_vector)
                                if "detail-mask" in avail_tex.keys():
                                    detail.setAttr("subsurfaceColor", color_as_vector)
                            
                            radius_as_vector = self.convert_color(props[avail_tex["sss-radius"]]["Value"])
    
                            surface.base.set(0)
                            surface.setAttr("subsurface", 1)
                            surface.setAttr("subsurfaceRadius", radius_as_vector)
                            surface.setAttr("subsurfaceScale", 0.5)
                            if "detail-mask" in avail_tex.keys():
                                detail.base.set(0)
                                detail.setAttr("subsurface", 1)
                                detail.setAttr("subsurfaceRadius", radius_as_vector)
                                detail.setAttr("subsurfaceScale", 0.5)

                        if not self.keep_phong:
                            pm.delete(shader)

        #print("DEBUG: convert_to_arnold(): done")
        return

    ## DB 2023-July-17: safe shader update which will not break Maya's Fbx Exporter
    def update_phong_shaders_safe(self):
        allshaders = self.get_materials_in_scene()
        self.load_materials()
        
        for shader in allshaders:
            # get shading engine
            se = shader.shadingGroups()[0]
            shader_connections = shader.listConnections()
            # get assigned shapes
            members = se.members()
            
            if len(members) > 0:
                split = members[0].split("Shape")
                if len(split) > 1:
                    obj_name = split[0]
                    props = self.find_mat_properties(obj_name, shader.name())
                    
                    if props:

                        avail_tex = {}
                        for tex_type in texture_library.keys():
                            for tex_name in texture_library[tex_type]["Name"]:
                                if tex_name in props.keys():
                                    if tex_type in avail_tex.keys():
                                        existing_texture = props[avail_tex[tex_type]]["Texture"]
                                        # if tex_type already in lookup table, only override if tex_name has a texture or non-zero value
                                        if props[tex_name]["Texture"] == "" and existing_texture != "":
                                            continue
                                        elif props[tex_name]["Value"] == 0.0:
                                            continue
                                    avail_tex[tex_type] = tex_name

                        blend_color_node = None
                        clr_node = None
                        file_node = None
                        opacity_node = None
                        uv_tile = None

                        # set up UV tile scale
                        if "Horizontal Tiles" in props.keys() and "Vertical Tiles" in props.keys():
                            horizontal_tiles = props["Horizontal Tiles"]["Value"]
                            vertical_tiles = props["Vertical Tiles"]["Value"]
                            if horizontal_tiles != 1.0 or vertical_tiles != 1.0:
                                # print("DEBUG: update_phong_shaders_safe(): UV Tile found for material: " + str(shader.name()) + ", horizontal_tiles=" + str(horizontal_tiles) + ", vertical_tiles=" + str(vertical_tiles))
                                uv_tile = pm.shadingNode("place2dTexture", asUtility=True)
                                uv_tile.setAttr('repeatU', horizontal_tiles)
                                uv_tile.setAttr('repeatV', vertical_tiles)

                        if "color" in avail_tex.keys() and blend_color_node is None:
                            prop = avail_tex["color"]
                            if props[prop]["Texture"] != "":
                                clr_node = pm.shadingNode("file", n = prop, asTexture = True)
                                clr_node.setAttr('fileTextureName',props[prop]["Texture"])
                                color_as_vector = self.convert_color(props[prop]["Value"])
                                clr_node.setAttr('colorGain', color_as_vector)
                                clr_node.outColor >> shader.color
                                if uv_tile is not None:
                                    uv_tile.outUV >> clr_node.uvCoord
                            else:
                                color_as_vector = self.convert_color(props[prop]["Value"])
                                shader.setAttr('color', color_as_vector)

                        if "opacity" in avail_tex.keys():
                            prop = avail_tex["opacity"]
                            if props[prop]["Texture"] != "":
                                print("DEBUG: update_phong_shaders_safe(): opacity found for material: " + str(shader.name()))
                                opacity_node = pm.shadingNode("file", n = prop, asTexture = True)
                                opacity_node.setAttr('fileTextureName',props[prop]["Texture"])
                                scalar = float(props[prop]["Value"])
                                opacity_node.setAttr('alphaGain', scalar)
                                opacity_node.setAttr('colorSpace', 'Raw', type='string')
                                opacity_node.setAttr('alphaIsLuminance', True)
                                opacity_node.outTransparency >> shader.transparency
                                if uv_tile is not None:
                                    uv_tile.outUV >> opacity_node.uvCoord

                        # if "transparency" in avail_tex.keys():
                        #     prop = avail_tex["transparency"]
                        #     shader.setAttr('transmission', props[prop]["Value"])
                        #     color_as_vector = self.convert_color(props[avail_tex["color"]]["Value"])
                        #     shader.setAttr('transmissionColor', color_as_vector)

                        if "roughness" in avail_tex.keys():
                            prop = avail_tex["roughness"]
                            if props[prop]["Texture"] != "":
                                print("DEBUG: update_phong_shaders_safe(): roughness found for material: " + str(shader.name()))
                                file_node = pm.shadingNode("file", n = prop, asTexture = True)
                                file_node.setAttr('fileTextureName', props[prop]["Texture"])
                                scalar = float(props[prop]["Value"])
                                file_node.setAttr('alphaGain', scalar)
                                file_node.setAttr('colorSpace', 'Raw', type='string')
                                file_node.setAttr('alphaIsLuminance', True)
                                file_node.setAttr('invert', True)
                                file_node.outAlpha >> shader.cosinePower
                                if uv_tile is not None:
                                    uv_tile.outUV >> file_node.uvCoord
                            else:
                                # print("DEBUG: update_phong_shaders_safe(): no roughness image file, using roughness_val=" + str(props[prop]["Value"]) + ", for material: " + str(shader.name()))
                                roughness_val = props[prop]["Value"]
                                cosinePower_val = roughnessToCosinePower(roughness_val)
                                cosinePower_val = max(cosinePower_val, 2.0)
                                cosinePower_val = min(cosinePower_val, 100.0)
                                shader.setAttr('cosinePower', cosinePower_val)

                        if "normal" in avail_tex.keys():
                            prop = avail_tex["normal"]
                            if props[prop]["Texture"] != "":
                                bump_node = pm.shadingNode("bump2d", asUtility=True)
                                bump_node.bumpInterp.set(1)  # 1 = Tangent Space Normals
                                file_node = pm.shadingNode("file", n = prop, asTexture = True)
                                file_node.setAttr('fileTextureName', props[prop]["Texture"])
                                file_node.setAttr('colorSpace', 'Raw', type='string')
                                file_node.outAlpha >> bump_node.bumpValue  # Use outAlpha for normal maps
                                normal_strength = props[prop]["Value"]
                                # Adjust bump depth
                                if isinstance(normal_strength, str):
                                    try:
                                        normal_strength = self.convert_color(normal_strength)[0]
                                    except Exception as e:
                                        print("Error: update_phong_shaders_safe(): Error processing normal map: " + str(e) + ", setting normal_strength to 1.0")
                                        normal_strength = 1.0
                                bump_node.bumpDepth.set(float(normal_strength))
                                bump_node.outNormal >> shader.normalCamera
                                if uv_tile is not None:
                                    uv_tile.outUV >> file_node.uvCoord

                        if "metalness" in avail_tex.keys():
                            prop = avail_tex["metalness"]
                            if props[prop]["Texture"] != "":
                                print("DEBUG: update_phong_shaders_safe(): metalness found for material: " + str(shader.name()))
                                file_node = pm.shadingNode("file", n=prop, asTexture=True)
                                file_node.setAttr('fileTextureName', props[prop]["Texture"])
                                scalar = float(props[prop]["Value"])
                                file_node.setAttr('alphaGain', scalar)
                                file_node.setAttr('colorSpace', 'Raw', type='string')
                                file_node.setAttr('alphaIsLuminance', True)
                                file_node.outAlpha >> shader.reflectivity
                                if uv_tile is not None:
                                    uv_tile.outUV >> file_node.uvCoord
                            else:
                                shader.setAttr('reflectivity', props[prop]["Value"])

                        if "Refraction Weight" in props.keys():
                            refraction_weight = props["Refraction Weight"]["Value"]
                            if refraction_weight != 0.0:
                                print("DEBUG: update_phong_shaders_safe(): Refraction Weight found for material: " + str(shader.name()) + ", refraction_weight=" + str(refraction_weight))
                                # set transparency value
                                transparency_value = float(cmds.getAttr(shader + ".transparency")[0][0])
                                transparency_correction = max(transparency_value, refraction_weight)
                                transparency_correction = min(0.95, transparency_correction)
                                if transparency_value != transparency_correction:
                                    print("DEBUG: update_phong_shaders_safe(): Refraction Weight Handler: Setting transparency value to: " + str(transparency_correction))
                                    if opacity_node is None:
                                        try:
                                            cmds.setAttr(shader + ".transparency", transparency_correction, transparency_correction, transparency_correction)
                                        except Exception as e:
                                            print("DEBUG: update_phong_shaders_safe(): Refraction Weight Handler: Unable to set transparency value: " + str(e))
                                    else:
                                        alpha_correction = 1.05 - refraction_weight
                                        opacity_node.setAttr('alphaGain', alpha_correction)
                                # set metalness value
                                metalness_value = float(cmds.getAttr(shader + ".reflectivity"))
                                if metalness_value < refraction_weight:
                                    print("DEBUG: update_phong_shaders_safe(): Refraction Weight Handler: Setting metalness value to refraction_weight: " + str(refraction_weight))
                                    try:
                                        cmds.setAttr(shader + ".reflectivity", refraction_weight)
                                    except Exception as e:
                                        print("DEBUG: update_phong_shaders_safe(): Refraction Weight Handler: Unable to set metalness value: " + str(e))
                                # set roughness value
                                cosinePower_val = float(cmds.getAttr(shader + ".cosinePower"))
                                roughness_value = cosinePowerToRoughness(cosinePower_val)
                                new_roughness_value = roughness_value * (1.01 - refraction_weight)
                                new_cosinePower = roughnessToCosinePower(new_roughness_value)
                                new_cosinePower = max(new_cosinePower, 2.0)
                                new_cosinePower = min(new_cosinePower, 100.0)
                                if cosinePower_val != new_cosinePower:
                                    print("DEBUG: update_phong_shaders_safe(): Refraction Weight Handler: Setting roughness value to: " + str(new_roughness_value) + ", cosinePower=" + str(new_cosinePower))
                                    try:
                                        cmds.setAttr(shader + ".cosinePower", new_cosinePower)
                                    except Exception as e:
                                        print("DEBUG: update_phong_shaders_safe(): Refraction Weight Handler: Unable to set roughness value: " + str(e))
                                try:
                                    cmds.setAttr(shader + ".specularColor", 1.0, 1.0, 1.0, type="double3")
                                    cmds.setAttr(shader + ".reflectedColor", 0.01, 0.01, 0.01, type="double3")
                                except Exception as e:
                                    print("DEBUG: update_phong_shaders_safe(): Refraction Weight Handler: Unable to set specular and reflected color: " + str(e))
                                    
                        # if "specular" in avail_tex.keys():
                        #     prop = avail_tex["specular"]
                        #     if props[prop]["Texture"] != "":
                        #         file_node = pm.shadingNode("file", n = prop, asTexture = True)
                        #         file_node.setAttr('fileTextureName', props[prop]["Texture"]) 
                        #         file_node.setAttr('colorSpace', 'Raw', type='string')
                        #         file_node.setAttr('alphaIsLuminance', True)
                        #         file_node.outColor >> shader.specularColor

                        # print("DEBUG: update_phong_shaders_safe(): done for material: " + str(shader.name()))

        # print("DEBUG: update_phong_shaders_safe(): done")


    ## DB 2023-July-17: enhanced shader update which may break Maya's Fbx Exporter
    def update_phong_shaders_with_makeup(self):
        allshaders = self.get_materials_in_scene()
        self.load_materials()
        
        for shader in allshaders:
            # get shading engine
            se = shader.shadingGroups()[0]
            shader_connections = shader.listConnections()
            # get assigned shapes
            members = se.members()
            
            if len(members) > 0:
                split = members[0].split("Shape")
                if len(split) > 1:
                    obj_name = split[0]
                    props = self.find_mat_properties(obj_name, shader.name())
                    
                    if props:

                        avail_tex = {}
                        for tex_type in texture_library.keys():
                            for tex_name in texture_library[tex_type]["Name"]:
                                if tex_name in props.keys():
                                    if tex_type in avail_tex.keys():
                                        existing_texture = props[avail_tex[tex_type]]["Texture"]
                                        # if tex_type already in lookup table, only override if tex_name has a texture or non-zero value
                                        if props[tex_name]["Texture"] == "" and existing_texture != "":
                                            continue
                                        elif props[tex_name]["Value"] == 0.0:
                                            continue
                                    avail_tex[tex_type] = tex_name

                        blend_color_node = None
                        clr_node = None
                        file_node = None
                        opacity_node = None
                        uv_tile = None

                        # set up UV tile scale
                        if "Horizontal Tiles" in props.keys() and "Vertical Tiles" in props.keys():
                            horizontal_tiles = props["Horizontal Tiles"]["Value"]
                            vertical_tiles = props["Vertical Tiles"]["Value"]
                            if horizontal_tiles != 1.0 or vertical_tiles != 1.0:
                                # print("DEBUG: update_phong_shaders_safe(): UV Tile found for material: " + str(shader.name()) + ", horizontal_tiles=" + str(horizontal_tiles) + ", vertical_tiles=" + str(vertical_tiles))
                                uv_tile = pm.shadingNode("place2dTexture", asUtility=True)
                                uv_tile.setAttr('repeatU', horizontal_tiles)
                                uv_tile.setAttr('repeatV', vertical_tiles)

                        if "makeup-weight" in avail_tex.keys() and "makeup-base" in avail_tex.keys() and "color" in avail_tex.keys():
                            makeup_weight = avail_tex["makeup-weight"]
                            makeup_base = avail_tex["makeup-base"]
                            skin_color = avail_tex["color"]
                            if props[makeup_weight]["Texture"] != "" and props[makeup_base]["Texture"] != "" and props[skin_color]["Texture"] != "":
                                # create blend color
                                blend_color_node = pm.shadingNode("blendColors", n = "makeup_blend", asUtility = True)
                                blend_color_node.output >> shader.color
                                # weight
                                weight_node = pm.shadingNode("file", n=makeup_weight, asTexture = True)
                                weight_node.setAttr('fileTextureName', props[makeup_weight]["Texture"])
                                scalar = float(props[makeup_weight]["Value"])
                                weight_node.setAttr('colorGain', [scalar, scalar, scalar])
                                weight_node.setAttr('colorSpace', 'Raw', type='string')
                                rgb_to_hsv_node = pm.shadingNode("rgbToHsv", n = "rgbToHsv", asUtility = True)
                                weight_node.outColor >> rgb_to_hsv_node.inRgb
                                rgb_to_hsv_node.outHsvV >> blend_color_node.blender
                                # makeup base
                                base_node = pm.shadingNode("file", n=makeup_base, asTexture = True)
                                base_node.setAttr('fileTextureName', props[makeup_base]["Texture"])
                                color_as_vector = self.convert_color(props[makeup_base]["Value"])
                                base_node.setAttr('colorGain', color_as_vector)
                                base_node.outColor >> blend_color_node.color1
                                # skin color
                                skin_node = pm.shadingNode("file", n = skin_color, asTexture = True)
                                skin_node.setAttr('fileTextureName',props[skin_color]["Texture"])
                                color_as_vector = self.convert_color(props[skin_color]["Value"])
                                skin_node.setAttr('colorGain', color_as_vector)
                                skin_node.outColor >> blend_color_node.color2
                                if uv_tile is not None:
                                    uv_tile.outUV >> weight_node.uvCoord
                                    uv_tile.outUV >> base_node.uvCoord
                                    uv_tile.outUV >> skin_node.uvCoord

                        if "color" in avail_tex.keys() and blend_color_node is None:
                            prop = avail_tex["color"]
                            if props[prop]["Texture"] != "":
                                clr_node = pm.shadingNode("file", n = prop, asTexture = True)
                                clr_node.setAttr('fileTextureName',props[prop]["Texture"])
                                color_as_vector = self.convert_color(props[prop]["Value"])
                                clr_node.setAttr('colorGain', color_as_vector)
                                clr_node.outColor >> shader.color
                                if uv_tile is not None:
                                    uv_tile.outUV >> clr_node.uvCoord
                            else:
                                color_as_vector = self.convert_color(props[prop]["Value"])
                                shader.setAttr('color', color_as_vector)

                        if "opacity" in avail_tex.keys():
                            prop = avail_tex["opacity"]
                            if props[prop]["Texture"] != "":
                                opacity_node = pm.shadingNode("file", n = prop, asTexture = True)
                                opacity_node.setAttr('fileTextureName',props[prop]["Texture"])
                                scalar = float(props[prop]["Value"])
                                opacity_node.setAttr('alphaGain', scalar)
                                opacity_node.setAttr('colorSpace', 'Raw', type='string')
                                opacity_node.setAttr('alphaIsLuminance', True)
                                opacity_node.outTransparency >> shader.transparency
                                if uv_tile is not None:
                                    uv_tile.outUV >> opacity_node.uvCoord

                        if "roughness" in avail_tex.keys():
                            prop = avail_tex["roughness"]
                            if props[prop]["Texture"] != "":
                                file_node = pm.shadingNode("file", n = prop, asTexture = True)
                                file_node.setAttr('fileTextureName', props[prop]["Texture"])
                                scalar = float(props[prop]["Value"])
                                file_node.setAttr('alphaGain', scalar)
                                file_node.setAttr('colorSpace', 'Raw', type='string')
                                file_node.setAttr('alphaIsLuminance', True)
                                file_node.setAttr('invert', True)
                                file_node.outAlpha >> shader.cosinePower
                                if uv_tile is not None:
                                    uv_tile.outUV >> file_node.uvCoord
                            else:
                                roughness_val = props[prop]["Value"]
                                cosinePower_val = roughnessToCosinePower(roughness_val)
                                cosinePower_val = max(cosinePower_val, 2.0)
                                cosinePower_val = min(cosinePower_val, 100.0)
                                shader.setAttr('cosinePower', cosinePower_val)

                        if "normal" in avail_tex.keys():
                            prop = avail_tex["normal"]
                            if props[prop]["Texture"] != "":
                                bump_node = pm.shadingNode("bump2d", asUtility=True)
                                bump_node.bumpInterp.set(1)  # 1 = Tangent Space Normals
                                file_node = pm.shadingNode("file", n = prop, asTexture = True)
                                file_node.setAttr('fileTextureName', props[prop]["Texture"])
                                file_node.setAttr('colorSpace', 'Raw', type='string')
                                file_node.outAlpha >> bump_node.bumpValue  # Use outAlpha for normal maps
                                normal_strength = props[prop]["Value"]
                                # Adjust bump depth
                                if isinstance(normal_strength, str):
                                    try:
                                        normal_strength = self.convert_color(normal_strength)[0]
                                    except Exception as e:
                                        print("Error: update_phong_shaders_with_makeup(): Error processing normal map: " + str(e) + ", setting normal_strength to 1.0")
                                        normal_strength = 1.0
                                bump_node.bumpDepth.set(float(normal_strength))
                                bump_node.outNormal >> shader.normalCamera
                                if uv_tile is not None:
                                    uv_tile.outUV >> file_node.uvCoord

                        if "metalness" in avail_tex.keys():
                            prop = avail_tex["metalness"]
                            if props[prop]["Texture"] != "":
                                file_node = pm.shadingNode("file", n=prop, asTexture=True)
                                file_node.setAttr('fileTextureName', props[prop]["Texture"])
                                scalar = float(props[prop]["Value"])
                                file_node.setAttr('alphaGain', scalar)
                                file_node.setAttr('colorSpace', 'Raw', type='string')
                                file_node.setAttr('alphaIsLuminance', True)
                                file_node.outAlpha >> shader.reflectivity
                                if uv_tile is not None:
                                    uv_tile.outUV >> file_node.uvCoord
                            else:
                                shader.setAttr('reflectivity', props[prop]["Value"])

                        if "Refraction Weight" in props.keys():
                            refraction_weight = props["Refraction Weight"]["Value"]
                            # print("DEBUG: update_phong_shaders_with_makeup(): Refraction Weight found for material: " + str(shader.name()) + ", refraction_weight=" + str(refraction_weight))
                            if refraction_weight != 0.0:
                                transparency_value = float(cmds.getAttr(shader + ".transparency")[0][0])
                                if transparency_value < refraction_weight:
                                    if opacity_node is None:
                                        try:
                                            cmds.setAttr(shader + ".transparency", refraction_weight, refraction_weight, refraction_weight)
                                        except Exception as e:
                                            print("DEBUG: update_phong_shaders_with_makeup(): Refraction Weight Handler: Unable to set transparency value: " + str(e))
                                    else:
                                        # set alphaGain to 1-refraction_weight
                                        opacity_node.setAttr('alphaGain', 1-refraction_weight)                                        
                                # set metalness value
                                metalness_value = float(cmds.getAttr(shader + ".reflectivity"))
                                if metalness_value < refraction_weight:
                                    try:
                                        cmds.setAttr(shader + ".reflectivity", 1-refraction_weight)
                                    except Exception as e:
                                        print("DEBUG: update_phong_shaders_with_makeup(): Refraction Weight Handler: Unable to set metalness value: " + str(e))
                                cosinePower_val = float(cmds.getAttr(shader + ".cosinePower"))
                                roughness_value = cosinePowerToRoughness(cosinePower_val)
                                new_roughness_value = roughness_value * (1.0 - refraction_weight)
                                new_cosinePower = roughnessToCosinePower(new_roughness_value)
                                new_roughness_value = max(new_cosinePower, 2.0)
                                new_roughness_value = min(new_cosinePower, 100.0)
                                try:
                                    cmds.setAttr(shader + ".cosinePower", new_cosinePower)
                                except Exception as e:
                                    print("DEBUG: update_phong_shaders_with_makeup(): Refraction Weight Handler: Unable to set roughness value: " + str(e))
                                try:
                                    cmds.setAttr(shader + ".specularColor", 1.0, 1.0, 1.0, type="double3")
                                    cmds.setAttr(shader + ".reflectedColor", 1.0, 1.0, 1.0, type="double3")
                                except Exception as e:
                                    print("DEBUG: update_phong_shaders_with_makeup(): Refraction Weight Handler: Unable to set specular and reflected color: " + str(e))

                        # if "transparency" in avail_tex.keys():
                        #     prop = avail_tex["transparency"]
                        #     shader.setAttr('transmission', props[prop]["Value"])
                        #     color_as_vector = self.convert_color(props[avail_tex["color"]]["Value"])
                        #     shader.setAttr('transmissionColor', color_as_vector)

                        # if "roughness" in avail_tex.keys():
                        #     prop = avail_tex["roughness"]
                        #     if props[prop]["Texture"] != "":
                        #         file_node = pm.shadingNode("file", n = prop, asTexture = True)
                        #         file_node.setAttr('fileTextureName', props[prop]["Texture"])
                        #         scalar = float(props[prop]["Value"])
                        #         file_node.setAttr('alphaGain', scalar)
                        #         file_node.setAttr('colorSpace', 'Raw', type='string')
                        #         file_node.setAttr('alphaIsLuminance', True)
                        #         file_node.setAttr('invert', True)
                        #         multiply100 = pm.shadingNode("floatMath", asUtility = True)
                        #         multiply100.setAttr('operation', 2) # add=0, subtract, multiply, divide, min, max, power
                        #         multiply100.setAttr('floatB', 100.0)
                        #         file_node.outAlpha >> multiply100.floatA
                        #         clamp = pm.shadingNode("clamp", asUtility = True)
                        #         clamp.setAttr('min', [2.0, 2.0, 2.0])
                        #         clamp.setAttr('max', [100.0, 100.0, 100.0])
                        #         multiply100.outFloat >> clamp.inputR
                        #         clamp.outputR >> shader.cosinePower
                        #     else:
                        #         roughness_val = props[prop]["Value"]
                        #         cosinePower_val = (1.0 - roughness_val)*100.0
                        #         cosinePower_val = max(cosinePower_val, 2.0)
                        #         cosinePower_val = min(cosinePower_val, 100.0)
                        #         shader.setAttr('cosinePower', cosinePower_val)

                        # if "normal" in avail_tex.keys():
                        #     prop = avail_tex["normal"]
                        #     if props[prop]["Texture"] != "":
                        #         normal_map = pm.shadingNode("aiNormalMap", asUtility = True)
                        #         file_node = pm.shadingNode("file", n = prop, asTexture = True)
                        #         file_node.setAttr('fileTextureName', props[prop]["Texture"])
                        #         file_node.setAttr('colorSpace', 'Raw', type='string')
                        #         file_node.outColor >> normal_map.input
                        #         if float(props[prop]["Value"]) < 0:
                        #            normal_map.setAttr('strength', (-1* float(props[prop]["Value"]))) 
                        #            normal_map.setAttr('invertY', 1)
                        #         else:
                        #             normal_map.setAttr('strength', float(props[prop]["Value"]))
                        #         normal_map.outValue >> shader.normalCamera

                        # if "bump" in avail_tex.keys():
                        #     prop = avail_tex["bump"]
                        #     if props[prop]["Texture"] != "":
                        #         bump_node = pm.shadingNode("aiBump2d", asUtility = True)
                        #         file_node = pm.shadingNode("file", n = shader.name() + "_" + prop + "_tx", asTexture = True)
                        #         file_node.setAttr('fileTextureName', props[prop]["Texture"])
                        #         file_node.setAttr('colorSpace', 'Raw', type='string')
                        #         file_node.setAttr('alphaIsLuminance', True)
                        #         file_node.outAlpha >> bump_node.bumpMap
                        #         # if "normal" in avail_tex.keys():
                        #         #     if props[avail_tex["normal"]]["Texture"] != "":
                        #         #         normal_map.outValue >> bump_node.normal
                        #         bump_node.outValue >> shader.normalCamera

                        # if "specular" in avail_tex.keys():
                        #     prop = avail_tex["specular"]
                        #     if props[prop]["Texture"] != "":
                        #         file_node = pm.shadingNode("file", n = prop, asTexture = True)
                        #         file_node.setAttr('fileTextureName', props[prop]["Texture"]) 
                        #         file_node.setAttr('colorSpace', 'Raw', type='string')
                        #         file_node.setAttr('alphaIsLuminance', True)
                        #         file_node.outColor >> shader.specularColor
        return

    ## DB 2024-09-18: standard surface shader implementation
    def convert_to_standard_surface(self):
        allshaders = self.get_materials_in_scene()
        self.load_materials()
        
        for shader in allshaders:
            # get shading engine
            se = shader.shadingGroups()[0]
            shader_connections = shader.listConnections()
            # get assigned shapes
            members = se.members()
            
            if len(members) > 0:
                split = members[0].split("Shape")
                if len(split) > 1:
                    obj_name = split[0]
                    props = self.find_mat_properties(obj_name, shader.name())

                    if props:
                        # Create Standard Surface shader and connect to shading group
                        surface = pm.shadingNode("standardSurface", n=shader.name() + "_std", asShader=True)
                        
                        # Connect the shader to the shading group
                        surface.outColor >> se.surfaceShader
                        surface.base.set(1)
                        
                        avail_tex = {}
                        for tex_type in texture_library.keys():
                            for tex_name in texture_library[tex_type]["Name"]:
                                if tex_name in props.keys():
                                    if tex_type in avail_tex.keys():
                                        existing_texture = props[avail_tex[tex_type]]["Texture"]
                                        # if tex_type already in lookup table, only override if tex_name has a texture or non-zero value
                                        if props[tex_name]["Texture"] == "" and existing_texture != "":
                                            continue
                                        elif props[tex_name]["Value"] == 0.0:
                                            continue
                                    avail_tex[tex_type] = tex_name

                        blend_color_node = None
                        clr_node = None
                        uv_tile = None

                        # set up UV tile scale
                        if "Horizontal Tiles" in props.keys() and "Vertical Tiles" in props.keys():
                            horizontal_tiles = props["Horizontal Tiles"]["Value"]
                            vertical_tiles = props["Vertical Tiles"]["Value"]
                            if horizontal_tiles != 1.0 or vertical_tiles != 1.0:
                                # print("DEBUG: update_phong_shaders_safe(): UV Tile found for material: " + str(shader.name()) + ", horizontal_tiles=" + str(horizontal_tiles) + ", vertical_tiles=" + str(vertical_tiles))
                                uv_tile = pm.shadingNode("place2dTexture", asUtility=True)
                                uv_tile.setAttr('repeatU', horizontal_tiles)
                                uv_tile.setAttr('repeatV', vertical_tiles)

                        if "makeup-weight" in avail_tex.keys() and "makeup-base" in avail_tex.keys() and "color" in avail_tex.keys():
                            makeup_weight = avail_tex["makeup-weight"]
                            makeup_base = avail_tex["makeup-base"]
                            skin_color = avail_tex["color"]
                            if props[makeup_weight]["Texture"] != "" and props[makeup_base]["Texture"] != "" and props[skin_color]["Texture"] != "":
                                # Create blend color
                                blend_color_node = pm.shadingNode("blendColors", n="makeup_blend", asUtility=True)
                                blend_color_node.output >> surface.baseColor
                                # Weight
                                weight_node = pm.shadingNode("file", n=makeup_weight, asTexture=True)
                                weight_node.setAttr('fileTextureName', props[makeup_weight]["Texture"])
                                scalar = float(props[makeup_weight]["Value"])
                                weight_node.setAttr('colorGain', [scalar, scalar, scalar])
                                weight_node.setAttr('colorSpace', 'Raw', type='string')
                                rgb_to_hsv_node = pm.shadingNode("rgbToHsv", n="rgbToHsv", asUtility=True)
                                weight_node.outColor >> rgb_to_hsv_node.inRgb
                                rgb_to_hsv_node.outHsvV >> blend_color_node.blender
                                # Makeup base
                                base_node = pm.shadingNode("file", n=makeup_base, asTexture=True)
                                base_node.setAttr('fileTextureName', props[makeup_base]["Texture"])
                                color_as_vector = self.convert_color(props[makeup_base]["Value"])
                                base_node.setAttr('colorGain', color_as_vector)
                                base_node.outColor >> blend_color_node.color1
                                # Skin color
                                skin_node = pm.shadingNode("file", n=skin_color, asTexture=True)
                                skin_node.setAttr('fileTextureName', props[skin_color]["Texture"])
                                color_as_vector = self.convert_color(props[skin_color]["Value"])
                                skin_node.setAttr('colorGain', color_as_vector)
                                skin_node.outColor >> blend_color_node.color2
                                if uv_tile is not None:
                                    uv_tile.outUV >> weight_node.uvCoord
                                    uv_tile.outUV >> base_node.uvCoord
                                    uv_tile.outUV >> skin_node.uvCoord

                        if "color" in avail_tex.keys() and blend_color_node is None:
                            prop = avail_tex["color"]
                            if props[prop]["Texture"] != "":
                                clr_node = pm.shadingNode("file", n=prop, asTexture=True)
                                clr_node.setAttr('fileTextureName', props[prop]["Texture"])
                                color_as_vector = self.convert_color(props[prop]["Value"])
                                clr_node.setAttr('colorGain', color_as_vector)
                                clr_node.outColor >> surface.baseColor
                                if uv_tile is not None:
                                    uv_tile.outUV >> clr_node.uvCoord
                            else:
                                color_as_vector = self.convert_color(props[prop]["Value"])
                                surface.setAttr('baseColor', color_as_vector)

                        if "opacity" in avail_tex.keys():
                            prop = avail_tex["opacity"]
                            if props[prop]["Texture"] != "":
                                file_node = pm.shadingNode("file", n=prop, asTexture=True)
                                file_node.setAttr('fileTextureName', props[prop]["Texture"])
                                scalar = float(props[prop]["Value"])
                                file_node.setAttr('colorGain', [scalar, scalar, scalar])
                                file_node.setAttr('colorSpace', 'Raw', type='string')
                                file_node.setAttr('alphaIsLuminance', True)
                                file_node.outColor >> surface.opacity
                                if uv_tile is not None:
                                    uv_tile.outUV >> file_node.uvCoord
                                cmds.setAttr('hardwareRenderingGlobals.transparencyAlgorithm', 5)

                        if "transparency" in avail_tex.keys():
                            prop = avail_tex["transparency"]
                            surface.setAttr('transmission', props[prop]["Value"])
                            color_as_vector = self.convert_color(props[avail_tex["color"]]["Value"])
                            surface.setAttr('transmissionColor', color_as_vector)

                        if "ior" in avail_tex.keys():
                            prop = avail_tex["ior"]
                            surface.setAttr('specularIOR', props[prop]["Value"])                            

                        if "metalness" in avail_tex.keys():
                            prop = avail_tex["metalness"]
                            if props[prop]["Texture"] != "":
                                file_node = pm.shadingNode("file", n=prop, asTexture=True)
                                file_node.setAttr('fileTextureName', props[prop]["Texture"])
                                file_node.setAttr('colorSpace', 'Raw', type='string')
                                file_node.setAttr('alphaIsLuminance', True)
                                file_node.outAlpha >> surface.metalness
                                if uv_tile is not None:
                                    uv_tile.outUV >> file_node.uvCoord

                        if "roughness" in avail_tex.keys():
                            prop = avail_tex["roughness"]
                            if props[prop]["Texture"] != "":
                                file_node = pm.shadingNode("file", n=prop, asTexture=True)
                                file_node.setAttr('fileTextureName', props[prop]["Texture"])
                                file_node.setAttr('colorSpace', 'Raw', type='string')
                                file_node.setAttr('alphaIsLuminance', True)
                                file_node.outAlpha >> surface.specularRoughness
                                if uv_tile is not None:
                                    uv_tile.outUV >> file_node.uvCoord
                            else:
                                surface.setAttr('specularRoughness', props[prop]["Value"])

                        if "specular" in avail_tex.keys():
                            prop = avail_tex["specular"]
                            if props[prop]["Texture"] != "":
                                file_node = pm.shadingNode("file", n=prop, asTexture=True)
                                file_node.setAttr('fileTextureName', props[prop]["Texture"]) 
                                file_node.setAttr('colorSpace', 'Raw', type='string')
                                file_node.setAttr('alphaIsLuminance', True)
                                file_node.outColor >> surface.specularColor
                                if uv_tile is not None:
                                    uv_tile.outUV >> file_node.uvCoord

                        if "normal" in avail_tex.keys():
                            prop = avail_tex["normal"]
                            if props[prop]["Texture"] != "":
                                # Create a bump2d node for normal mapping
                                bump_node = pm.shadingNode("bump2d", asUtility=True)
                                bump_node.bumpInterp.set(1)  # 1 = Tangent Space Normals
                                file_node = pm.shadingNode("file", n=prop, asTexture=True)
                                file_node.setAttr('fileTextureName', props[prop]["Texture"])
                                file_node.setAttr('colorSpace', 'Raw', type='string')
                                file_node.outAlpha >> bump_node.bumpValue  # Use outAlpha for normal maps
                                if uv_tile is not None:
                                    uv_tile.outUV >> file_node.uvCoord
                                normal_strength = props[prop]["Value"]
                                # Adjust bump depth
                                if isinstance(normal_strength, str):
                                    try:
                                        normal_strength = self.convert_color(normal_strength)[0]
                                    except Exception as e:
                                        print("Error: convert_to_standard_surface(): Error processing normal map: " + str(e) + ", setting normal_strength to 1.0")
                                        normal_strength = 1.0
                                bump_node.bumpDepth.set(float(normal_strength))
                                bump_node.outNormal >> surface.normalCamera             

                        if "bump" in avail_tex.keys():
                            prop = avail_tex["bump"]
                            if props[prop]["Texture"] != "":
                                bump_node = pm.shadingNode("bump2d", asUtility=True)
                                bump_node.bumpInterp.set(0)  # 0 = Bump
                                file_node = pm.shadingNode("file", n=shader.name() + "_" + prop + "_tx", asTexture=True)
                                file_node.setAttr('fileTextureName', props[prop]["Texture"])
                                file_node.setAttr('colorSpace', 'Raw', type='string')
                                file_node.setAttr('alphaIsLuminance', True)
                                file_node.outAlpha >> bump_node.bumpValue
                                if uv_tile is not None:
                                    uv_tile.outUV >> file_node.uvCoord
                                bump_node.bumpDepth.set(props[prop]["Value"])
                                bump_node.outNormal >> surface.normalCamera           

                        if "sss-radius" in avail_tex.keys():
                            if "color" in avail_tex.keys():
                                if props[avail_tex["color"]]["Texture"] != "":
                                    if clr_node:
                                        clr_node.outColor >> surface.subsurfaceColor
                                    elif blend_color_node:
                                        blend_color_node.output >> surface.subsurfaceColor
                                else:
                                    color_as_vector = self.convert_color(props[avail_tex["color"]]["Value"])
                                    surface.setAttr("subsurfaceColor", color_as_vector)

                            radius_as_vector = self.convert_color(props[avail_tex["sss-radius"]]["Value"])
                            surface.base.set(0)
                            surface.setAttr("subsurface", 1)
                            surface.setAttr("subsurfaceRadius", radius_as_vector)
                            surface.setAttr("subsurfaceScale", 0.5)

                        if not self.keep_phong:
                            pm.delete(shader)

    ## DB 2024-09-18: Stingray PBS shader implementation
    def convert_to_stingray_pbs(self):
        allshaders = self.get_materials_in_scene()
        self.load_materials()
        
        for shader in allshaders:
            # Get shading engine
            se = shader.shadingGroups()[0]
            # Get assigned shapes
            members = se.members()
            
            if members:
                split = members[0].split("Shape")
                if len(split) > 1:
                    obj_name = split[0]
                    props = self.find_mat_properties(obj_name, shader.name())

                    if props:
                        # Create Stingray PBS shader and connect to shading group
                        surface = pm.shadingNode("StingrayPBS", n=shader.name() + "_stingray", asShader=True)
                                               
                        # Connect the shader to the shading group
                        surface.outColor >> se.surfaceShader

                        avail_tex = {}
                        for tex_type in texture_library.keys():
                            for tex_name in texture_library[tex_type]["Name"]:
                                if tex_name in props.keys():
                                    if tex_type in avail_tex.keys():
                                        existing_texture = props[avail_tex[tex_type]]["Texture"]
                                        # if tex_type already in lookup table, only override if tex_name has a texture or non-zero value
                                        if props[tex_name]["Texture"] == "" and existing_texture != "":
                                            continue
                                        elif props[tex_name]["Value"] == 0.0:
                                            continue
                                    avail_tex[tex_type] = tex_name

                        # Get the name of the shader node
                        shaderfx_node = surface.name()
                        
                        # Refresh the shader to initialize all attributes
                        pm.refresh()

                        # Define the path to the Standard_Transparent.sfx preset
                        standard_path = 'Scenes/StingrayPBS/Standard.sfx'
                        transparent_path = 'Scenes/StingrayPBS/Standard_Transparent.sfx'

                        clr_node = None
                        color_texture = None
                        opacity_texture = None
                        opacity_value = None
                        refraction_weight = None
                        transparent_preset_enabled = False

                        cmds.shaderfx(sfxnode=shaderfx_node, loadGraph=standard_path)
                        if 'opacity' in avail_tex:
                            prop = avail_tex['opacity']
                            opacity_texture = props[prop]['Texture']
                            opacity_value = props[prop]['Value']
                            if opacity_texture or opacity_value != 1.0:
                                transparent_preset_enabled = True
                                cmds.shaderfx(sfxnode=shaderfx_node, loadGraph=transparent_path)
                        if not transparent_preset_enabled and "Refraction Weight" in props.keys():
                            refraction_weight = props["Refraction Weight"]["Value"]
                            if refraction_weight != 0.0:
                                transparent_preset_enabled = True
                                cmds.shaderfx(sfxnode=shaderfx_node, loadGraph=transparent_path)

                        # set up UV tile scale
                        if "Horizontal Tiles" in props.keys() and "Vertical Tiles" in props.keys():
                            horizontal_tiles = props["Horizontal Tiles"]["Value"]
                            vertical_tiles = props["Vertical Tiles"]["Value"]
                            if horizontal_tiles != 1.0 or vertical_tiles != 1.0:
                                surface.setAttr('uv_scaleX', horizontal_tiles)
                                surface.setAttr('uv_scaleY', vertical_tiles)

                        # Assign textures and set attributes as before

                        if "color" in avail_tex:
                            prop = avail_tex["color"]
                            if props[prop]["Texture"]:
                                color_texture = props[prop]["Texture"]
                                # Create file node
                                clr_node = pm.shadingNode("file", n=prop + "_file", asTexture=True)
                                clr_node.setAttr('fileTextureName', props[prop]["Texture"])
                                clr_node.setAttr('colorSpace', 'sRGB', type='string')
                                # Connect outColor to base_color
                                clr_node.outColor >> surface.TEX_color_map
                                # Enable the color map
                                surface.use_color_map.set(True)
                            else:
                                color_as_vector = self.convert_color(props[prop]["Value"])
                                surface.base_color.set(color_as_vector)
                                surface.use_color_map.set(False)

                        # WARNING: StingrayPBS requires opacity map to be carried as an alpha channel of color map
                        if "opacity" in avail_tex:
                            prop = avail_tex["opacity"]
                            if opacity_texture and clr_node:
                                if opacity_texture == color_texture:
                                    surface.use_opacity_map.set(True)
                                else:
                                    # ERROR: can not have separate opacity and color maps, FAIL
                                    print("ERROR: convert_to_stingray_pbs(): Separate opacity and color maps not supported for material: " + str(shader.name()) + ", keeping color map and setting opacity to 0.5")
                                    surface.opacity.set(0.5)
                                    surface.use_opacity_map.set(False)
                            elif opacity_texture and clr_node is None:
                                print("ERROR: convert_to_stingray_pbs(): Opacity map found without color map for material: " + str(shader.name()) + ", using opacity map as stand-in for color map and setting opacity to 0.5")
                                # create an opacity node to be stand in for the color node
                                opacity_node = pm.shadingNode("file", n=prop + "_file", asTexture=True)
                                opacity_node.setAttr('fileTextureName', opacity_texture)
                                opacity_node.setAttr('colorSpace', 'Raw', type='string')
                                opacity_node.outColor >> surface.TEX_color_map
                                surface.opacity.set(0.5)
                                surface.use_color_map.set(True)
                                surface.use_opacity_map.set(False)
                            elif (opacity_value and opacity_value != 1.0):
                                surface.opacity.set(opacity_value)
                                surface.use_opacity_map.set(False)

                        if "metalness" in avail_tex.keys():
                            prop = avail_tex["metalness"]
                            if props[prop]["Texture"] != "":
                                file_node = pm.shadingNode("file", n=prop, asTexture=True)
                                file_node.setAttr('fileTextureName', props[prop]["Texture"])
                                file_node.setAttr('colorSpace', 'Raw', type='string')
                                surface.setAttr('use_metallic_map', True)
                                file_node.outColor >> surface.TEX_metallic_map
                            else:
                                surface.setAttr('metallic', props[prop]["Value"])
                        
                        if "roughness" in avail_tex.keys():
                            prop = avail_tex["roughness"]
                            if props[prop]["Texture"] != "":
                                file_node = pm.shadingNode("file", n=prop, asTexture=True)
                                file_node.setAttr('fileTextureName', props[prop]["Texture"])
                                file_node.setAttr('colorSpace', 'Raw', type='string')
                                surface.setAttr('use_roughness_map', True)
                                file_node.outColor >> surface.TEX_roughness_map
                            else:
                                surface.setAttr('roughness', props[prop]["Value"])

                        if "normal" in avail_tex.keys():
                            prop = avail_tex["normal"]
                            if props[prop]["Texture"] != "":
                                # Create a normal map node
                                file_node = pm.shadingNode("file", n=prop, asTexture=True)
                                file_node.setAttr('fileTextureName', props[prop]["Texture"])
                                file_node.setAttr('colorSpace', 'Raw', type='string')
                                surface.setAttr('use_normal_map', True)
                                file_node.outColor >> surface.TEX_normal_map

                        if "ao" in avail_tex.keys():
                            prop = avail_tex["ao"]
                            if props[prop]["Texture"] != "":
                                ao_node = pm.shadingNode("file", n=prop, asTexture=True)
                                ao_node.setAttr('fileTextureName', props[prop]["Texture"])
                                ao_node.setAttr('colorSpace', 'Raw', type='string')
                                surface.setAttr('use_ao_map', True)
                                ao_node.outColor >> surface.TEX_ao_map

                        if "Refraction Weight" in props.keys():
                            refraction_weight = props["Refraction Weight"]["Value"]
                            transparency_correction = 1.01-refraction_weight
                            if refraction_weight != 0.0:
                                print("DEBUG: convert_to_stingray_pbs(): Refraction Weight found for material: " + str(shader.name()) + ", refraction_weight=" + str(refraction_weight))
                                opacity_value = float(surface.opacity.get())
                                # print("DEBUG: convert_to_stingray_pbs(): Refraction Weight Handler: opacity_value=" + str(opacity_value))
                                if opacity_value > transparency_correction:
                                    try:
                                        surface.opacity.set(transparency_correction)
                                    except Exception as e:
                                        print("DEBUG: convert_to_stingray_pbs(): Refraction Weight Handler: Unable to set opacity value: " + str(e))
                                
                                # if transparency_value < refraction_weight:
                                #     if opacity_node is None:
                                #         try:
                                #             cmds.setAttr(shader + ".transparency", refraction_weight, refraction_weight, refraction_weight)
                                #         except Exception as e:
                                #             print("DEBUG: convert_to_stingray_pbs(): Refraction Weight Handler: Unable to set transparency value: " + str(e))
                                #     else:
                                #         # set alphaGain to 1-refraction_weight
                                #         opacity_node.setAttr('alphaGain', 1-refraction_weight)                                        
                                # # set metalness value
                                # metalness_value = float(cmds.getAttr(shader + ".reflectivity"))
                                # if metalness_value < refraction_weight:
                                #     try:
                                #         cmds.setAttr(shader + ".reflectivity", 1-refraction_weight)
                                #     except Exception as e:
                                #         print("DEBUG: convert_to_stingray_pbs(): Refraction Weight Handler: Unable to set metalness value: " + str(e))
                                # cosinePower_val = float(cmds.getAttr(shader + ".cosinePower"))
                                # roughness_value = cosinePowerToRoughness(cosinePower_val)
                                # new_roughness_value = roughness_value * (1.0 - refraction_weight)
                                # new_cosinePower = roughnessToCosinePower(new_roughness_value)
                                # new_roughness_value = max(new_cosinePower, 2.0)
                                # new_roughness_value = min(new_cosinePower, 100.0)
                                # try:
                                #     cmds.setAttr(shader + ".cosinePower", new_cosinePower)
                                # except Exception as e:
                                #     print("DEBUG: convert_to_stingray_pbs(): Refraction Weight Handler: Unable to set roughness value: " + str(e))
                                # try:
                                #     cmds.setAttr(shader + ".specularColor", 1.0, 1.0, 1.0, type="double3")
                                #     cmds.setAttr(shader + ".reflectedColor", 1.0, 1.0, 1.0, type="double3")
                                # except Exception as e:
                                #     print("DEBUG: convert_to_stingray_pbs(): Refraction Weight Handler: Unable to set specular and reflected color: " + str(e))

                        # Handle other properties as needed

                        if not self.keep_phong:
                            pm.delete(shader)
