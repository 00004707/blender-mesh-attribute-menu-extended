# Mesh Attributes Menu eXtended
![Static Badge](https://img.shields.io/badge/blender-3.1.0%2B-orange)

 Addon that extends Mesh Attributes menu in blender (and more!).

[Take me to the downloads](https://github.com/00004707/blender-mesh-attribute-menu-extended/releases/)

[How to install and how to use it?](https://github.com/00004707/blender-mesh-attribute-menu-extended/wiki)

_Note: You can press the "Code" button to download the latest unstable version. It might have new features or not work at all._


## Features

### Set Attribute Values For selection in Edit Mode

<p align="center">
  <img src="https://github.com/00004707/blender-mesh-attribute-menu-extended/assets/117545764/bc05b27a-b41e-4ef0-9d59-cc1140917c05">
</p>

<ul>
<li><details><summary>Vertex paint meshes with more precision and visualize mesh loops</summary>

https://github.com/00004707/blender-mesh-attribute-menu-extended/assets/117545764/4cee8eb2-d37b-48a2-9ce8-71ffb56b6232

<a href="https://skfb.ly/6TpDn"> "Hand Topology Study"</a> by Johnson Martin is licensed under <a href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution. </a>

</details></li>

<li><details><summary> Use attributes as an alternative to vertex groups and face maps, in a conveniently placed menu</summary>

https://github.com/00004707/blender-mesh-attribute-menu-extended/assets/117545764/d135de45-315d-4ffe-8740-d9ed07646d4b

<a href="https://skfb.ly/6TpDn"> "Hand Topology Study"</a> by Johnson Martin is licensed under <a href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution. </a>
</details></li>


<li><details><summary> Assign values to individual face corners (with edge selection and face corner spill feature off)</summary>

https://github.com/00004707/blender-mesh-attribute-menu-extended/assets/117545764/90fc519a-4543-4df4-b38d-6f6168abbfd2

<a href="https://skfb.ly/6TpDn"> "Hand Topology Study"</a> by Johnson Martin is licensed under <a href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution. </a>
</details></li>
</ul>

### Conditional Selection in Edit Mode
<p align="center">
  <img src="https://i.imgur.com/h2nKael.png">
</p>

* Select in edit mode by attribute value - equal, higher, lower and more
* Mark different part of meshes in geometry nodes to then select it in edit mode
* Select domains with non-zero/non-black/non-false value quickly
* Select domains with specified value quickly

### Duplicate Attribute
<p align="center">
  <img src="https://i.imgur.com/d0TS8Mi.png">
</p>

* Duplicate active attribute with one click


### Invert Attribute Value
<p align="center">
  <img src="https://i.imgur.com/8BNxjKi.png">
</p>

* Perform an invert operation on attribute values, quickly!
  * **Integer/Int8** Multiply by -1
  * **Float, Vector, Color** Subtract from 1, add to -1, multiply by -1
  * **Boolean** NOT operation
  * **String** Reverse text


### Remove all attributes

* Remove all attributes FAST
* Filter by type (hidden, built-in, ...), domain, data type


### Quick copy to selected meshes

<p align="center">
  <img src="https://i.imgur.com/nZ8EWW8.png">
</p>

* Copy attributes to other meshes FAST without data transfer modifier
* Active, multiple, all - with a filtered list 
* Extend the values on larger meshes by repeating on duplicating values on domains

### Create Attribute From Mesh Data

<p align="center">
  <img width="1200" src="https://i.imgur.com/zwJSbzq.png">
</p>

* Create attribute from data in blender not yet accesible via dedicated geometry nodes node
* Use Shape Keys, Edge seams, freestyle marks, in geometry nodes
* Store multiple sculping masks, face sets, seams as attributes
* Automatically convert to desired domain and data type after creation
* Convert multiple and all at once

### Convert Attribute to Mesh Data

<p align="center">
  <img src="https://i.imgur.com/69d4BuF.png">
</p>

* Convert created attributes in geometry ndoes to sculpt mode masks, shape keys, material index assignments and more
* Auto convert to right domain and data type
* Convert multiple attributes to selected mesh data (like shape keys)
* Set multiple vertex group weight values by using To Vertex Group index feature

### Resolve Naming Collisions

<p align="center">
  <img src="https://i.imgur.com/r27JpTY.png">
</p>


* Quickly append numeric suffix to all colliding attribute names

### Bake attributes to data textures

* Convert attributes to data textures to use in game engines eg. create vertex animation textures
* Bake vertex color to texture FAST
* Pack textures with a plane mesh 

### Create named attribute node quickly

<p align="center">
  <img src="https://github.com/00004707/blender-mesh-attribute-menu-extended/assets/117545764/3e30a1f8-ac5e-4316-b86e-6ce12b2f5c3d">
</p>


<ul>
<li><details><summary>Get your attributes to work in Geometry Nodes and Shaders FAST</summary>

https://github.com/00004707/blender-mesh-attribute-menu-extended/assets/117545764/955bab4c-6f58-4f81-8746-b58e40900f85

</li>
</ul>


### Export attributes to CSV (+ import)

* Simple export of active, all or seleted attributes to CSV file
* Import attributes from CSV file (headers must contain domain and data type in round brackets)

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




## Limitations and notes

* In Blender 3.5 "Set Mesh Attribute" operator was implemented, which greatly improves the performance of the addon.
* The addon can freeze blender if the mesh has more than 500k vertices (varies by system). Use with caution
* Precise selection by condition for face corners is very slow. By default it is using the fast method. If you want to precisely select face corners, enable it in addon preferences and make sure the mesh should not exceed 50k vertices to not freeze blender
* Name collisions can produce unexpected results and even crashes. Use resolve naming collisions or avoid naming the attributes with same name. Mind that some of the built-in blender operators can also produce unexpeced results with naming collisions (TL:DR avoid naming collisons!)
* blender spreadsheet does not show the string values. The addon sets the values correctly.
