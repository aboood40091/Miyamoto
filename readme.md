# Miyamoto! DX
## The New Super Mario Bros. U Deluxe Editor
A level editor for NSMBUDX by AboodXD and Gota7, based on Reggie! Next by RoadrunnerWMC, which is based on Reggie by Treeki, Tempus et al. Uses Python 3, PyQt5, SarcLib and libyaz0.

----------------------------------------------------------------

Discord: https://discord.gg/AvFEHpp  
GitHub: https://github.com/aboood40091/Miyamoto/tree/deluxe  

----------------------------------------------------------------

### Credits
#### Reggie! & Reggie! Next
* Treeki -- Creator of Reggie!
* RoadrunnerWMC -- Creator of Reggie! Next
  
#### Miyamoto
* AboodXD -- Lead Coder, Spritedata, Graphics
* Gota7 -- Coding, Spritedata, Graphics
* Grop -- Coding, Spritedata
* John10v10 -- Quick Paint Tool
* Luzifer -- Graphics
* Mayro -- Graphics
* mrbengtsson -- Graphics
* Meorge -- Testing on macOS
* RicBent -- Graphics
* reece stone -- Spritedata, Graphics
* Shawn Shea -- Graphics
* Toms -- Spritedata, Graphics
* Wiimm -- WSZST
  
#### Reggie NSMBU
* Grop -- Coding, Spritedata, Graphics
* Hiccup -- Spritedata
* Kinnay -- Spritedata
* MrRean -- Coding, Spritedata, Categories, Graphics
* RoadrunnerWMC -- Coding, Spritedata, Graphics

----------------------------------------------------------------

### TODO
- Get unknown area fields figured out
- Sprite images / HD screenshots (a lot of them)
- Improve Zones and Objects resizing

----------------------------------------------------------------

### Building
Please note that when building Miyamoto, you have to remove any instances of Cython usage in both Miyamoto and libyaz0. (pyximport)  
Alternatively, you can build the .pyx files and then remove any instances of pyximport in the code.

----------------------------------------------------------------

### How To Use
#### STEP 1:
Download the source code from here:  
https://github.com/aboood40091/Miyamoto/tree/deluxe  

Or using `git` with the following command:  
`git clone -b deluxe --single-branch https://github.com/aboood40091/Miyamoto.git`  

#### STEP 2:
Install the latest version of Python 3 (make sure you install pip and add it to PATH):  
https://www.python.org/downloads/

#### STEP 3:
Open Command Prompt (or PowerShell) and type the following:  
`py -3 -m pip install PyQt5`  
`py -3 -m pip install Cython`  
`py -3 -m pip install libyaz0`  
`py -3 -m pip install SarcLib`  

#### STEP 4:
Make sure you have a compatible C compiler with Cython. For Linux and Mac OSX, you want "gcc". (which is usually preinstalled)  

##### STEP 4.5 (C compiler for Windows):
Download the Microsoft Build Tools 2015 installer:  
http://download.microsoft.com/download/5/F/7/5F7ACAEB-8363-451F-9425-68A90F98B238/visualcppbuildtools_full.exe  


Run the following in a command prompt:  
`python3 miyamoto.py`  
You can replace `python3` with the path to python.exe (including "python.exe" at the end) and `miyamoto.py` with the path to miyamoto.py (including "miyamoto.py" at the end)  
  
It should ask you to choose a folder. Choose the `Course` folder, or where you've stored the levels (1-1.sarc, at least). (The `Unit` folder is also required and must be placed next to the `Course` folder)

Enjoy.
