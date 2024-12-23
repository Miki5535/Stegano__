[Setup]
AppName=My Python App
AppVersion=1.0
DefaultDirName={pf}\MyPythonApp
DefaultGroupName=My Python App
OutputBaseFilename=MyPythonApp_Setup
Compression=lzma
SolidCompression=yes

[Files]
Source: "C:\Users\65011\Desktop\Segano\work00002\dist\main.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\65011\Desktop\Segano\work00002\dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\My Python App"; Filename: "{app}\main.exe"
Name: "{group}\Uninstall My Python App"; Filename: "{uninstallexe}"
