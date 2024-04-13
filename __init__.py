bl_info = {
    "name": "Add Attribute",
    "blender": (3, 6, 5),
    "category": "Object",
    "author": "Hulifier, KSYN",
    "description": "Add or update the 'seam' attribute for selected mesh objects",
    "location": "View3D > UV Mapping",
    "warning": "",
    "doc_url": "https://blender.stackexchange.com/questions/269330/how-to-get-seams-as-an-edge-property-in-geometry-nodes",
    "support": "COMMUNITY",
    "version": (1, 0, 1),
    "blenderapi": (3, 6, 0),
    "update_check": False,  
    "category": "Mesh",  
}


import bpy
from mathutils import Vector

def add_attr(attributename,attributes,domain_type,attribute_type):
    if attribute_type=="FLOAT_VECTOR_AXIS":
        attribute_type="FLOAT_VECTOR"
    return attributes.new(name=attributename, type=attribute_type, domain=domain_type)

def set_attribute(mesh, attributename, attribute_value_getter, domain_type,attribute_type,domain_valuse,seam_bool):
    attribute = mesh.attributes.get(attributename)
    if attribute:
        if attribute_type=="FLOAT_VECTOR_AXIS":
            attribute_type="FLOAT_VECTOR"
        if attribute.data_type != attribute_type or attribute.domain != domain_type:
            mesh.attributes.remove(attribute)
            attribute = add_attr(attributename,mesh.attributes,domain_type,attribute_type)
    else:
        attribute = add_attr(attributename,mesh.attributes,domain_type,attribute_type)
    if attribute_type=="BOOLEAN" and seam_bool==True:

        attribute.data.foreach_set('value', attribute_value_getter(mesh))
    else:
        # print("###attribute_value_getter(mesh)",attribute_value_getter(mesh))
        for index,i in enumerate(attribute_value_getter(mesh)):
            if i:
     
                try:
                    if attribute_type=="FLOAT_VECTOR" or attribute_type =="FLOAT_VECTOR_AXIS": 
                        # print("###domain_valuse",domain_valuse)
                        mesh.attributes[attributename].data[index].vector = domain_valuse
                    # elif attribute_type=="FLOAT2": 
                    #     vector_3d = Vector(domain_valuse)
                    #     vector_2d = vector_3d.to_2d()
                    #     mesh.attributes[attributename].data[index].vector = vector_2d
                    #     bpy.ops.geometry.attribute_convert(domain='CORNER', data_type='FLOAT2')
                    elif attribute_type=="FLOAT_COLOR":

                        # print("###domain_valuse",domain_valuse)
                        # print("###mesh.attributes[attributename].data[index].color",mesh.attributes[attributename].data[index].color)
                        mesh.attributes[attributename].data[index].color = domain_valuse

                        
                    else:
                        mesh.attributes[attributename].data[index].value = domain_valuse
                except TypeError:
                    print("###type error",)
                    pass
        # attribute.data.foreach_set(1.0, attribute_value_getter(mesh))

    return mesh

# 列挙型のアイテムと説明の辞書
items = [
    ("POINT", "Point", "Point."),
    ("EDGE", "Edge", "Edge."),
    ("FACE", "Face", "Face."),
    # ("CORNER", "Face Corner", "Face Corner."),
    # ("CURVE", "Spline", "Spline."),
    # ("INSTANCE", "Instance", "Instance."),
    ]
# 列挙型のアイテムと説明の辞書
attribute_items = [
    ("FLOAT", "Float", "Floating-point value."),
    ("INT", "Integer", "32-bit integer."),
    ("FLOAT_VECTOR", "Vector", "3D vector with floating-point values."),
    ("FLOAT_VECTOR_AXIS", "Vector(axis)", "3D vector with floating-point values."),
    ("FLOAT_COLOR", "Color", "RGBA color with 32-bit floating-point values."),
    # ("BYTE_COLOR", "Byte Color", "RGBA color with 8-bit positive integer values."),
    # ("STRING", "String", "Text string."),
    ("BOOLEAN", "Boolean", "True or false."),
    # ("FLOAT2", "2D Vector", "2D vector with floating-point values."),
    # ("INT8", "8-Bit Integer", "Smaller integer with a range from -128 to 127."),
    # ("INT32_2D", "2D Integer Vector", "32-bit signed integer vector."),
    # ("QUATERNION", "Quaternion", "Floating point quaternion rotation."),
    ]

