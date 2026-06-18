; ============================================================
; 印流PDflow V1.2 — Inno Setup 安装脚本
; 编译方式: ISCC.exe PDflow_V1.2.iss
; ============================================================

#define MyAppName "印流PDflow"
#define MyAppVersion "1.2"
#define MyAppPublisher "印流PDflow"
#define MyAppExeName "PDflow_V1.2.exe"
#define MyAppIcon "..\assets\pdflow-logo.ico"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} V{#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
; 安装向导界面
WizardStyle=modern
WizardSizePercent=120,120
; 压缩设置
Compression=lzma2/ultra64
SolidCompression=yes
; 权限: 不需要管理员权限（默认安装到用户目录）
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
; 图标
SetupIconFile={#MyAppIcon}
UninstallDisplayIcon={app}\{#MyAppExeName}
; 输出设置
OutputDir=..\03-安装包输出
OutputBaseFilename=PDFlow_V1.2_Setup
; 界面语言
ShowLanguageDialog=auto

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式(&D)"; GroupDescription: "附加选项:"
Name: "startmenu"; Description: "创建开始菜单快捷方式(&S)"; GroupDescription: "附加选项:"

[Files]
; 主程序
Source: "..\dist\PDflow_V1.2\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; _internal 目录（所有依赖）
Source: "..\dist\PDflow_V1.2\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; 桌面快捷方式（仅在用户勾选时创建）
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
; 开始菜单
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startmenu
Name: "{group}\卸载 {#MyAppName}"; Filename: "{uninstallexe}"; Tasks: startmenu

[Run]
; 安装完成后启动应用
Filename: "{app}\{#MyAppExeName}"; Description: "启动 {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; 卸载时清理用户数据目录中的配置文件
Type: files; Name: "{userappdata}\印流PDflow\app_config.json"
