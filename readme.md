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
* Gregory Haskins -- Gibberish
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
- Get unknown entrance fields figured out
- Get unknown area fields figured out
- Sprite images / HD screenshots (a lot of them)
- Improve Zones and Objects resizing

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
Download the Build Tools for Visual Studio 2017 installer:  
https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2017  
After you get the installer running, go to the `Workloads` tab and check `Visual C++ Build Tools` and then proceed with the installation process.   

Run the following in a command prompt:  
`python3 miyamoto.py`  
You can replace `python3` with the path to python.exe (including "python.exe" at the end) and `miyamoto.py` with the path to miyamoto.py (including "miyamoto.py" at the end)  
  
It should ask you to choose a folder. Choose the `Course` folder, or where you've stored the levels (1-1.sarc, at least). (The `Unit` folder is also required and must be placed next to the `Course` folder)

Enjoy.
