@ECHO OFF

echo This script is able to start Reggie and/or download the
echo latest spritedata and category data XMLs off of the internet.
echo(
echo Requirements:
echo - Python 3.4, installed to the default location
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
powershell -Command "Invoke-WebRequest http://rhcafe.us.to/spritexml.php -OutFile reggiedata/spritedata.xml"
echo Done!

:nogoaway
set /P c=Do you want to download the latest category.xml [Y/N]?
if /I "%c%" EQU "Y" goto :downloadthatxml
if /I "%c%" EQU "N" goto :srslygoaway
goto :nogoaway

:downloadthatxml

@echo OFF
echo Downloading latest cateogry data...
powershell -Command "Invoke-WebRequest http://rhcafe.us.to/categoryxml.php -OutFile reggiedata/spritecategories.xml"
echo Done!
echo Starting Reggie!
cmd /k C:/Python34/python.exe reggie.py

:srslygoaway
@echo OFF
echo Starting Reggie!
cmd /k C:/Python34/python.exe reggie.py