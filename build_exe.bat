@echo off
chcp 65001 >nul
echo ========================================
echo    MUSIC LYRICS FETCHER BUILDER
echo ========================================
echo.

REM Check if source file exists
if not exist "music_lyrics_gui.py" (
    echo [❌] ERROR: File music_lyrics_gui.py not found!
    pause
    exit /b 1
)
echo [✓] File music_lyrics_gui.py found

REM Check if icon exists
if not exist "MusicLyricsFetcher.ico" (
    echo [⚠] WARNING: Icon file MusicLyricsFetcher.ico not found!
    echo Building without icon...
    set ICON_OPTION=
    set ADD_DATA=
) else (
    echo [✓] Icon file found
    set ICON_OPTION=--icon="MusicLyricsFetcher.ico"
    set ADD_DATA=--add-data="MusicLyricsFetcher.ico;."
)
echo.

REM Create Ready folder
if not exist "Ready" mkdir Ready

REM Install dependencies
echo Installing dependencies...
pip install pyinstaller requests mutagen
if %errorlevel% neq 0 (
    echo [❌] Error installing dependencies
    pause
    exit /b 1
)
echo [✓] Dependencies installed
echo.

REM Create README.txt directly in Ready folder (simple method)
echo Creating README.txt in Ready folder...

echo ======================================== > "Ready\README.txt"
echo MUSIC LYRICS FETCHER >> "Ready\README.txt"
echo ======================================== >> "Ready\README.txt"
echo. >> "Ready\README.txt"
echo Version: 3.0.1 >> "Ready\README.txt"
echo Author: © 2026 Lyagoosh. >> "Ready\README.txt"
echo GitHub: https://github.com/Lyagoosh >> "Ready\README.txt"
echo. >> "Ready\README.txt"
echo ======================================== >> "Ready\README.txt"
echo DESCRIPTION >> "Ready\README.txt"
echo ======================================== >> "Ready\README.txt"
echo Music Lyrics Fetcher is a desktop application that >> "Ready\README.txt"
echo automatically adds lyrics to your audio files. >> "Ready\README.txt"
echo. >> "Ready\README.txt"
echo It supports both MP3 and FLAC formats and uses >> "Ready\README.txt"
echo multiple online sources to find the best matching >> "Ready\README.txt"
echo lyrics for your songs. >> "Ready\README.txt"
echo. >> "Ready\README.txt"
echo ======================================== >> "Ready\README.txt"
echo FEATURES >> "Ready\README.txt"
echo ======================================== >> "Ready\README.txt"
echo • Supports MP3 and FLAC audio formats >> "Ready\README.txt"
echo • Two lyrics sources: Lyrics.ovh and Lrclib.net >> "Ready\README.txt"
echo • Adjustable source priority order >> "Ready\README.txt"
echo • Auto-saves your folder settings >> "Ready\README.txt"
echo • Clean and simple interface >> "Ready\README.txt"
echo • Real-time progress tracking >> "Ready\README.txt"
echo • Color-coded execution log >> "Ready\README.txt"
echo • No API tokens required >> "Ready\README.txt"
echo. >> "Ready\README.txt"
echo ======================================== >> "Ready\README.txt"
echo HOW TO USE >> "Ready\README.txt"
echo ======================================== >> "Ready\README.txt"
echo 1. Launch the program >> "Ready\README.txt"
echo 2. Click "Browse..." to select folder with audio files >> "Ready\README.txt"
echo 3. Adjust source priority (optional) >> "Ready\README.txt"
echo 4. Click "START LYRICS SEARCH" >> "Ready\README.txt"
echo 5. Watch the progress in the log window >> "Ready\README.txt"
echo 6. Wait for completion >> "Ready\README.txt"
echo. >> "Ready\README.txt"
echo ======================================== >> "Ready\README.txt"
echo REQUIREMENTS >> "Ready\README.txt"
echo ======================================== >> "Ready\README.txt"
echo • Windows >> "Ready\README.txt"
echo • No additional software needed >> "Ready\README.txt"
echo • No API tokens or registration required >> "Ready\README.txt"
echo • Installed Python >> "Ready\README.txt"
echo. >> "Ready\README.txt"

if exist "Ready\README.txt" (
    echo [✓] README.txt created in Ready folder
) else (
    echo [❌] Failed to create README.txt
    pause
    exit /b 1
)
echo.

REM Build EXE with icon (with ADD_DATA to embed icon for window)
echo Building EXE with icon...
pyinstaller --onefile --windowed %ICON_OPTION% %ADD_DATA% --name="Music Lyrics Fetcher" music_lyrics_gui.py

if %errorlevel% neq 0 (
    echo [❌] Failed to build EXE
    pause
    exit /b 1
)
echo [✓] EXE built successfully

REM Check if EXE exists in dist
if not exist "dist\Music Lyrics Fetcher.exe" (
    echo [❌] EXE not found in dist folder!
    pause
    exit /b 1
)

REM Copy EXE to Ready folder
copy "dist\Music Lyrics Fetcher.exe" "Ready\" >nul
if %errorlevel% equ 0 (
    echo [✓] EXE copied to Ready folder
) else (
    echo [❌] Failed to copy EXE to Ready folder
    pause
    exit /b 1
)

REM Copy icon to Ready folder
if exist "MusicLyricsFetcher.ico" (
    copy "MusicLyricsFetcher.ico" "Ready\" >nul
    echo [✓] Icon copied to Ready folder
)

echo.
echo ========================================
echo    BUILD COMPLETED!
echo ========================================
echo.
echo Files in Ready folder:
dir "Ready\"

echo.
pause