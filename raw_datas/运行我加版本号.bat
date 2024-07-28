@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: 获取当前目录作为文件路径
set "filepath=%~dp0"

:: 提示用户输入版本号
echo 请输入版本号，例如： 11.0.2.55789
set /p version=

:: 检查版本号是否为空
if "%version%"=="" (
    echo 版本号为空，未执行任何操作。
    endlocal
    pause
    exit /b
)

:: 设置要处理的文件列表
set files=spell spellauraoptions spellduration spelleffect spellmisc spellname spellradius

:: 循环处理每个文件
for %%f in (%files%) do (
    if exist "%filepath%%%f.csv" (
        ren "%filepath%%%f.csv" "%%f_%version%.csv"
    ) else (
        echo 系统找不到指定的文件: %filepath%%%f.csv
    )
)

echo 文件重命名完成！

endlocal
pause
