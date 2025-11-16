[Setup]
AppName=Zapret Custom
AppVersion=0.1
AppPublisher=Savvy08
DefaultDirName={autopf}\Zapret Custom
DefaultGroupName=Zapret Custom
OutputBaseFilename=ZapretCustom_Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\ZapretCustom.exe
OutputDir=Output

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Tasks]
Name: "desktopicon"; Description: "Создать ярлык на рабочем столе"; GroupDescription: "Ярлыки:"; Flags: unchecked

[Files]
; Основная программа из папки dist\ZapretCustom
Source: "dist\ZapretCustom\ZapretCustom.exe"; DestDir: "{app}"; Flags: ignoreversion
; ВАЖНО! Папка _internal с библиотеками Python
Source: "dist\ZapretCustom\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs
; Все BAT файлы из корня
Source: "*.bat"; DestDir: "{app}"; Flags: ignoreversion
; Папка lists
Source: "lists\*"; DestDir: "{app}\lists"; Flags: ignoreversion recursesubdirs createallsubdirs
; Папка bin  
Source: "bin\*"; DestDir: "{app}\bin"; Flags: ignoreversion recursesubdirs createallsubdirs
; Иконки из корня
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.png"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Zapret Custom"; Filename: "{app}\ZapretCustom.exe"
Name: "{autodesktop}\Zapret Custom"; Filename: "{app}\ZapretCustom.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\ZapretCustom.exe"; Description: "Запустить Zapret Custom"; Flags: nowait postinstall skipifsilent