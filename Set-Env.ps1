$MANUAL_DEP_INSTRUCTIONS = @"
Please comment out the following three lines 'Pulumi.yaml' to enable manual dependency management with Pulumi:
  # options:
  #   toolchain: pip
  #   virtualenv: .venv
Then install dependencies manually (make sure to address any conflicts pip identifies):
  pip install -r requirements.txt
"@

# Function to check for active conda environment
function Test-ActiveCondaEnv {
    if ($env:CONDA_DEFAULT_ENV) {
        $yamlContent = Get-Content -Path 'Pulumi.yaml' -Raw
        if ($yamlContent -match "runtime:\s*\n\s*name:\s*python\s*\n\s*options:\s*\n\s*toolchain:\s*pip\s*\n\s*virtualenv:\s*.venv") {
            Write-Host "Using Pulumi with conda requires manual management of dependencies."
            Write-Host $MANUAL_DEP_INSTRUCTIONS
            return $false
        }
    }
    return $true
}

# Function to load .env file
function Import-EnvFile {
    if (-not (Test-Path '.env')) {
        Write-Host "Error: .env file not found."
        Write-Host "Please create a .env file with VAR_NAME=value pairs."
        return $false
    }
    Get-Content '.env' | ForEach-Object {
        if ($_ -match '^(\w+)=(.*)$') {
            [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2].Trim('"'))
        }
    }
    Write-Host "Environment variables from .env have been set."
    return $true
}

# Function to activate the virtual environment if it exists
function Enable-VirtualEnvironment {
    if (Test-Path '.venv\Scripts\Activate.ps1') {
        Write-Host "Activated virtual environment found at .venv\Scripts\Activate.ps1"
        . '.venv\Scripts\Activate.ps1'
    }
}

# Main execution
if (Test-ActiveCondaEnv) {
    Enable-VirtualEnvironment
    Import-EnvFile
}
