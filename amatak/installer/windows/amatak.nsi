; NSIS Script for Amatak Windows Installer
Unicode true
Name "Amatak Language"
OutFile "Amatak-Installer.exe"
InstallDir "$PROGRAMFILES64\Amatak"
RequestExecutionLevel admin ; Requires admin for program files install

!include "MUI2.nsh"

; UI Configuration
!define MUI_ICON "assets\amatak.ico"
!define MUI_UNICON "assets\amatak-uninstall.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "assets\installer-sidebar.bmp"

; Installer Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Uninstaller Pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Languages
!insertmacro MUI_LANGUAGE "English"

Section "Main Application"
  SetOutPath "$INSTDIR"
  
  ; Main application files
  File /r "dist\windows\*.*"
  
  ; Add to PATH
  EnVar::SetHKCU
  EnVar::AddValue "PATH" "$INSTDIR\bin"
  
  ; Create shortcuts
  CreateDirectory "$SMPROGRAMS\Amatak"
  CreateShortcut "$SMPROGRAMS\Amatak\Amatak.lnk" "$INSTDIR\bin\amatak.exe"
  CreateShortcut "$SMPROGRAMS\Amatak\Uninstall.lnk" "$INSTDIR\uninstall.exe"
  CreateShortcut "$DESKTOP\Amatak.lnk" "$INSTDIR\bin\amatak.exe"
  
  ; Register uninstaller
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Amatak" \
                   "DisplayName" "Amatak Language"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Amatak" \
                   "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Amatak" \
                   "Publisher" "Amatak Team"
  WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

Section "Uninstall"
  ; Remove files
  RMDir /r "$INSTDIR"
  
  ; Remove shortcuts
  Delete "$SMPROGRAMS\Amatak\*.*"
  RMDir "$SMPROGRAMS\Amatak"
  Delete "$DESKTOP\Amatak.lnk"
  
  ; Remove PATH entry
  EnVar::SetHKCU
  EnVar::DeleteValue "PATH" "$INSTDIR\bin"
  
  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Amatak"
SectionEnd