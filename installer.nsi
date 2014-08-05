# NSIS Installer Script for Reggie!
# 
# Change the values below to change basic settings:
!define Name "Reggie! Level Editor Next"
!define InputDir "distrib\reggie_next_m2a4_win32"
!define OutputName "reggie-next-0.14-win32.exe"
!define Publisher "RVLution"
!define IconPath "reggiedata\win_icon.ico"
!define VersionStr "Milestone 2 Alpha 4"

###############################################################
###############################################################
###############################################################
###############################################################
# General
Name "${Name}"

OutFile "${OutputName}"
 
RequestExecutionLevel admin
InstallDir "$PROGRAMFILES\${Name}"

!include LogicLib.nsh
!include MUI2.nsh
!include "FileFunc.nsh"
!insertmacro GetTime

!define MUI_ICON "${IconPath}"

###############################################################
# Ask for admin privileges

Function .onInit
SetShellVarContext all
UserInfo::GetAccountType
pop $0
${If} $0 != "admin"
    MessageBox mb_iconstop "Administrator rights required!"
    SetErrorLevel 740 # ERROR_ELEVATION_REQUIRED
    Quit
${EndIf}
FunctionEnd

###############################################################
# Pages

!define MUI_FINISHPAGE_RUN
!define MUI_FINISHPAGE_RUN_TEXT "Create desktop shortcut"
!define MUI_FINISHPAGE_RUN_FUNCTION CreateDesktopShortcut

!define MUI_FINISHPAGE_SHOWREADME
!define MUI_FINISHPAGE_SHOWREADME_TEXT "Create Start Menu shortcut"
!define MUI_FINISHPAGE_SHOWREADME_FUNCTION CreateStartMenuShortcut

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE license.txt
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

###############################################################
# Functions

Function CreateDesktopShortcut
	CreateShortCut "$DESKTOP\${Name}.lnk" "$INSTDIR\reggie.exe"
FunctionEnd

Function CreateStartMenuShortcut
	CreateShortCut "$SMPROGRAMS\${Name}.lnk" "$INSTDIR\reggie.exe"
FunctionEnd

###############################################################
# Sections
Section

	# This fixes a bug, maybe
	SetShellVarContext all
 
	# Define output path
	SetOutPath $INSTDIR
	 
	# Copy all files, recursively
	File /r "${InputDir}\*.*"
	 
	# Create uninstaller
	WriteUninstaller $INSTDIR\uninstall.exe
	
	# Write registry keys so the uninstaller will
	# show up in Control Panel
	${GetTime} "" "L" $0 $1 $2 $3 $4 $5 $6
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${Name}" \
				"DisplayIcon"     "$INSTDIR\${IconPath}"
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${Name}" \
				"DisplayName"     "${Name}"
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${Name}" \
				"DisplayVersion"  "${VersionStr}"
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${Name}" \
				"InstallDate"     "$2$1$0"
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${Name}" \
				"InstallLocation" "$INSTDIR\"
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${Name}" \
				"Publisher"       "${Publisher}"
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${Name}" \
				"UninstallString" "$INSTDIR\uninstall.exe"
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${Name}" \
				"URLInfoAbout"    "http://rvlution.net"
				
	${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
	IntFmt $0 "0x%08X" $0
	WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${Name}" \
				"EstimatedSize" "$0"
	

SectionEnd

Section "Uninstall"

	# This fixes a bug, maybe
	SetShellVarContext all
 
	# Delete uninstaller first
	Delete $INSTDIR\uninstall.exe
	
	# Delete the registry key folder, thereby deleting
	# all the values contained within
	DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${Name}"
	
	# Delete shortcuts, if possible
	Delete "$DESKTOP\${Name}.lnk"
	Delete "$SMPROGRAMS\${Name}.lnk"
	
	# Delete the entire folder recursively
	RMDir /r $INSTDIR
 
SectionEnd