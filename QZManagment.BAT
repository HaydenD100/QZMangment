@echo off
TITLE QZ Management - Data Pipeline Runner
COLOR 0A

:: ========================================================
:: STEP 1: LAUNCH AGENT (CLIENT SIDE)
:: ========================================================
ECHO.
ECHO [STEP 1/3] Launching SecureAgent.exe...
ECHO --------------------------------------------------------
ECHO INSTRUCTIONS:
ECHO  1. The Agent GUI will open.
ECHO  2. Enter Username/Password and click "SCAN NOW".
ECHO  3. Wait for the "Upload Complete" message.
ECHO  4. **CLOSE THE AGENT WINDOW** to continue this script.
ECHO.

:: Check if EXE exists
IF NOT EXIST "agent\dist\SecureAgent.exe" (
    COLOR 0C
    ECHO [ERROR] SecureAgent.exe not found! 
    ECHO Please build it using 'pyinstaller' inside the agent folder.
    PAUSE
    EXIT /B
)

:: "start /wait" pauses this script until you close the Agent window
start /wait agent\dist\SecureAgent.exe

CLS
ECHO.
ECHO [STEP 1 COMPLETE] Data sent to Server.
ECHO.

:: ========================================================
:: STEP 2: CLEAN DATA (SERVER SIDE)
:: ========================================================
ECHO [STEP 2/3] Normalizing Software Names (AI Cleaning)...
ECHO --------------------------------------------------------

:: Move into source folder so imports (like 'common') work correctly
CD src

:: We use -c to import the specific function because your __main__ block is commented out
python -c "from database import CleanSoftwareNames; CleanSoftwareNames()"

ECHO.

:: ========================================================
:: STEP 3: ENRICH DATA (SERVER SIDE)
:: ========================================================
ECHO [STEP 3/3] Enriching Data with NVD CVEs...
ECHO --------------------------------------------------------

:: Run the enrichment script
python enrichment.py

:: Return to root
CD ..

ECHO.
ECHO ========================================================
ECHO  PIPELINE COMPLETE
ECHO ========================================================
PAUSE
