# Mesh Attributes Menu eXtended
 Addon that extends Mesh Attributes menu in blender.



⚠️ EARLY VERSION/WORK IN PROGRESS, MANY FEATURES UNTESTED, NOT YET IMPLEMENTED 

but kinda works so feel free to test it

### Set Attribute Values For selection in Edit Mode

![Attribute Set](https://i.imgur.com/c8e9oF7.png)

* Supports any data type and all domains (vertex, edge, face, face corner)

* Allows assigning value to individual face corners based on edge selection, or "spillling" the value to near face corners

![Face Spill](https://i.imgur.com/YQyma0i.png)

### Duplicate Attribute

* Duplicate active attribute

### Invert Attribute

* Inverts attribute value
  * Integer/Int8: multiply by -1
  * Float, Vector, Color: Subtract from 1, add to -1, multiply by -1
  * Boolean: NOT operation

### Create Attribute From Mesh Data

![Attribute Set](https://i.imgur.com/5QfmyCo.png)

* Create data from 35 mesh data, including: Shape Keys, Edge Seam, Selection, Creases and more
* Support for any source domain, eg.: Mean Bevel for Vertices and edges
* Auto convert attribute upon creation

### Convert Attribute to Mesh Data

* **Boolean attributes**: selection, visibility in edit mode, seams, sharps, freestyle mark
* **Integer attributes**: sculpt mode face sets, material index, face map index
* **Float attributes**: mean bevel, crease, sculpt mode mask and vertex group

* **Vector attributes**: shape keys, normals or vertices position
