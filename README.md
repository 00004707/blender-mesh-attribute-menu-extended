# Mesh Attributes Menu eXtended
 Addon that extends Mesh Attributes menu in blender.



⚠️ EARLY VERSION/WORK IN PROGRESS, MANY FEATURES UNTESTED, NOT YET IMPLEMENTED 

but kinda works so feel free to test it

*Note: blender spreadsheet does not show the string values. The addon sets the values correctly.*

### Example use cases

<details> <summary>Use and create Shape Keys in Geometry Nodes</summary>
    Convert Shape Keys to Vector Attributes and use Set Position node to use the shape key
    <br>
	Create Shape Key Offset Vector Attributes to use with *Offset* input of Set Position node
</details>

<details> <summary>Create Sculpt Mask or Face Sets in Geometry Nodes</summary>
    Convert float vertex attributes to sculpt mode mask
    <br>
    Convert integer vertex attributes to face sets
</details>

<details> <summary>Use edge seams in Geometry Nodes</summary>
    Split mesh on UV islands by converting edge seams into edge boolean attribute
</details>

<details> <summary>Set color attribute to single face corner</summary>
    Using attribute assignment menu
</details>

<details> <summary>Create custom split normals in Geometry Nodes</summary>
    TODO
</details>

<details> <summary>Store multiple sculpt mode masks</summary>
    TODO
</details>

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

* Create attribute from 35 mesh data, including: Shape Keys, Edge Seam, Selection, Creases and more
* Support for any source domain, eg.: Mean Bevel for Vertices and edges
* Auto convert attribute upon creation

### Convert Attribute to Mesh Data

* **Boolean attributes**: selection, visibility in edit mode, seams, sharps, freestyle mark
* **Integer attributes**: sculpt mode face sets, material index, face map index
* **Float attributes**: mean bevel, crease, sculpt mode mask and vertex group

* **Vector attributes**: shape keys, normals or vertices position