class AddSeamOperator(bpy.types.Operator):
    bl_idname = "object.add_seam_operator"
    bl_label = "Add Seam Attribute"
    bl_description = "Add or update the 'seam' attribute for selected mesh objects"
    bl_options = {'REGISTER', 'UNDO','PRESET'}
    domein_valuse=None
    add_seam: bpy.props.BoolProperty(name="add seam",default=True) # type: ignore
    add_custum_name: bpy.props.StringProperty(name="Add Custum Name",default="Attr")  # type: ignore
    use_face: bpy.props.BoolProperty(name="use face",default=False)  # type: ignore
    
    # プロパティ
    my_enum_property: bpy.props.EnumProperty(
        name="Attribute Domain Items",
        items=items,
        description="Select an attribute domain item"
    ) # type: ignore

    # プロパティ
    attribute_type_property: bpy.props.EnumProperty(
        name="Attribute Type Items",
        items=attribute_items,
        description="Select an attribute type item"
        ,default="BOOLEAN"
    ) # type: ignore

    domain_valuse : bpy.props.FloatProperty(name="Attribute Float valuse",
        description="",
        default=1.0
    ) # type: ignore

    domain_valuse_int : bpy.props.IntProperty(name="Attribute INT valuse",
        description="",
        default=1
    ) # type: ignore

    domain_valuse_boolean: bpy.props.BoolProperty(name="Attribute Boolean valuse",default=True) # type: ignore

    domain_valuse_vector:bpy.props.FloatVectorProperty(name="Attribute Vector valuse",subtype="XYZ") # type: ignore
    domain_valuse_vector_axis:bpy.props.FloatVectorProperty(name="Attribute Vector valuse",subtype="EULER") # type: ignore
    domain_valuse_vector_color:bpy.props.FloatVectorProperty(name="Attribute color valuse",
                                     subtype = "COLOR_GAMMA",
                                     size = 4,
                                     min = 0.0,
                                     max = 1.0,
                                     default = (0.75,0.0,0.8,1.0)
                                     )# type: ignore

    # domain_valuse_strings:bpy.props.StringProperty(name="Attribute String valuse") # type: ignore

    def draw(self, context):
    
        layout = self.layout
        # layout.label(text="領域分割:")
        layout.prop(self,"add_seam")
        if not self.add_seam:
            layout.prop(self,"my_enum_property")
            layout.prop(self,"attribute_type_property")
            if self.attribute_type_property=="FLOAT":
                layout.prop(self,"domain_valuse")
            elif self.attribute_type_property=="INT":
                layout.prop(self,"domain_valuse_int")
            elif self.attribute_type_property=="BOOLEAN":
                layout.prop(self,"domain_valuse_boolean")
            elif self.attribute_type_property=="FLOAT_VECTOR":
                layout.prop(self,"domain_valuse_vector")
            elif self.attribute_type_property=="FLOAT_VECTOR_AXIS":
                layout.prop(self,"domain_valuse_vector_axis")
            elif self.attribute_type_property=="FLOAT_COLOR":
                layout.prop(self,"domain_valuse_vector_color")
            # elif self.attribute_type_property=="STRING":
            #     layout.prop(self,"domain_valuse_strings")
  

            layout.prop(self,"add_custum_name")



    def execute(self, context):
        attributename="seam"
        if not self.add_seam:
            attributename=self.add_custum_name


        bpy.ops.object.mode_set(mode='OBJECT')

        obj = bpy.context.object

        if obj.type == 'MESH':
            mesh = obj.data

            if self.add_seam:
                # シームを設定する場合
                # Attribute Domain Items https://docs.blender.org/api/current/bpy_types_enum_items/attribute_domain_items.html#rna-enum-attribute-domain-items
                mesh = set_attribute(mesh, attributename, lambda mesh: [e.use_seam for e in mesh.edges], domain_type='EDGE', attribute_type="BOOLEAN",domain_valuse=self.domein_valuse, seam_bool=self.add_seam)
            else:
                attribute_type = self.attribute_type_property
                if self.attribute_type_property=="FLOAT":
                    self.domein_valuse=self.domain_valuse
                elif self.attribute_type_property=="INT":
                    self.domein_valuse=self.domain_valuse_int
                elif self.attribute_type_property=="BOOLEAN":
                    self.domein_valuse=self.domain_valuse_boolean
                elif self.attribute_type_property=="FLOAT_VECTOR":
                    self.domein_valuse=self.domain_valuse_vector
                elif self.attribute_type_property=="FLOAT_VECTOR_AXIS":
                    self.domein_valuse=self.domain_valuse_vector_axis
                elif self.attribute_type_property=="FLOAT_COLOR":
                    self.domein_valuse=self.domain_valuse_vector_color


                # カスタム名を設定する場合
                if self.my_enum_property=="EDGE":
                    mesh = set_attribute(mesh, attributename, lambda mesh: [e.select for e in mesh.edges] ,domain_type=self.my_enum_property, attribute_type=attribute_type,domain_valuse=self.domein_valuse, seam_bool=self.add_seam)
                elif self.my_enum_property=="FACE":
                    mesh = set_attribute(mesh, attributename, lambda mesh: [face.select for face in mesh.polygons] ,domain_type=self.my_enum_property, attribute_type=attribute_type,domain_valuse=self.domein_valuse, seam_bool=self.add_seam)
                elif self.my_enum_property=="POINT":
                    mesh = set_attribute(mesh, attributename, lambda mesh: [ver.select for ver in mesh.vertices] ,domain_type=self.my_enum_property, attribute_type=attribute_type,domain_valuse=self.domein_valuse ,seam_bool=self.add_seam)
  
            mesh.update()

        bpy.ops.object.mode_set(mode='EDIT')
        
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.separator()
    self.layout.operator(AddSeamOperator.bl_idname)

def register():
    bpy.utils.register_class(AddSeamOperator)
    bpy.types.VIEW3D_MT_uv_map.append(menu_func)

def unregister():
    bpy.utils.unregister_class(AddSeamOperator)
    bpy.types.VIEW3D_MT_uv_map.remove(menu_func)

if __name__ == "__main__":
    register()
