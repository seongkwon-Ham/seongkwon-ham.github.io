@echo off
rem Double-click to check the site builds, then upload your changes to GitHub.
rem GitHub rebuilds and publishes the site 1-2 minutes after the upload.
rem (Edits made in the web editor at /admin do not need this file.)
cd /d "%~dp0"
echo [1/3] Checking that the site builds ...
python build.py
if errorlevel 1 goto failed
echo.
echo [2/3] Saving a version (commit) ...
git pull --rebase --autostash
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
