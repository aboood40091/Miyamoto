@ECHO OFF

echo This script is able to start Miyamoto and/or download the
echo latest spritedata and category data XMLs off of the internet.
echo(
echo Requirements:
echo - Python 3+, installed to path (make sure the py command works)
echo - PowerShell 3.0 (for the spritedata and categoryxml download), included
echo   by default on Windows 10, for other versions of Windows,
echo   you have to download the installer off of the internet.
echo(
echo Enjoy!

:choice
set /P c=Do you want to download the latest spritedata.xml [Y/N]?
if /I "%c%" EQU "Y" goto :downloadthatstuff
if /I "%c%" EQU "N" goto :nogoaway
goto :choice


:downloadthatstuff

@echo OFF
echo Downloading latest spritedata...
powershell -Command "Invoke-WebRequest https://raw.githubusercontent.com/Gota7/Miyamoto/master/miyamotodata/spritedata.xml -OutFile miyamotodata/spritedata.xml"
echo Done!

:nogoaway
set /P c=Do you want to download the latest category.xml [Y/N]?
if /I "%c%" EQU "Y" goto :downloadthatxml
if /I "%c%" EQU "N" goto :srslygoaway
goto :nogoaway

:downloadthatxml

@echo OFF
echo Downloading latest cateogry data...
powershell -Command "Invoke-WebRequest https://raw.githubusercontent.com/Gota7/Miyamoto/master/miyamotodata/spritecategories.xml -OutFile miyamotodata/spritecategories.xml"
echo Done!
echo Starting Miyamoto!
py miyamoto.py
EXIT

:srslygoaway
@echo OFF
echo Starting Miyamoto!
py miyamoto.py
