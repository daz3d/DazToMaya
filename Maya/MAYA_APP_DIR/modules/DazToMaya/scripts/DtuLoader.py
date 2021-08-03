import os
import json


class DtuLoader:
    """
    Loader to Store the Necessary information from the Companion JSON into Memory
    """

    dtu_dict = dict()
    bone_limits_dict = dict()
    skeleton_data_dict = dict()
    pose_data_dict = dict()
    bone_head_tail_dict = dict()
    morph_links_dict = dict()
    joint_orientation_dict = dict()
    asset_name = ""
    fbx_path = ""
    subdivsion_level = ""
    materials_list = []

    def __init__(self, imported_dir):
        self.import_dir = imported_dir

    def load_dtu(self):
        for file in os.listdir(self.import_dir):
            if file.endswith(".dtu"):
                dtu = os.path.join(self.import_dir, file)
                break
        with open(dtu, "r") as data:
            self.dtu_dict = json.load(data)

    def get_dtu_dict(self):
        if len(self.dtu_dict.keys()) == 0:
            self.load_dtu()
        return self.dtu_dict

    def load_dtu_dict(self, dtu_dict):
        self.dtu_dict = dtu_dict
        return self.dtu_dict

    def load_asset_name(self):
        dtu_dict = self.get_dtu_dict()
        self.asset_name = dtu_dict["Asset Name"]

    def get_asset_name(self):
        if self.asset_name == "":
            self.load_asset_name()
        return self.asset_name

    def load_import_name(self):
        dtu_dict = self.get_dtu_dict()
        self.asset_name = dtu_dict["Import Name"]

    def get_import_name(self):
        if self.asset_name == "":
            self.load_import_name()
        return self.asset_name

    def load_fbx_path(self):
        dtu_dict = self.get_dtu_dict()
        self.fbx_path = os.path.abspath(dtu_dict["FBX File"])

    def get_fbx_path(self):
        if self.asset_name == "":
            self.load_fbx_path()
        return self.fbx_path

    def load_subdivision(self):
        dtu_dict = self.get_dtu_dict()
        self.subdivision = dtu_dict["Subdivision"]

    def get_subdivision(self):
        if self.subdivsion_level == "":
            self.load_subdivision()
        return self.subdivision

    def load_bone_head_tail_dict(self):
        dtu_dict = self.get_dtu_dict()
        self.bone_head_tail_dict = dtu_dict["HeadTailData"]

    def get_bone_head_tail_dict(self):
        if len(self.bone_head_tail_dict.keys()) == 0:
            self.load_bone_head_tail_dict()
        return self.bone_head_tail_dict

    def load_joint_orientation_dict(self):
        dtu_dict = self.get_dtu_dict()
        self.joint_orientation_dict = dtu_dict["JointOrientation"]

    def get_joint_orientation_dict(self):
        if len(self.joint_orientation_dict.keys()) == 0:
            self.load_joint_orientation_dict()
        return self.joint_orientation_dict

    def load_bone_limits_dict(self):
        dtu_dict = self.get_dtu_dict()
        self.bone_limits_dict = dtu_dict["LimitData"]

    def get_bone_limits_dict(self):
        if len(self.bone_limits_dict.keys()) == 0:
            self.load_bone_limits_dict()
        return self.bone_limits_dict

    def load_skeleton_data_dict(self):
        dtu_dict = self.get_dtu_dict()
        self.skeleton_data_dict = dtu_dict["SkeletonData"]

    def get_skeleton_data_dict(self):
        if len(self.skeleton_data_dict.keys()) == 0:
            self.load_skeleton_data_dict()
        return self.skeleton_data_dict

    def load_pose_data_dict(self):
        dtu_dict = self.get_dtu_dict()
        data = dtu_dict["PoseData"]
        for key in data:
            if key.startswith("Genesis"):
                new_key = "root"
                data[key]["Name"] = new_key
                data[key]["Object Type"] = "BONE"
                data[new_key] = data[key]
                del data[key]
                break

        self.pose_data_dict = dtu_dict["PoseData"]

    def get_pose_data_dict(self):
        if len(self.pose_data_dict.keys()) == 0:
            self.load_pose_data_dict()
        return self.pose_data_dict

    def load_materials_list(self):
        dtu_dict = self.get_dtu_dict()
        self.materials_list = dtu_dict["Materials"]

    def get_materials_list(self):
        if len(self.materials_list) == 0:
            self.load_materials_list()
        return self.materials_list

    def load_morph_links_dict(self):
        dtu_dict = self.get_dtu_dict()
        self.morph_links_dict = dtu_dict["MorphLinks"]

    def get_morph_links_dict(self):
        if len(self.morph_links_dict.keys()) == 0:
            self.load_morph_links_dict()
        return self.morph_links_dict
