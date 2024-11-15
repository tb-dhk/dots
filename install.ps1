# install.ps1
param (
    [string]$SourcePath = "src"
)

# Define paths
$DistPath = "dist"
$BinPath = "C:\Windows\System32"
$ConfigPath = "$HOME\.dots"

# Helper function to display error and exit
function ErrorExit {
    param([string]$Message)
    Write-Host "error: $Message" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "Installing dependencies..."
pip install -r "$SourcePath\requirements.txt" -ErrorAction Stop || ErrorExit "failed to install dependencies."

# Build with PyInstaller
Write-Host "Building project..."
if ($IsWindows) {
    pyinstaller --onefile --name=dots-windows.exe "$SourcePath\main.py" || ErrorExit "pyinstaller failed to build the project."
} else {
    ErrorExit "Unsupported operating system."
}

# Copy executable to System32 for easy access
if (!(Test-Path "$DistPath\dots-windows.exe")) {
    ErrorExit "no build artifact found. please build the project first."
}

Copy-Item "$DistPath\dots-windows.exe" -Destination "$BinPath\dots.exe" -Force -ErrorAction Stop || ErrorExit "failed to copy to System32. please ensure you have administrative rights."

# Set up .dots directory and config files
Write-Host "Setting up configuration files..."
New-Item -ItemType Directory -Path $ConfigPath -Force -ErrorAction Stop || ErrorExit "failed to create ~/.dots."

$DefaultFiles = @(
    @{ Path = "$ConfigPath\config.toml"; Source = "$SourcePath\config.toml"; DefaultContent = "" },
    @{ Path = "$ConfigPath\tasks.json"; DefaultContent = "{}" },
    @{ Path = "$ConfigPath\habits.json"; DefaultContent = "{}" },
    @{ Path = "$ConfigPath\lists.json"; DefaultContent = "{}" },
    @{ Path = "$ConfigPath\logs.json"; DefaultContent = "{}" }
)

foreach ($file in $DefaultFiles) {
    if (!(Test-Path $file.Path)) {
        if ($file.Source) {
            Copy-Item $file.Source -Destination $file.Path -ErrorAction Stop || ErrorExit "failed to copy $($file.Source) to $($file.Path)"
        } else {
            $file.DefaultContent | Out-File -FilePath $file.Path -Encoding UTF8 -Force || ErrorExit "failed to create $($file.Path)"
        }
        Write-Host "Created $($file.Path)"
    } else {
        Write-Host "Warning: $($file.Path) already exists. skipping..."
    }
}

Write-Host "dots installed successfully."
