# Reggie! Level Editor Next
(Milestone 2 Alpha 2)

----------------------------------------------------------------

Homepage:  http://rvlution.net/reggie/  
Support:   http://rvlution.net/forums/  
On GitHub: https://github.com/RoadrunnerWMC/Reggie-Next

----------------------------------------------------------------

**NOTE: THIS IS A VERY UNSTABLE PRERELEASE VERSION! EXPECT CRASHES AND UNFINISHED THINGS!**

Advanced level editor for New Super Mario Bros. Wii, created by Treeki, Tempus and RoadrunnerWMC using Python, PyQt and Wii.py .

"Next" version created by RoadrunnerWMC, based on official release 3.

This release contains many improvements, in addition to code imports from the following Reggie! forks:
 * "ReggieMod 3.7.2" by JasonP27
 * "Reggie! Level Editor Mod (Newer Sprites) 3.8.1" by Kamek64 and MalStar1000
 * "NeweReggie! (Extension to Reggie! Level Editor)" by Treeki and angelsl

Source code repository for Reggie! Next can be found at:  
https://github.com/RoadrunnerWMC/Reggie-Next 

----------------------------------------------------------------

### Getting Started

If you're on Windows and don't care about having the bleeding-edge latest features, you can use the official installer. This is by far the easiest setup method. The installer will take care of everything for you.

If you are not on Windows or you want the very latest features, you'll need to run Reggie! from source.


### How to Run Reggie! from Source

Download and install the following:
 * Python 3.4 (or newer) - http://www.python.org
 * PyQt 5.3 (or newer) - http://www.riverbankcomputing.co.uk/software/pyqt/intro
 * cx_Freeze 4.3 (or newer) (optional) - http://cx-freeze.sourceforge.net
 * PyQtRibbon (latest version) - https://github.com/RoadrunnerWMC/PyQtRibbon
 * NSMBLib 0.5a (or newer) (optional) - included with the source release

Run the following in a command prompt:  
`python3 reggie.py`  
You can replace `python3` with the path to python.exe (including "python.exe" at the end) and `reggie.py` with the path to reggie.py (including "reggie.py" at the end)


### Reggie! Team

Developers:
 * Treeki - Creator, Programmer, Data, RE
 * Tempus - Programmer, Graphics, Data
 * AerialX - CheerIOS, Riivolution
 * megazig - Code, Optimisation, Data, RE
 * Omega - int(), Python, Testing
 * Pop006 - Sprite Images
 * Tobias Amaranth - Sprite Info (a lot of it), Event Example Stage
 * RoadrunnerWMC - Reggie! Next Developer: Programmer, UI, Sprite Images
 * JasonP27 - ReggieMod Developer: Programmer, UI, Sprite Images
 * Kamek64 - Reggie! Newer Sprites Developer: Programmer, Sprite Images
 * ZementBlock - Sprite Data
 * MalStar1000 - Sprite Images, Other
 * Grop - Sprite Data
 * joietyfull64 - Sprite Data
 * MidiGuyDP - NewerSMBW Background Images & Names

Translators: (in alphabetical order, by language)
 * Translation Leader: Wolfy76700
 * Dutch: Grop
 * French: Wolfy76700
 * German: Atomic Python (mralpha)
 * Spanish: MalStar1000
 * Turkish: nlgzrgn

Other Testers and Contributors:
 * BulletBillTime, Dirbaio, EdgarAllen, FirePhoenix, GrandMasterJimmy, Mooseknuckle2000, MotherBrainsBrain, RainbowIE, Skawo, Sonicandtails, Tanks, Vibestar, angelsl
 * Tobias Amaranth and Valeth - Text Tileset Addon
 * LifeMushroom (Mario64) - run-python34.bat


### Dependencies/Libraries/Resources

