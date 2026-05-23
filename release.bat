@echo off
REM ==========================================
REM XM全能营销助手 - 版本发布脚本
REM 用法: release.bat <类型>
REM   类型: patch | minor | major
REM   示例: release.bat patch  (1.0.0 -> 1.0.1)
REM         release.bat minor  (1.0.0 -> 1.1.0)
REM         release.bat major  (1.0.0 -> 2.0.0)
REM ==========================================

if "%1"=="" (
    echo 用法: release.bat patch^|minor^|major
    exit /b 1
)

REM 读取当前版本
for /f "tokens=3" %%a in ('findstr "VERSION " VERSION.txt') do set ver=%%a
echo 当前版本: %ver%

REM 解析版本号
for /f "tokens=1,2,3 delims=." %%a in ("%ver%") do (
    set major=%%a
    set minor=%%b
    set patch=%%c
)

if "%1"=="patch" set /a patch+=1
if "%1"=="minor" (set /a minor+=1 & set patch=0)
if "%1"=="major" (set /a major+=1 & set minor=0 & set patch=0)

set newver=%major%.%minor%.%patch%
echo 新版本: %newver%

REM 更新 VERSION.txt
powershell -Command "(Get-Content VERSION.txt) -replace 'VERSION = [\d.]+', 'VERSION = %newver%' | Set-Content VERSION.txt"

REM 更新 main.py
powershell -Command "(Get-Content main.py) -replace 'VERSION = \"[\d.]+\"', 'VERSION = \"%newver%\"' | Set-Content main.py"

REM 更新 src/__init__.py
powershell -Command "(Get-Content src\__init__.py) -replace '__version__ = \"[\d.]+\"', '__version__ = \"%newver%\"' | Set-Content src\__init__.py"

REM 更新 pyproject.toml
powershell -Command "(Get-Content pyproject.toml) -replace 'version = \"[\d.]+\"', 'version = \"%newver%\"' | Set-Content pyproject.toml"

echo.
echo 版本已更新: %ver% ^-^> %newver%

REM 提交 + 打标签
git add -A
git commit -m "chore: bump version to %newver%"
git tag v%newver%
git push origin master
git push origin v%newver%

echo.
echo 已推送 v%newver% 到 GitHub
echo.
