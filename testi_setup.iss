; Инсталлятор для Zapret Custom 0.2
; Автор: Savvy08

[Setup]
; Основная информация о приложении
AppName=Zapret Custom
AppVersion=0.2
AppPublisher=Savvy08
AppPublisherURL=https://github.com/savvy08
AppSupportURL=https://github.com/savvy08
AppUpdatesURL=https://github.com/savvy08

; Директории установки
DefaultDirName={autopf}\Zapret Custom
DefaultGroupName=Zapret Custom
DisableProgramGroupPage=yes

; Выходные файлы
OutputDir=D:\Desktop My\Coding\ZapretGUI\Zapret 0.2\Output
OutputBaseFilename=ZapretCustom_0.2_Setup
SetupIconFile=D:\Desktop My\Coding\ZapretGUI\Zapret 0.2\zapret-discord-youtube\icon.ico
UninstallDisplayIcon={app}\ZapretCustom.exe

; Сжатие
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes
LZMANumBlockThreads=2

; Стиль и внешний вид
WizardStyle=modern
; Используем стандартные изображения Inno Setup
; Если хотите свои - создайте WizModernImage.bmp (164x314) и WizModernSmallImage.bmp (55x55)

; Требования к системе
MinVersion=10.0
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; Права доступа
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Основной исполняемый файл
Source: "D:\Desktop My\Coding\ZapretGUI\Zapret 0.2\zapret-discord-youtube\dist\ZapretCustom\ZapretCustom.exe"; DestDir: "{app}"; Flags: ignoreversion

; Папка _internal с библиотеками Python (КРИТИЧЕСКИ ВАЖНО!)
Source: "D:\Desktop My\Coding\ZapretGUI\Zapret 0.2\zapret-discord-youtube\dist\ZapretCustom\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

; BAT файлы конфигураций из корня
Source: "D:\Desktop My\Coding\ZapretGUI\Zapret 0.2\zapret-discord-youtube\*.bat"; DestDir: "{app}"; Flags: ignoreversion

; Папка lists со списками
Source: "D:\Desktop My\Coding\ZapretGUI\Zapret 0.2\zapret-discord-youtube\lists\*"; DestDir: "{app}\lists"; Flags: ignoreversion recursesubdirs createallsubdirs

; Папка bin с исполняемыми файлами zapret
Source: "D:\Desktop My\Coding\ZapretGUI\Zapret 0.2\zapret-discord-youtube\bin\*"; DestDir: "{app}\bin"; Flags: ignoreversion recursesubdirs createallsubdirs

; Иконки
Source: "D:\Desktop My\Coding\ZapretGUI\Zapret 0.2\zapret-discord-youtube\icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\Desktop My\Coding\ZapretGUI\Zapret 0.2\zapret-discord-youtube\icon.png"; DestDir: "{app}"; Flags: ignoreversion; DestName: "icon.png"

; Файл настроек (если существует) - НЕ перезаписывать при обновлении!
Source: "D:\Desktop My\Coding\ZapretGUI\Zapret 0.2\zapret-discord-youtube\settings.json"; DestDir: "{app}"; Flags: onlyifdoesntexist skipifsourcedoesntexist uninsneveruninstall

; README или документация (если есть)
Source: "D:\Desktop My\Coding\ZapretGUI\Zapret 0.2\zapret-discord-youtube\README.md"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist isreadme

[Icons]
; Ярлык в меню Пуск
Name: "{group}\Zapret Custom"; Filename: "{app}\ZapretCustom.exe"; WorkingDir: "{app}"; IconFilename: "{app}\icon.ico"; Comment: "Запустить Zapret Custom 0.2"

; Ярлык удаления в меню Пуск
Name: "{group}\{cm:UninstallProgram,Zapret Custom}"; Filename: "{uninstallexe}"

; Ярлык на рабочем столе
Name: "{autodesktop}\Zapret Custom"; Filename: "{app}\ZapretCustom.exe"; WorkingDir: "{app}"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon; Comment: "Запустить Zapret Custom 0.2"

; Ярлык быстрого запуска
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\Zapret Custom"; Filename: "{app}\ZapretCustom.exe"; WorkingDir: "{app}"; Tasks: quicklaunchicon

[Run]
; Запуск после установки
Filename: "{app}\ZapretCustom.exe"; Description: "{cm:LaunchProgram,Zapret Custom}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Удаление файлов настроек при деинсталляции
Type: files; Name: "{app}\settings.json"
Type: filesandordirs; Name: "{app}\lists"
Type: filesandordirs; Name: "{app}\_internal"

[Code]
// Проверка версии Windows
function InitializeSetup(): Boolean;
var
  Version: TWindowsVersion;
begin
  GetWindowsVersionEx(Version);
  
  // Проверяем, что это Windows 10 или новее
  if Version.Major < 10 then
  begin
    MsgBox('Для работы Zapret Custom требуется Windows 10 или новее.' + #13#10 + 
           'Установка будет прервана.', mbError, MB_OK);
    Result := False;
  end
  else
    Result := True;
end;

// Сообщение о завершении установки
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Здесь можно добавить дополнительные действия после установки
  end;
end;

[Messages]
; Пользовательские сообщения на русском
russian.WelcomeLabel2=Программа установит [name/ver] на ваш компьютер.%n%nZapret Custom - графический интерфейс для обхода блокировок Discord и YouTube.%n%nРекомендуется закрыть все другие приложения перед продолжением.
russian.FinishedHeadingLabel=Завершение установки [name]
russian.FinishedLabelNoIcons=Программа [name] успешно установлена.%n%nДля корректной работы требуются права администратора при запуске.
russian.FinishedLabel=Программа [name] успешно установлена.%n%n ВАЖНО: Для корректной работы запускайте программу от имени администратора!

; Английские сообщения
english.WelcomeLabel2=This will install [name/ver] on your computer.%n%nZapret Custom is a GUI for bypassing Discord and YouTube blocks.%n%nIt is recommended that you close all other applications before continuing.
english.FinishedHeadingLabel=Completing [name] Setup
english.FinishedLabelNoIcons=[name] has been successfully installed.%n%nAdministrator rights are required for proper operation.
english.FinishedLabel=[name] has been successfully installed.%n%n IMPORTANT: Run the program as administrator for proper operation!
