@echo off
setlocal

cd /d C:\paprika

echo.
echo ============================================================
echo PAPRIKA - GIT UPDATE
echo ============================================================
echo.

echo [1/7] Checking Git status...
git status

echo.
echo [2/7] Updating .gitignore...

(
echo # ============================================================
echo # PAPRIKA - GITIGNORE
echo # ============================================================
echo.
echo # Python
echo venv/
echo __pycache__/
echo *.pyc
echo *.pyo
echo *.pyd
echo.
echo # Environment / local settings
echo .env
echo .env.*
echo.
echo # IDE
echo .idea/
echo .vscode/
echo.
echo # Logs
echo *.log
echo.
echo # ============================================================
echo # DATA
echo # ============================================================
echo data/raw/*
echo data/processed/*
echo data/train/*
echo data/validation/*
echo data/test/*
echo.
echo !data/raw/.gitkeep
echo !data/processed/.gitkeep
echo !data/train/.gitkeep
echo !data/validation/.gitkeep
echo !data/test/.gitkeep
echo.
echo # ============================================================
echo # AI MODELS
echo # ============================================================
echo models/*
echo *.pt
echo *.pth
echo *.onnx
echo *.engine
echo *.safetensors
echo *.ckpt
echo.
echo !models/.gitkeep
echo.
echo # ============================================================
echo # RESULTS
echo # ============================================================
echo results/*
echo.
echo !results/.gitkeep
echo.
echo # ============================================================
echo # MEDIA FILES
echo # ============================================================
echo *.jpg
echo *.jpeg
echo *.png
echo *.bmp
echo *.tif
echo *.tiff
echo *.webp
echo *.gif
echo *.heic
echo *.heif
echo.
echo *.mp4
echo *.avi
echo *.mov
echo *.mkv
echo *.webm
echo *.flv
echo *.wmv
echo *.mpeg
echo *.mpg
echo.
echo *.mp3
echo *.wav
echo *.aac
echo *.flac
echo *.ogg
echo *.m4a
echo.
echo # ============================================================
echo # LOCAL IMAGES DIRECTORY
echo # ============================================================
echo images/*
echo !images/.gitkeep
echo.
echo # ============================================================
echo # DATABASES
echo # ============================================================
echo *.db
echo *.sqlite
echo *.sqlite3
echo.
echo # ============================================================
echo # OPERATING SYSTEM
echo # ============================================================
echo .DS_Store
echo Thumbs.db
echo desktop.ini
) > .gitignore

if errorlevel 1 (
    echo.
    echo ERROR: Could not create .gitignore
    pause
    exit /b 1
)

echo.
echo [3/7] Creating .gitkeep files...

if not exist data\raw mkdir data\raw
if not exist data\processed mkdir data\processed
if not exist data\train mkdir data\train
if not exist data\validation mkdir data\validation
if not exist data\test mkdir data\test
if not exist images mkdir images
if not exist models mkdir models
if not exist results mkdir results

if not exist data\raw\.gitkeep type nul > data\raw\.gitkeep
if not exist data\processed\.gitkeep type nul > data\processed\.gitkeep
if not exist data\train\.gitkeep type nul > data\train\.gitkeep
if not exist data\validation\.gitkeep type nul > data\validation\.gitkeep
if not exist data\test\.gitkeep type nul > data\test\.gitkeep
if not exist images\.gitkeep type nul > images\.gitkeep
if not exist models\.gitkeep type nul > models\.gitkeep
if not exist results\.gitkeep type nul > results\.gitkeep

echo.
echo [4/7] Removing large model files from current Git tracking...

git rm --cached --ignore-unmatch "*.pt"
git rm --cached --ignore-unmatch "*.pth"
git rm --cached --ignore-unmatch "*.onnx"
git rm --cached --ignore-unmatch "*.engine"
git rm --cached --ignore-unmatch "*.safetensors"
git rm --cached --ignore-unmatch "*.ckpt"

echo.
echo [5/7] Adding project files...

git add .

if errorlevel 1 (
    echo.
    echo ERROR: git add failed.
    pause
    exit /b 1
)

echo.
echo [6/7] Creating commit...

git diff --cached --quiet

if errorlevel 1 (
    git commit -m "PAPRIKA update %date% %time%"

    if errorlevel 1 (
        echo.
        echo ERROR: Commit failed.
        pause
        exit /b 1
    )
) else (
    echo.
    echo No new changes to commit.
)

echo.
echo [7/7] Pushing to GitHub...

git push

if errorlevel 1 (
    echo.
    echo ============================================================
    echo ERROR: GitHub push failed.
    echo ============================================================
    echo.
    echo The current files are protected by .gitignore.
    echo.
    echo If GitHub still reports a large .pt file such as:
    echo     sam2.1_b.pt
    echo     sam2.1_t.pt
    echo.
    echo that file exists in an older Git commit history.
    echo .gitignore cannot remove files from old commits.
    echo.
    echo The local model files have NOT been deleted.
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo GIT UPDATE COMPLETED
echo ============================================================
echo.
echo Project code and allowed files were synchronized.
echo.
echo Ignored:
echo     Media files
echo     AI model files
echo     Results
echo     Local datasets
echo     Databases
echo.
echo Kept in GitHub:
echo     Project directories via .gitkeep
echo     Source code
echo     Python files
echo     Configuration files
echo     Documentation
echo.
pause