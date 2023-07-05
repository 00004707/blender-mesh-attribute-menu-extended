# Mesh Attributes Menu eXtended
 Addon that extends Mesh Attributes menu in blender.



⚠️ EARLY VERSION/WORK IN PROGRESS, MANY FEATURES UNTESTED, NOT YET IMPLEMENTED 

but kinda works so feel free to test it

*Note: blender spreadsheet does not show the string values. The addon sets the values correctly.*

## Example use cases

<details> <summary>Use and create Shape Keys in Geometry Nodes</summary>
    <p align="center">
  <img width="600" src="https://i.imgur.com/tlvGPFj.gif">
</p>
    <ul><li>Create Shape Key Position Vector Attributes and use Set Position node</li>
          <li>Create Shape Key Offset Vector Attributes to use with Offset input of Set Position node</li>
</ul>
</details>

<details> <summary>Create Sculpt Mask or Face Sets in Geometry Nodes</summary>
    <p align="center">
  <img width="600" src="https://i.imgur.com/3evILQs.gif">
</p>
    <ul>
        <li>Convert float vertex attributes to sculpt mode mask</li>
        <li>Convert integer vertex attributes to face sets</li>
    </ul>
    <br>
</details>

<details> <summary>Use edge seams in Geometry Nodes</summary>
    <p align="center">
  <img width="600" src="https://i.imgur.com/acwuZ42.gif">
</p>
    <ul>
    <li>Convert edge seams to boolean edge attribute</li>
    </ul>
</details>

<details> <summary>Set color attribute to single face corner</summary>
    <p align="center">
  <img width="600" src="https://i.imgur.com/V153qx6.gif">
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
  <img width="600" src="https://i.imgur.com/BuWoZTd.gif">
</p>
    <ul>
    <li>Using multiple float attributes and conversion tools</li>
    </ul>
</details>


## Features

### Set Attribute Values For selection in Edit Mode

<p align="center">
  <img src="https://i.imgur.com/c8e9oF7.png">
</p>

* Supports any data type and all domains (vertex, edge, face, face corner)
* Allows assigning value to individual face corners based on edge selection, or "spillling" the value to near face corners from selected vertices/edges/faces

<details> <summary>Face Corner Spill</summary>
    <p align="center">
  <img width="600" src="https://i.imgur.com/YQyma0i.png">
</p>
</details>


### Duplicate Attribute

* Duplicate active attribute, (that's it)


### Invert Attribute

* Inverts attribute value
  * **Integer/Int8** multiply by -1
  * **Float, Vector, Color** Subtract from 1, add to -1, multiply by -1
  * **Boolean** NOT operation


### Remove all attributes

* Remove all attributes, with color attributes and UVMaps or not


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
  <img width="600" src="https://i.imgur.com/8beEArz.png">
</p>

* Convert any attribute to 19 mesh data, including: sculpt mode masks, shape keys, material index assignments and more
* Auto conversion to supported type
