import os
import Definitions

texture_maps = Definitions.DAZTOMAYA_MODULE_DIR + "/scripts/textures/"

texture_library = {
    "normal": {
        "Name": [
            "Normal Map",
        ],
    },
    "color": {
        "Name": [
            "Base Color",
            "Diffuse Color",
        ],
    },
    "bump": {
        "Name": [
            "Bump Strength",
        ],
    },
    "opacity": {
        "Name": [
            "Cutout Opacity",
            "Opacity Strength",
        ],
    },
    "roughness": {
        "Name": [
            "Glossy Roughness",
            "Specular Lobe 1 Roughness",
        ],
    },
    "specular": {
        "Name": [
            "Dual Lobe Specular Reflectivity",
            "Dual Lobe Specular Weight",
            "Specular 2 Color",
            "Specular Color",
            "Glossy Layered Weight",
        ],
    },
    "metalness": {
        "Name": [
            "Metallic Weight",
        ],
    },
    "transparency": {
        "Name": [
            "Refraction Weight",
        ]
    },
    "ior": {
        "Name": [
            "Refraction Index",
        ]
    },
    "sss": {
        "Name": [
            "Translucency Color",
        ]
    },
    "displacement": {
        "Name": [
            "Displacement Strength",
        ]
    },
    "displacement-height": {
        "Name": [
            "Maximum Displacement",
        ]
    },
    "detail-normal":{
        "Name": [
            "Detail Normal Map"
        ]
    },
    "detail-roughness":{
        "Name": [
            "Detail Specular Roughness Mult"
        ]
    },
    "detail-mask":{
        "Name": [
            "Detail Weight"
        ]
    },
    "sss-enabled":{
        "Name": [
            "Sub Surface Enable"
        ]
    },
    "sss-color":{
        "Name": [
            "SSS Color",
        ]
    },
    "sss-radius":{
        "Name": [
            "Transmitted Color"
        ]
    },
    "sss-scale":{
        "Name": [
            "Transmitted Measurement Distance"
        ]
    }
}
