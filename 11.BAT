@echo off
setlocal

cd /d C:\paprika

echo.
echo ============================================================
echo PAPRIKA - FIRST CLEAN GITHUB SYNC
echo ============================================================
echo.
echo This operation will replace the GitHub main branch with
echo the current PAPRIKA project on this computer.
echo.
echo Large models and media will NOT be uploaded.
echo.
pause

echo.
echo [1/9] Checking current Git status...
git status

echo.
echo [2/9] Creating local backup branch...

git branch backup-before-clean-sync

if errorlevel 1 (
    echo.
    echo WARNING: Backup branch may already exist.
)

echo.
echo [3/9] Creating clean orphan branch...

git checkout --orphan clean-main

if errorlevel 1 (
    echo.
    echo ERROR: Could not create clean branch.
    pause
    exit /b 1
)

echo.
echo [4/9] Removing old tracked files from the new branch...

git rm -r --cached . 2>nul

echo.
echo [5/9] Rebuilding Git index from current project...

git add .

if errorlevel 1 (
    echo.
    echo ERROR: git add failed.
    echo.
    echo Check the messages above.
    pause
    exit /b 1
)

echo.
echo [6/9] Showing files that will be uploaded...

git status

echo.
echo ============================================================
echo IMPORTANT
echo ============================================================
echo.
echo The files above are the files that will be uploaded.
echo.
echo *.pt / *.pth / media / results / models / databases
echo should NOT appear as new files.
echo.
pause

echo.
echo [7/9] Creating clean Git commit...

git commit -m "PAPRIKA clean project sync"

if errorlevel 1 (
    echo.
    echo ERROR: Commit failed.
    pause
    exit /b 1
)

echo.
echo [8/9] Replacing local main branch...

git branch -M main

if errorlevel 1 (
    echo.
    echo ERROR: Could not rename branch to main.
    pause
    exit /b 1
)

echo.
echo [9/9] Force pushing clean project to GitHub...

git push origin main --force

if errorlevel 1 (
    echo.
    echo ============================================================
    echo ERROR: GitHub push failed.
    echo ============================================================
    echo.
    echo The local project has NOT been deleted.
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo PAPRIKA - CLEAN GITHUB SYNC COMPLETED
echo ============================================================
echo.
echo GitHub main now contains the current project files.
echo.
echo Excluded from GitHub:
echo     AI model files
echo     Images
echo     Videos
echo     Results
echo     Local datasets
echo     Databases
echo.
echo Included:
echo     Source code
echo     Python files
echo     Project configuration
echo     Documentation
echo     .gitkeep directory structure
echo.
echo ============================================================
echo.

git status

echo.
pause