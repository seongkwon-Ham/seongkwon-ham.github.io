@echo off
rem Double-click to rebuild the site and upload it to GitHub.
rem Edit content\ or static\ first. The live site updates 1-2 minutes after this finishes.
cd /d "%~dp0"
echo [1/3] Building the site into docs\ ...
python build.py
if errorlevel 1 goto failed
echo.
echo [2/3] Saving a version (commit) ...
git add -A
git commit -m "Update site"
echo.
echo [3/3] Uploading to GitHub (push) ...
git push
if errorlevel 1 goto failed
echo.
echo Done. Check https://seongkwon-ham.github.io in 1-2 minutes.
pause
exit /b 0
:failed
echo.
echo Something went wrong. Read the message above, or ask Claude.
pause
exit /b 1
