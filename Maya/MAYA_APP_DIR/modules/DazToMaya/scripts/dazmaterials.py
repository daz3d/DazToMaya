import os, sys

import pymel.core as pm
import maya.cmds  as cmds

from Definitions import EXPORT_DIR
from DtuLoader import DtuLoader
from TextureLib import texture_library, texture_maps



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
            return
        properties = {}
        for prop in self.material_dict[obj][mat]["Properties"]:
            if "Texture" in prop.keys():
                if (not os.path.isabs(prop["Texture"])) and (prop["Texture"] != ""):
                    prop["Texture"] = os.path.join(EXPORT_DIR, prop["Texture"])
            properties[prop["Name"]] = prop
        return properties

    """
    Reference for the standard followed.
    https://substance3d.adobe.com/tutorials/courses/Substance-guide-to-Rendering-in-Arnold
    """
    
    
    def convert_to_arnold(self):
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
                        # create shader and connect shader
                        surface = pm.shadingNode("aiStandardSurface", n = shader.name() + "_ai", asShader = True)
                        
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
                                        if props[tex_name]["Texture"] == "":
                                            continue
                                    avail_tex[tex_type] = tex_name

                        blend_color_node = None
                        clr_node = None
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
                                rgb_to_hsv_node = pm.shadingNode("rgbToHsv", n = "rgbToHsv", asUtility = True)
                                weight_node.outColor >> rgb_to_hsv_node.inRgb
                                rgb_to_hsv_node.outHsvV >> blend_color_node.blender
                                # makeup base
                                base_node = pm.shadingNode("file", n=makeup_base, asTexture = True)
                                base_node.setAttr('fileTextureName', props[makeup_base]["Texture"])
                                base_node.outColor >> blend_color_node.color1
                                # skin color
                                skin_node = pm.shadingNode("file", n = skin_color, asTexture = True)
                                skin_node.setAttr('fileTextureName',props[skin_color]["Texture"])
                                skin_node.outColor >> blend_color_node.color2

                        if "color" in avail_tex.keys() and blend_color_node is None:
                            prop = avail_tex["color"]
                            if props[prop]["Texture"] != "":
                                clr_node = pm.shadingNode("file", n = prop, asTexture = True)
                                clr_node.setAttr('fileTextureName',props[prop]["Texture"])
                                color_as_vector = self.convert_color(props[prop]["Value"])
                                clr_node.setAttr('colorGain', color_as_vector)
                                clr_node.outColor >> surface.baseColor
                            else:
                                color_as_vector = self.convert_color(props[prop]["Value"])
                                surface.setAttr('baseColor', color_as_vector)
                        
                        if "opacity" in avail_tex.keys():
                            prop = avail_tex["opacity"]
                            if props[prop]["Texture"] != "":
                                file_node = pm.shadingNode("file", n = prop, asTexture = True)
                                file_node.setAttr('fileTextureName',props[prop]["Texture"])
                                file_node.setAttr('colorSpace', 'Raw', type='string')
                                file_node.setAttr('alphaIsLuminance', True)
                                file_node.outColor >> surface.opacity
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
                        
                        if "roughness" in avail_tex.keys():
                            prop = avail_tex["roughness"]
                            if props[prop]["Texture"] != "":
                                file_node = pm.shadingNode("file", n = prop, asTexture = True)
                                file_node.setAttr('fileTextureName', props[prop]["Texture"])
                                file_node.setAttr('colorSpace', 'Raw', type='string')
                                file_node.setAttr('alphaIsLuminance', True)
                                file_node.outAlpha >> surface.specularRoughness
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

                        if "normal" in avail_tex.keys():
                            prop = avail_tex["normal"]
                            if props[prop]["Texture"] != "":
                                normal_map = pm.shadingNode("aiNormalMap", asUtility = True)
                                file_node = pm.shadingNode("file", n = prop, asTexture = True)
                                file_node.setAttr('fileTextureName', props[prop]["Texture"])
                                file_node.setAttr('colorSpace', 'Raw', type='string')
                                file_node.outColor >> normal_map.input
                                if float(props[prop]["Value"]) < 0:
                                   normal_map.setAttr('strength', (-1* float(props[prop]["Value"]))) 
                                   normal_map.setAttr('invertY', 1)
                                else:
                                    normal_map.setAttr('strength', float(props[prop]["Value"]))
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
                                if "normal" in avail_tex.keys():
                                    if props[avail_tex["normal"]]["Texture"] != "":
                                        normal_map.outValue >> bump_node.normal
                                bump_node.outValue >> surface.normalCamera           
                        
                        if "detail-mask" in avail_tex.keys():
                            uv_tile = pm.shadingNode("place2dTexture", asUtility = True)
                            uv_tile.setAttr('repeatU', props["Detail Horizontal Tiles"]['Value'])
                            uv_tile.setAttr('repeatV', props["Detail Vertical Tiles"]['Value'])

                            detail_normal_map = pm.shadingNode("aiNormalMap", asUtility = True)
                            nrm_node = pm.shadingNode("file", n = shader.name() + "_detail_nrm_tx", asTexture = True)
                            nrm_node.setAttr('fileTextureName', props[avail_tex['detail-normal']]["Texture"])
                            nrm_node.setAttr('colorSpace', 'Raw', type='string')
                            nrm_node.outColor >> detail_normal_map.input
                            uv_tile.outUV >> nrm_node.uvCoord

                            rgh_node = pm.shadingNode("file", n = shader.name() + "_detail_rough_tx", asTexture = True)
                            rgh_node.setAttr('fileTextureName', props[avail_tex['detail-roughness']]["Texture"])
                            rgh_node.setAttr('colorSpace', 'Raw', type='string')
                            rgh_node.setAttr('alphaIsLuminance', True)
                            uv_tile.outUV >> rgh_node.uvCoord
                            
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

    def update_phong_shaders(self):
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
                                        if props[tex_name]["Texture"] == "":
                                            continue
                                    avail_tex[tex_type] = tex_name

                        blend_color_node = None
                        clr_node = None
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
                                rgb_to_hsv_node = pm.shadingNode("rgbToHsv", n = "rgbToHsv", asUtility = True)
                                weight_node.outColor >> rgb_to_hsv_node.inRgb
                                rgb_to_hsv_node.outHsvV >> blend_color_node.blender
                                # makeup base
                                base_node = pm.shadingNode("file", n=makeup_base, asTexture = True)
                                base_node.setAttr('fileTextureName', props[makeup_base]["Texture"])
                                base_node.outColor >> blend_color_node.color1
                                # skin color
                                skin_node = pm.shadingNode("file", n = skin_color, asTexture = True)
                                skin_node.setAttr('fileTextureName',props[skin_color]["Texture"])
                                skin_node.outColor >> blend_color_node.color2

                        if "color" in avail_tex.keys() and blend_color_node is None:
                            prop = avail_tex["color"]
                            if props[prop]["Texture"] != "":
                                clr_node = pm.shadingNode("file", n = prop, asTexture = True)
                                clr_node.setAttr('fileTextureName',props[prop]["Texture"])
                                color_as_vector = self.convert_color(props[prop]["Value"])
                                clr_node.setAttr('colorGain', color_as_vector)
                                clr_node.outColor >> shader.color
                            else:
                                color_as_vector = self.convert_color(props[prop]["Value"])
                                shader.setAttr('color', color_as_vector)

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

                        # if "specular" in avail_tex.keys():
                        #     prop = avail_tex["specular"]
                        #     if props[prop]["Texture"] != "":
                        #         file_node = pm.shadingNode("file", n = prop, asTexture = True)
                        #         file_node.setAttr('fileTextureName', props[prop]["Texture"]) 
                        #         file_node.setAttr('colorSpace', 'Raw', type='string')
                        #         file_node.setAttr('alphaIsLuminance', True)
                        #         file_node.outColor >> shader.specularColor