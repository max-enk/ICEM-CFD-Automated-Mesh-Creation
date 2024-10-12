# ICEM CFD Automated Mesh Creation

## Introduction

This project aims to automate the creation of various 2D and 3D meshes in ICEM CFD. Simply run the script for the desired geometry, enter geometric and meshing parameters and generate the mesh in ICEM. The meshes are intended to be used for the study of the hydrodynamics of falling film flows.

As of October 2024, this package is no longer supported by updates and is published to GitHub for public access.


## Supported Geometries

### Geometries

Currently, two different geometries are supported in 2D and 3D. 
| Geometry        | Description                                              |
|-----------------|----------------------------------------------------------|
| 2D HORIZONTAL   | Generate a 2D mesh with rectangular, horizontal* structures |
| 2D SMOOTH       | Generate a 2D mesh without structures and a smooth reactor wall |
| 3D HORIZONTAL   | Generate a 3D mesh with rectangular, horizontal* structures |
| 3D SMOOTH       | Generate a 3D mesh without structures and a smooth reactor wall |

*horizontal = structures orthogonal to main flow direction


### Supported geometric Variants

| GEOMETRY         | INLET VARIANTS                          | OUTLET VARIANTS                                    |
|-----------------|----------------------------------------|----------------------------------------------------|
| 2D HORIZONTAL   | 1: simple inlet                        | 1: simple outlet (auto select)                    |
|                 | 2: additional gas space                |                                                    |
| 2D SMOOTH       | 1: simple inlet                        | 1: simple outlet (auto select)                    |
|                 | 2: additional gas space                |                                                    |
| 3D HORIZONTAL   | 1: simple inlet                        | 1: simple outlet (auto select)                    |
|                 | 2: additional gas space                |                                                    |
| 3D SMOOTH       | 1: simple inlet                        | 1: simple outlet                                |
|                 | 2: additional gas space                | 2: recessed outlet                                |


## Contents of the Project

Included are three folders:
- __1 Documents__          - Find all of the relevant documentation here. Includes the "how-to" section below and all geometry- and meshing-related information.
- __2 Standalone Scripts__ - Scripts to be run without the need of a source file. Standalone scripts are no longer supported by updates. It is strongly recommended to use the available script bundle instead.
- __3 Script Bundle__      - Scripts that need a source file to be located in the same folder. Does continue to recieve updates and functional extensions.


## How to use the scripts

### Install and configure Python

To run the scripts, make sure to have a suitable Python environment installed on your machine. The latest version of Python can be downloaded [here](https://www.python.org/downloads/) or via the Microsoft Store. To ensure maximum compatibility, installing Python version 3.11 from the sources is recommended. Using Python 3.12 may cause errors as some of the string formatting works differently.

Additionally, install all the required packages via the windows command line, if not installed already.

```
python -m pip install package
```

Replace "package" with the desired package to be installed.
Required packages:
- os
- re
- numpy
- colorama (tested for Windows 11, Visual Studio Code CLI)

In case you are using a version of Python different to the one provided in the Microsoft Store, replace the command line executable "python" with the path to your python.exe, usually in the form of C:/Users/(username)/AppData/Local/Programs/Python/PythonXXX/python.exe when installing from the sources.

### Execute the scripts

For clarification of the geometric and meshing parameters, please refer to the provided documents outlining variable names and meshing zones.

1. __Execute the .py file__ (ensure, that a suitable python environment is installed)
2. __Define inlet and outlet variants__
   - Inlet:
      1. Simple inlet
      2. Inlet with additional gas space
   - Outlet:
      1.	Simple outlet
      2.	Recessed outlet (3D smooth only)
   - (optional) inlet 1 + outlet 1: prepare geometry for periodic boundary conditions (must be separately defined in ICEM/Fluent)
3. __Define project name__
   - The project name will be the name of all output files and the output folder, in which the output files are saved to.
4. (optional) __Load an existing ".conf" file for reference__
   - The script will look for the specified file in its root folder.
   - Configuration files created by a different script can be used as well, but may require additional user inputs.
   - Enables reference only options.
5. __Define geometric parameters__ – options:
   - (reference only) Copy geometric parameters from reference file.
   - Manually define geometric parameters.
6. __Define meshing parameters__ – options:
   - (reference only) Reference Meshing – use mesh parameters as defined in the reference file.
      - A refinement factor can be defined, which will coarsen/refine the mesh. Its default value is 1.0, resulting in a mesh topology identical to the one defined in the reference file.
      - Values > 1.0 lead to coarsening, values < 1.0 lead to refining.
      - The factor will be applied to all absolute cell dimensions defined in the reference file.
   - Default Meshing – Will mesh geometry automatically with default settings. The default cell sizes can be adjusted at the top of the scripts.
   - Custom Meshing – Define meshing rule and cell size(s) for every section individually.
7. __Output:__
   - A folder with the specified project name containing:
      - .conf: configuration file containing geometric and meshing parameters.
      - .rpl: replay file to be loaded into ICEM.
8. __Load the .rpl file into ICEM.__
   1. Load the .rpl file (File > Replay Scripts > Load script file).
   2. Execute all commands (do all).
9. __Check mesh configuration and export:__
   - Always check your geometry and mesh if all parameters have been applied as specified.
   - Consider running a mesh check before exporting to Fluent/CFX…
   - When exporting a mesh to Fluent/CFX, select the correct type of geometry (2D/3D).