Python 3 - Python Software Foundation (https://www.python.org)  
Qt 5 - Nokia (http://qt.nokia.com)  
PyQt5 - Riverbank Computing (http://www.riverbankcomputing.co.uk/software/pyqt/intro)  
PyQtRibbon - RoadrunnerWMC (https://github.com/RoadrunnerWMC/PyQtRibbon)  
Wii.py - megazig, Xuzz, The Lemon Man, Matt_P, SquidMan, Omega (https://github.com/grp/Wii.py) (included)  
Interface Icons - FlatIcons (http://flaticons.net)  
cx_Freeze - Anthony Tuininga (http://cx-freeze.sourceforge.net)


### License

Reggie! is released under the GNU General Public License v3.
See the license file in the distribution for information.

----------------------------------------------------------------

## Changelog

Release Next (Milestone 2 Alpha 2): (July 31, 2014)
 * Fixed a bug that prevented the Zones dialog from working properly
 * Added some debug code to help track an elusive bug

Release Next (Milestone 2 Alpha 1): (July 30, 2014)
 * Prerequisites have changed; make sure to download the new ones!
 * New Sprite Image API fully implemented
 * Several new sprite images, and more that have been improved
 * New Bitfield editor for Rotating Bullet Bill Launcher
 * Many other new features
 * New icon set from flaticons.net

Release Next (Public Beta 1): (November 1st, 2013)
 * First beta version of Reggie! Next is finally released after a full year of work!
 * First release, may have bugs. Report any errors at the forums (link above).
 * The following sprites now render using new or updated images:  
   24:  Buzzy Beetle (UPDATE)  
   25:  Spiny (UPDATE)  
   49:  Unused Seesaw Platform  
   52:  Unused 4x Self Rotating Platforms  
   55:  Unused Rising Seesaw Platform  
   87:  Unused Trampoline Wall  
   123: Unused Swinging Castle Platform  
   125: Chain-link Koopa Horizontal (UPDATE)  
   126: Chain-link Koopa Vertical (UPDATE)  
   132: Beta Path-controlled Platform  
   137: 3D Spiked Stake Down  
   138: Water (Non-location-based only)  
   139: Lava (Non-location-based only)  
   140: 3D Spiked Stake Up  
   141: 3D Spiked Stake Right  
   142: 3D Spiked Stake Left  
   145: Floating Barrel  
   147: Coin (UPDATE)  
   156: Red Coin Ring (UPDATE)  
   157: Unused Big Breakable Brick Block  
   160: Beta Path-controlled Platform  
   170: Powerup in a Bubble  
   174: DS One-way Gates  
   175: Flying Question Block (UPDATE)  
   179: Special Exit Controller  
   190: Unused Tilt-controlled Girder  
   191: Tile Event  
   195: Huckit Crab (UPDATE)  
   196: Fishbones (UPDATE)  
   197: Clam (UPDATE)  
   205: Giant Bubbles (UPDATE)  
   206: Zoom Controller  
   212: Rolling Hill (UPDATE)  
   216: Poison Water (Non-location-based only)  
   219: Line Block  
   222: Conveyor-belt Spike  
   233: Bulber (UPDATE)  
   262: Poltergeist Items (UPDATE)  
   268: Lava Geyser (UPDATE)  
   271: Little Mouser (UPDATE)  
   287: Beta Path-controlled Ice Block  
   305: Lighting - Circle  
   323: Boo Circle  
   326: King Bill (UPDATE)  
   359: Lamp (UPDATE)  
   368: Path-controlled Flashlight Raft  
   376: Moving Chain-link Fence (UPDATE)  
   416: Invisible Mini-Mario 1-UP (UPDATE)  
   417: Invisible Spin-jump coin (UPDATE)  
   420: Giant Glow Block (UPDATE)  
   433: Floating Question Block (UPDATE)  
   447: Underwater Lamp (UPDATE)  
   451: Little Mouser Despawner
 * Various bug fixes.


Release 3: (April 2nd, 2011)
 * Unicode is now supported in sprite names within spritedata.xml (thanks to 'NSMBWHack' on rvlution.net for the bug report)
 * Unicode is now supported in sprite categories.
 * Sprites 274, 354 and 356 now render using images.
 * Other various bug fixes.


Release 2: (April 2nd, 2010)
 * Bug with Python 2.5 compatibility fixed.
 * Unicode filenames and Stage folder paths should now work.
 * Changed key shortcut for "Shift Objects" to fix a conflict.
 * Fixed pasting so that whitespace/newlines won't mess up Reggie clips.
 * Fixed a crash with the Delete Zone button in levels with no zones.
 * Added an error message if an error occurs while loading a tileset.
 * Fixed W9 toad houses showing up as unused in the level list.
 * Removed integrated help viewer (should kill the QtWebKit dependency)
 * Fixed a small error when saving levels with empty blocks
 * Fixed tileset changing
 * Palette is no longer unclosable
 * Ctrl+0 now sets the zoom level to 100%
 * Path editing support added (thanks, Angel-SL)


Release 1: (March 19th, 2010)
 * Reggie! is finally released after 4 months of work and 18 test builds!
 * First release, may have bugs or incomplete sprites. Report any errors to us at the forums (link above).

