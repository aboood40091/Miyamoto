=== Reggie! Level Editor (Release Next Milestone 2 Alpha 0) ===

Advanced level editor for New Super Mario Bros. Wii, created by Treeki and
Tempus using Python, PyQt and Wii.py.

Reggie! Next created by RoadrunnerWMC, based on Reggie! release 3
This release contains many improvements, in addition to code ports from the
following Reggie! forks:
  - "ReggieMod 3.7.2" by JasonP27
  - "Reggie! Level Editor Mod (Newer Sprites) 3.8.1" by Kamek64 and MalStar1000
  - "NeweReggie! (Extention to Reggie! Level Editor)" by Treeki and angelsl

Homepage: http://rvlution.net/reggie/
Support:  http://rvlution.net/forums/

Source code package for this release can be found at:
- http://rvlution.net/forums/
Navigate to Releases -> Reggie! Next


=== Changelog: ===

Release Next (Milestone 2): (??)
- Dependencies have changed; make sure to download the new ones!

Release Next (Public Beta 1): (November 1st, 2013)
- First beta version of Reggie! Next is finally released after a full year 
  of work!
- First release, may have bugs. Report any errors at the forums (link above).
- The following sprites now render using new or updated images:
  24:  Buzzy Beetle (UPDATE)
  25:  Spiny (UPDATE)
  49:  Unused Seesaw Platform
  52:  Unused 4x Self Rotating Platforms
  55:  Unused Risihg Seesaw Platform
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
- Various bug fixes.


Release 3: (April 2nd, 2011)
- Unicode is now supported in sprite names within spritedata.xml
  (thanks to 'NSMBWHack' on rvlution.net for the bug report)
- Unicode is now supported in sprite categories.
- Sprites 274, 354 and 356 now render using images.
- Other various bug fixes.


Release 2: (April 2nd, 2010)
- Bug with Python 2.5 compatibility fixed.
- Unicode filenames and Stage folder paths should now work.
- Changed key shortcut for "Shift Objects" to fix a conflict.
- Fixed pasting so that whitespace/newlines won't mess up Reggie clips.
- Fixed a crash with the Delete Zone button in levels with no zones.
- Added an error message if an error occurs while loading a tileset.
- Fixed W9 toad houses showing up as unused in the level list.
- Removed integrated help viewer (should kill the QtWebKit dependency)
- Fixed a small error when saving levels with empty blocks
- Fixed tileset changing
- Palette is no longer unclosable
- Ctrl+0 now sets the zoom level to 100%
- Path editing support added (thanks, Angel-SL)


Release 1: (March 19th, 2010)
- Reggie! is finally released after 4 months of work and 18 test builds!
- First release, may have bugs or incomplete sprites. Report any errors to us
  at the forums (link above).


=== Requirements: ===

If you are using the source release:
- Python 3.0 (or newer) - http://www.python.org
- PyQt 5.0 (or newer) - http://www.riverbankcomputing.co.uk/software/pyqt/intro
- NSMBLib 0.5a - included with the source package (optional)

If you have a prebuilt/frozen release (for Windows or Mac OS)
you don't need to install anything - all the required libraries are included.

For more information on running Reggie from source and getting the required
libraries, check the Getting Started page inside the help file
(located at reggiedata/help/start.html within the archive)


=== Reggie! Team: ===

Developers:
- Treeki - Creator, Programmer, Data, RE
- Tempus - Programmer, Graphics, Data
- AerialX - CheerIOS, Riivolution
- megazig - Code, Optimisation, Data, RE
- Omega - int(), Python, Testing
- Pop006 - Sprite Images
- Tobias Amaranth - Sprite Info (a lot of it), Event Example Stage
- RoadrunnerWMC - Reggie! Next Developer: Programmer, UI, Sprite Images
- JasonP27 - ReggieMod Developer: Programmer, UI, Sprite Images
- Kamek64 - Reggie! Newer Sprites Developer: Programmer, Sprite Images
- ZementBlock - Sprite Data

Other Testers and Contributors:
- BulletBillTime, Dirbaio, EdgarAllen, FirePhoenix, GrandMasterJimmy,
  Mooseknuckle2000, MotherBrainsBrain, RainbowIE, Skawo, Sonicandtails,
  Tanks, Vibestar, angelsl, MalStar1000

- Tobias Amaranth and Valeth - Text Tileset Addon


=== Dependencies/Libraries/Resources: ===

Python 3 - Python Software Foundation (https://www.python.org)
Qt 5 - Nokia (http://qt.nokia.com)
PyQt 5 - Riverbank Computing (http://www.riverbankcomputing.co.uk/software/pyqt/intro)
PyQtRibbon - RoadrunnerWMC
Wii.py - megazig, Xuzz, The Lemon Man, Matt_P, SquidMan, Omega (http://github.com/icefire/Wii.py)
Interface Icons - FlatIcons (http://flaticons.net)
cx_Freeze (optional) - Anthony Tuininga (http://cx-freeze.sourceforge.net)


=== Licensing: ===

Reggie! is released under the GNU General Public License v3.
See the license file in the distribution for information.
