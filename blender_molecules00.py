import numpy as np
import bpy
from bpy import data as D
from bpy import context as C

"""
#~ PYTHON INTERACTIVE CONSOLE 3.7.4 (default, Oct  8 2019, 15:23:02)
[GCC 6.3.1 20170216 (Red Hat 6.3.1-3)]
Command History:     Up/Down Arrow
Cursor:              Left/Right Home/End
Remove:              Backspace/Delete
Execute:             Enter
Autocomplete:        Ctrl-Space
Zoom:                Ctrl +/-, Ctrl-Wheel
Builtin Modules:     bpy, bpy.data, bpy.ops, bpy.props, bpy.types,
                     bpy.context, bpy.utils, bgl, blf, mathutils
Convenience Imports: from mathutils import *; from math import *
Convenience Variables: C = bpy.context, D = bpy.data

To debug a python script, run blender script from the command line:
blender --background --python blender_molecules00.py

"""

# enable rigid body world
#bpy.ops.rigidbody.world_add()


# ---------------- INITIALIZE ENVIRONMENT ----------------------

# select all objects and delete them
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# add light source
bpy.ops.object.light_add(type='SUN', radius=1.0, location=(0, 2, 2))
bpy.context.object.name = 'lamp'

# add camera
cam_pos = [0, 0, 10]
cam_rot = [0, 0, 0]
bpy.ops.object.camera_add(location=cam_pos, rotation=cam_rot)
bpy.context.object.name = 'cam'

# --------- CREATE MOLECULES -------------------------

# set current position
x, y, z = 0, 0, 0

# order in which molecule was created
mol_num = 0

for i in range(7):
    for j in range(7):
        for k in range(7):

            # add sphere
            bpy.ops.mesh.primitive_uv_sphere_add(location=(x+i, y+j, z+k), radius=0.1)
            # name sphere
            bpy.context.object.name = 'molecule_' + str(mol_num).zfill(3)
            # set sphere rendering smooth
            bpy.ops.object.shade_smooth()
            # make sphere a rigid object
            #bpy.context.scene.objects.active.rigid_body.type=True
            #bpy.context.object.rigid_body.type=True

            mol_num += 1