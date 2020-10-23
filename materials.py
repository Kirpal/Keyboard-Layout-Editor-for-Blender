import bpy
from .helpers import hex2rgb


class Material:
    """Make and modify materials"""
    def __init__(self, name: str):
        self.name = name
        self.xpos = 0
        self.ypos = 0

        self.mat = bpy.data.materials.new(name)
        self.mat.use_nodes = True
        self.nodes = self.mat.node_tree.nodes
        # material output node
        self.output = self.nodes['Material Output']

    def link(self, from_node, from_slot_name, to_node, to_slot_name):
        input = to_node.inputs[to_slot_name]
        output = from_node.outputs[from_slot_name]
        self.mat.node_tree.links.new(input, output)

    def makeNode(self, type, name):
        self.node = self.nodes.new(type)
        self.node.name = name
        self.xpos += 200
        self.node.location = self.xpos, self.ypos
        return self.node


def make_key_material(color: str):
    """Make a glossy plastic material for keycaps, return the name"""
    if color not in bpy.data.materials:
        m = Material(color)

        # make new diffuse node
        diffuseBSDF = m.makeNode('ShaderNodeBsdfDiffuse', 'Diffuse BSDF')

        diffuseBSDF.inputs["Color"].default_value = hex2rgb(color)

        # add glossy node
        glossyBSDF = m.makeNode('ShaderNodeBsdfGlossy', 'Glossy BSDF')
        # set glossy node color to white and roughness to
        # 0.3
        glossyBSDF.inputs['Color'].default_value = [1, 1, 1, 1]
        glossyBSDF.inputs['Roughness'].default_value = 0.3
        # add mix node
        mixShader = m.makeNode('ShaderNodeMixShader', 'Mix Shader')
        # set mix node factor to 0.8
        mixShader.inputs['Fac'].default_value = 0.8
        # connect glossy and diffuse nodes to the mix node, and connect
        # that to the material output
        m.link(glossyBSDF, 'BSDF', mixShader, 1)
        m.link(diffuseBSDF, 'BSDF', mixShader, 2)
        m.link(mixShader, 'Shader', m.output, 'Surface')

    return color


def make_led_material(color: str, strength: float):
    """Make a glowing material for LEDs, return the name"""
    material_name = f'led: {color}'
    if material_name not in bpy.data.materials:
        m = Material(material_name)
        # make new emission node
        emission = m.makeNode('ShaderNodeEmission', 'Emission')
        # set color
        emission.inputs["Color"].default_value = hex2rgb(color)
        emission.inputs["Strength"].default_value = strength * 5

        # attach emission to material output
        m.link(emission, 'Emission', m.output, 'Surface')

    return material_name
