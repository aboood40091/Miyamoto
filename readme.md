# Miyamoto!
## The New Super Mario Bros. U / New Super Luigi U Editor
A level editor for NSMBU and NSLU by AboodXD and Gota7, based on Reggie! Next by RoadrunnerWMC, which is based on Reggie by Treeki, Tempus et al. Uses Python 3, PyQt5, SarcLib and libyaz0.

----------------------------------------------------------------

Discord: https://discord.gg/AvFEHpp  
GitHub: https://github.com/aboood40091/Miyamoto  

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
* libtxc_dxtn -- Original DXT5 (De)compressor in C
* Luzifer -- Graphics
* Mayro -- Graphics
* mrbengtsson -- Graphics
* Meorge -- Testing on macOS
* NVIDIA -- NVCOMPRESS
* RicBent -- Graphics
* reece stone -- Spritedata, Graphics
* Shawn Shea -- Graphics
* Toms -- Spritedata, Graphics
* Wexos -- Original BC3 Compressor in C#
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
First, download this repo (either by using ```git clone``` or ```git pull``` if you've already cloned it), or by downloading a release, or by just downloading this repo as a whole.

Second, you need the filesystem for New Super Mario Bros. U. You can get it by dumping the game using ddd: https://gbatemp.net/threads/ddd-wiiu-title-dumper.418492/

Thirdly, Download and install the following:
 * Python 3.4 (or newer) - http://www.python.org
 * PyQt 5.3 (or newer) - http://www.riverbankcomputing.co.uk/software/pyqt/intro
 * SarcLib (pip3 install SarcLib)
 * libyaz0 (pip3 install libyaz0)
 * cx_Freeze 4.3 (or newer) (optional) - http://cx-freeze.sourceforge.net  

Run the following in a command prompt:  
`python3 miyamoto.py`  
You can replace `python3` with the path to python.exe (including "python.exe" at the end) and `miyamoto.py` with the path to miyamoto.py (including "miyamoto.py" at the end)  
  
It should ask you to choose a folder. Choose the course_res_pack folder, or where you've stored the levels (1-1.szs, at least).

Enjoy.
