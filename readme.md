# Miyamoto!
## The New Super Mario Bros. U / New Super Luigi U Editor
A level editor for NSMBU and NSLU by AboodXD and Gota7, based on Reggie! Next by RoadrunnerWMC, which is based on Reggie by Treeki, Tempus et al. Uses Python 3, PyQt5, SarcLib and libyaz0.

----------------------------------------------------------------

Discord: https://discord.gg/AvFEHpp  
GitHub: https://github.com/aboood40091/Miyamoto  

----------------------------------------------------------------

### Credits
#### Reggie! & Reggie! Next
* Treeki & Tempus -- Creators of Reggie!
* RoadrunnerWMC -- Creator of Reggie! Next
* Grop, Hiccup, Kinnay, MrRean and RoadrunnerWMC -- Reggie! Next NSMBU
  
#### Miyamoto
* AboodXD -- Lead Coder, Icons & Graphics, Sprite Images & Coding
* Gota7 -- Founder, Icons
* John10v10 -- Quick Paint Tool
* mrbengtsson -- Sprite Images & Coding
  
#### Level and Tileset Data Reverse-engineering
* AboodXD
* Kinnay
  
#### Spritedata Reverse-engineering
* AboodXD
* mrbengtsson
* Kinnay
* Grop
  
#### Others
* Gota7 -- Spritedata, Testing on Linux
* Gregory Haskins -- Gibberish
* Hiccup -- Spritedata, Sprite Categories
* libtxc_dxtn -- Original DXT5 (De)compressor in C
* Meorge -- Testing on macOS
* NVIDIA -- NVCOMPRESS
* reece stone -- Spritedata
* RoadrunnerWMC -- Stamps offset fixes
* Toms -- Spritedata, Testing on macOS
* Wexos -- Original BC3 Compressor in C#
* Wiimm -- WSZST

----------------------------------------------------------------

### Building
Please note that when building Miyamoto, you have to remove any instances of Cython usage in both Miyamoto and libyaz0. (pyximport)  
Alternatively, you can build the .pyx files and then remove any instances of pyximport in the code.

----------------------------------------------------------------

### How To Use
#### STEP 1:
Download the source code from here:  
https://github.com/aboood40091/Miyamoto  

Or using `git` with the following command:  
`git clone --single-branch https://github.com/aboood40091/Miyamoto.git`  

#### STEP 2:
Install the latest version of Python 3 (make sure you install pip and, on Windows, select the option to add Python to PATH):  
https://www.python.org/downloads/

#### STEP 3:
Open Command Prompt or PowerShell (Windows) or Terminal (Linux or Mac OSX) and type the following: (If you are on Linux or Mac OSX, replace `py -3` with `python3`)  
`py -3 -m pip install PyQt5`  
`py -3 -m pip install Cython`  
`py -3 -m pip install libyaz0`  
`py -3 -m pip install SarcLib`  

#### STEP 4: (Skip to 4.5 for Windows)
Make sure you have a compatible C compiler with Cython. For Linux and Mac OSX, you want "GCC".  
GCC is usually preinstalled on Linux, but if you don't have it, the command `sudo apt-get install build-essential` will fetch everything you need.  
On Mac OSX, you can retrieve gcc by installing Apple’s XCode through running the command `xcode-select --install`.  

##### STEP 4.5 (C compiler for Windows):
Download the Microsoft Build Tools 2015 installer:  
http://download.microsoft.com/download/5/F/7/5F7ACAEB-8363-451F-9425-68A90F98B238/visualcppbuildtools_full.exe  

#### STEP 5:
You need the filesystem for New Super Mario Bros. U. You can get it by dumping the game using ddd: https://gbatemp.net/threads/ddd-wiiu-title-dumper.418492/  


Finally, open Command Prompt or PowerShell (Windows) or Terminal (Linux or Mac OSX) and type the following: (If you are on Linux or Mac OSX, replace `py -3` with `python3`)  
`py -3 miyamoto.py`  
You can replace `miyamoto.py` with the path to miyamoto.py (including "miyamoto.py" at the end)  
  
It should ask you to choose a folder. Choose the course_res_pack folder, or where you've stored the levels (1-1.szs, at least).

Enjoy.
