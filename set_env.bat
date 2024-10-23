@echo off
setlocal enabledelayedexpansion
:: Define LF (Line Feed) at the start of your script
set ^"LF=^

^" The empty line above is critical - do not remove

set PULUMI_MANAGED_VENV=runtime:  name: python  options:    toolchain: pip    virtualenv: .venv
set MANUAL_DEP_INSTRUCTIONS=Please comment out the following three lines 'Pulumi.yaml' to enable manual dependency management with Pulumi:!LF!  # options:!LF!  #   toolchain: pip!LF!  #   virtualenv: .venv!LF!Then install dependencies manually (make sure to address any conflicts pip identifies):!LF!  pip install -r requirements.txt

:: Function to check for DataRobot Codespaces environment
call :check_datarobot_environment || exit /b

:: Function to load .env file
call :load_env_file || exit /b

:: Function to activate the virtual environment if it exists
call :activate_virtual_environment

:: Function to check for active conda environment
call :check_active_conda_env || exit /b

endlocal
call :set_env_vars

exit /b


:check_datarobot_environment
    if defined DATAROBOT_NOTEBOOK_IMAGE (
        findstr /C:"%PULUMI_MANAGED_VENV%" Pulumi.yaml >nul
        if %errorlevel% equ 0 (
            echo DR Codespaces requires manual management of dependencies.
            echo !MANUAL_DEP_INSTRUCTIONS!
            exit /b 1
        )
    )
    exit /b 0

:check_active_conda_env
    @REM echo DEBUG: Entering check_active_conda_env function
    @REM echo DEBUG: CONDA_DEFAULT_ENV = %CONDA_DEFAULT_ENV%
    
    if not defined CONDA_DEFAULT_ENV (
        @REM echo DEBUG: No active conda environment detected
        @REM echo DEBUG: Exiting check_active_conda_env function with errorlevel 0
        exit /b 0
    )
    
    @REM echo DEBUG: Conda environment is active

    if not exist Pulumi.yaml (
        @REM echo DEBUG: Pulumi.yaml file not found
        @REM echo DEBUG: Exiting check_active_conda_env function with errorlevel 0
        exit /b 0
    )

    @REM echo DEBUG: Contents of Pulumi.yaml:
    @REM type Pulumi.yaml
    @REM echo.
    
    @REM echo DEBUG: Searching for uncommented configuration lines...
    
    set "found_options="
    set "found_toolchain="
    set "found_virtualenv="
    
    for /f "usebackq tokens=*" %%a in (`findstr /R /C:"^  options:$" /C:"^    toolchain: pip$" /C:"^    virtualenv: \.venv$" Pulumi.yaml ^| findstr /V /R /C:"^#"`) do (
        @REM echo DEBUG: Found line: %%a
        if "%%a"=="options:" set "found_options=1"
        if "%%a"=="toolchain: pip" set "found_toolchain=1"
        if "%%a"=="virtualenv: .venv" set "found_virtualenv=1"
    )
    
    @REM echo DEBUG: found_options=%found_options%
    @REM echo DEBUG: found_toolchain=%found_toolchain%
    @REM echo DEBUG: found_virtualenv=%found_virtualenv%
    
    if defined found_options if defined found_toolchain if defined found_virtualenv (
        @REM echo DEBUG: All uncommented configuration lines found
        echo Using Pulumi with conda requires manual management of dependencies.
        echo !MANUAL_DEP_INSTRUCTIONS!
        @REM echo DEBUG: Exiting with errorlevel 1
        exit /b 1
    ) else (
        @REM echo DEBUG: Not all uncommented configuration lines were found
    )
    
    @REM echo DEBUG: Exiting check_active_conda_env function with errorlevel 0
    exit /b 0

:load_env_file
    if not exist .env (
        echo Error: .env file not found.
        echo Please create a .env file with VAR_NAME=value pairs.
        exit /b 1
    )
    set "env_vars="
    > "%TEMP%\set_env_vars.cmd" (
        for /f "usebackq delims== tokens=1,*" %%a in (".env") do (
            set "key=%%a"
            set "value=%%b"
            set "value=!value:"=!"
            set "value=!value:'=!"
            echo set "%%a=!value!"
            set "env_vars=!env_vars! %%a"
            @REM echo Setting %%a=!value!
        )
    )
    echo Environment variables from .env have been set.
    exit /b 0

:activate_virtual_environment
    if exist .venv\Scripts\activate.bat (
        echo Activated virtual environment found at .venv\Scripts\activate.bat
        call .venv\Scripts\activate.bat
    )
    exit /b 0

:set_env_vars
    echo.
    echo Contents of temporary command file:
    echo -----------------------------------
    type "%TEMP%\set_env_vars.cmd"
    echo -----------------------------------
    echo.
    echo Executing temporary command file...
    endlocal
    call "%TEMP%\set_env_vars.cmd"
    del "%TEMP%\set_env_vars.cmd"
    exit /b 0


:check_active_conda_env
    if defined CONDA_DEFAULT_ENV (
        set "managed_env_config=  options:!LF!    toolchain: pip!LF!    virtualenv: .venv"
        findstr /C:"%managed_env_config%" Pulumi.yaml >nul
        if %errorlevel% equ 0 (
            echo Using Pulumi with conda requires manual management of dependencies.
            echo !MANUAL_DEP_INSTRUCTIONS!
            exit /b 1
        )
    )
    exit /b 0

