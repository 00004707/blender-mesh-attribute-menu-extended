# Mesh Attributes Menu eXtended
![Static Badge](https://img.shields.io/badge/blender-3.1.0%2B-orange)

 Addon that extends Mesh Attributes menu in blender.

[Take me to the downloads](https://github.com/00004707/blender-mesh-attribute-menu-extended/releases/)


## Examples 

### Use cases

<details> <summary>Selecting points on which instances will appear in Geometry Nodes</summary>
 <p align="center">
 
  https://github.com/00004707/blender-mesh-attribute-menu-extended/assets/117545764/9e0e5101-9cfa-42d9-913b-c0cc15b527fa

</p>
</details>

<details> <summary>Invering points selection in Geometry Nodes</summary>
    <p align="center">


https://github.com/00004707/blender-mesh-attribute-menu-extended/assets/117545764/4c9b79bd-5bbc-4ed6-ac16-8a9bfd1dbbf4


</p>

</details>

<details> <summary>Use and create Shape Keys in Geometry Nodes</summary>
    <p align="center">



https://github.com/00004707/blender-mesh-attribute-menu-extended/assets/117545764/f8df6eee-7320-4625-bb88-a907302fcd93



</p>
    <ul><li>Create Shape Key Position Vector Attributes and use Set Position node</li>
          <li>Create Shape Key Offset Vector Attributes to use with Offset input of Set Position node</li>
</ul>
</details>

<details> <summary>Create Sculpt Mask or Face Sets in Geometry Nodes</summary>
    <p align="center">




https://github.com/00004707/blender-mesh-attribute-menu-extended/assets/117545764/0235c907-5bc8-4112-aeab-b0a956ffa58b


</p>
    <ul>
        <li>Convert float vertex attributes to sculpt mode mask</li>
        <li>Convert integer vertex attributes to face sets</li>
    </ul>
    <br>
</details>

<details> <summary>Use edge seams in Geometry Nodes</summary>
    <p align="center">




https://github.com/00004707/blender-mesh-attribute-menu-extended/assets/117545764/13dd6501-ba71-4c9e-96b4-0acb196d6217


</p>
    <ul>
    <li>Convert edge seams to boolean edge attribute</li>
    </ul>
</details>

<details> <summary>Set color attribute to single face corner</summary>
    <p align="center">

https://github.com/00004707/blender-mesh-attribute-menu-extended/assets/117545764/5db821ce-1a01-4868-a2f2-ad677fec9a36



 </p>

<ul>
<li>Using attribute value assignment menu</li>
</ul>
</details>

<details> <summary>Create custom split normals in Geometry Nodes</summary>
    <p align="center">
  <img width="600" src="https://i.imgur.com/dEkRTRM.png">
</p>
    <ul>
        <li>Assign custom split normals created in geometry nodes to mesh</li>
    </ul>
</details>

<details> <summary>Store multiple sculpt mode masks</summary>
    <p align="center">




https://github.com/00004707/blender-mesh-attribute-menu-extended/assets/117545764/2a67c1c9-aa94-4cad-b2cb-21d988470eb0


</p>
    <ul>
    <li>Using multiple float attributes and conversion tools</li>
    </ul>
</details>

### Example models made with help of this addon

* Sketchfab: [Holo Shapeshifter](https://sketchfab.com/3d-models/holo-shapeshifter-5d581768fbe3425c8540e3ff329707bc)
* Sketchfab: [Hyperspeed Starfield](https://sketchfab.com/3d-models/hyperspeed-starfield-6938925b3b5d40f6ba45a637e862a338)
* Sketchfab: [Disintegration effect](https://sketchfab.com/3d-models/disintegration-effect-7bcb3b17d50240c2be0f5dffffcb1308)


## Features

### Set Attribute Values For selection in Edit Mode

<p align="center">
  <img src="https://i.imgur.com/xfzUJWM.png">
</p>

* Supports any data type and all domains (vertex, edge, face, face corner)
* Allows assigning value to individual face corners based on edge selection, or "spillling" the value to near face corners from selected vertices/edges/faces

<details> <summary>Face Corner Spill</summary>
    <p align="center">
  <img width="600" src="https://i.imgur.com/YQyma0i.png">
</p>
</details>

### Conditional Selection in Edit Mode
<p align="center">
  <img src="https://i.imgur.com/h2nKael.png">
</p>

* Create a selection vertices, edges or faces based on their attribute values


### Duplicate Attribute
<p align="center">
  <img src="https://i.imgur.com/d0TS8Mi.png">
</p>

* Duplicate active attribute (that's it)


### Invert Attribute Value
<p align="center">
  <img src="https://i.imgur.com/8BNxjKi.png">
</p>

* Inverts attribute value
  * **Integer/Int8** Multiply by -1
  * **Float, Vector, Color** Subtract from 1, add to -1, multiply by -1
  * **Boolean** NOT operation
  * **String** Reverse text


### Remove all attributes

* Remove all attributes
* Exclude or include color attributes and UVMaps
* Excludes hidden attributes


### Quick copy to selected meshes

<p align="center">
  <img src="https://i.imgur.com/nZ8EWW8.png">
</p>

* Quickly copy active attribute to all selected meshes
* Extend values to meshes with more attribute value storage by duplicating or repeating 

### Create Attribute From Mesh Data

<p align="center">
  <img width="1200" src="https://i.imgur.com/zwJSbzq.png">
</p>

* Create attribute from 35+ mesh data, including: **Shape Keys, Edge Seam, Selection, Creases** and more
* Support for any source domain, eg.: Mean Bevel for Vertices and edges
* Auto convert attribute to desired domain and data type
* Batch convert all shape keys, vertex groups and other


### Convert Attribute to Mesh Data

<p align="center">
  <img src="https://i.imgur.com/69d4BuF.png">
</p>

* Convert any attribute to 19 mesh data, including: sculpt mode masks, shape keys, material index assignments and more
* Auto conversion to supported type

### Resolve Naming Collisions

<p align="center">
  <img src="https://i.imgur.com/r27JpTY.png">
</p>


* Quickly append numeric suffix to all colliding attribute names

## Notes

* blender spreadsheet does not show the string values. The addon sets the values correctly.
