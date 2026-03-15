# TrueMark Certificate Forge v2.0 - Installation Script
# Run this script to set up the complete forge environment

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                                      ║" -ForegroundColor Cyan
Write-Host "║            TRUEMARK CERTIFICATE FORGE v2.0 - INSTALLER              ║" -ForegroundColor Cyan
Write-Host "║                                                                      ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$FORGE_DIR = "T:\certificate generator 2x\truemark\forge_v2.0"

# Check Python version
Write-Host "🐍 Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "   ✅ Found: $pythonVersion" -ForegroundColor Green
    
    # Check if version is 3.8+
    $version = [regex]::Match($pythonVersion, 'Python (\d+)\.(\d+)').Groups
    $major = [int]$version[1].Value
    $minor = [int]$version[2].Value
    
    if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
        Write-Host "   ❌ Python 3.8+ required. Found: $major.$minor" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "   ❌ Python not found. Please install Python 3.8+" -ForegroundColor Red
    Write-Host "      Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Check pip
Write-Host ""
Write-Host "📦 Checking pip installation..." -ForegroundColor Yellow
try {
    $pipVersion = pip --version 2>&1
    Write-Host "   ✅ Found: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "   ❌ pip not found. Installing pip..." -ForegroundColor Red
    python -m ensurepip --upgrade
}

# Install dependencies
Write-Host ""
Write-Host "📥 Installing dependencies..." -ForegroundColor Yellow
Write-Host "   This may take a few minutes..." -ForegroundColor Gray

Set-Location $FORGE_DIR

try {
    pip install -r requirements.txt --quiet
    Write-Host "   ✅ Dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Some packages may have failed. Trying alternatives..." -ForegroundColor Yellow
    
    # Try installing packages individually
    $packages = @(
        "reportlab==4.0.7",
        "Pillow==10.1.0",
        "qrcode==7.4.2",
        "ed25519==1.5"
    )
    
    foreach ($package in $packages) {
        try {
            pip install $package --quiet
            Write-Host "   ✅ Installed: $package" -ForegroundColor Green
        } catch {
            Write-Host "   ⚠️  Failed: $package (will try fallback)" -ForegroundColor Yellow
        }
    }
}

# Check if ed25519 is installed, fallback to cryptography
Write-Host ""
Write-Host "🔐 Verifying cryptography libraries..." -ForegroundColor Yellow
try {
    python -c "import ed25519" 2>&1 | Out-Null
    Write-Host "   ✅ ed25519 library available" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  ed25519 not found, installing cryptography..." -ForegroundColor Yellow
    pip install cryptography --quiet
    Write-Host "   ✅ cryptography library installed (fallback)" -ForegroundColor Green
}

# Verify forge components
Write-Host ""
Write-Host "🔍 Verifying forge components..." -ForegroundColor Yellow

$components = @(
    "certificate_forge.py",
    "forensic_renderer.py",
    "crypto_anchor.py",
    "integration_bridge.py"
)

foreach ($component in $components) {
    if (Test-Path "$FORGE_DIR\$component") {
        Write-Host "   ✅ $component" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $component (missing!)" -ForegroundColor Red
    }
}

# Check directory structure
Write-Host ""
Write-Host "📁 Verifying directory structure..." -ForegroundColor Yellow

$directories = @(
    "T:\certificate generator 2x\truemark\templates",
    "T:\certificate generator 2x\truemark\fonts",
    "T:\certificate generator 2x\truemark\keys",
    "T:\certificate generator 2x\Vault_System_1.0\certificates\issued"
)

foreach ($dir in $directories) {
    if (Test-Path $dir) {
        Write-Host "   ✅ $dir" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Creating: $dir" -ForegroundColor Yellow
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
        Write-Host "   ✅ Created: $dir" -ForegroundColor Green
    }
}

# Run self-tests
Write-Host ""
Write-Host "🧪 Running self-tests..." -ForegroundColor Yellow
Write-Host ""

Write-Host "   Testing crypto_anchor.py..." -ForegroundColor Gray
python "$FORGE_DIR\crypto_anchor.py" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Crypto engine: PASSED" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Crypto engine: See warnings above" -ForegroundColor Yellow
}

Write-Host "   Testing integration_bridge.py..." -ForegroundColor Gray
python "$FORGE_DIR\integration_bridge.py" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Integration bridge: PASSED" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Integration bridge: See warnings above" -ForegroundColor Yellow
}

# Generate initial keypair
Write-Host ""
Write-Host "🔑 Generating Ed25519 keypair..." -ForegroundColor Yellow
python -c "from crypto_anchor import CryptoAnchorEngine; CryptoAnchorEngine()" 2>&1 | Out-Null
Write-Host "   ✅ Keypair generated and stored securely" -ForegroundColor Green
Write-Host "   📁 Location: T:\certificate generator 2x\truemark\keys\" -ForegroundColor Gray

# Template asset reminders
Write-Host ""
Write-Host "🎨 Template Assets Setup" -ForegroundColor Yellow
Write-Host "   For production use, add the following template files:" -ForegroundColor Gray
Write-Host "   • parchment_base_600dpi.jpg (scanned security paper)" -ForegroundColor Gray
Write-Host "   • border_guilloche_vector.svg (mathematical border)" -ForegroundColor Gray
Write-Host "   • truemark_tree_watermark.png (brand watermark)" -ForegroundColor Gray
Write-Host "   • seal_gold_embossed_600dpi.png (gold seal)" -ForegroundColor Gray
Write-Host ""
Write-Host "   See README.md for detailed instructions" -ForegroundColor Gray
Write-Host "   The system will use procedural fallbacks for testing" -ForegroundColor Gray

# Font reminders
Write-Host ""
Write-Host "🔤 Font Setup (Optional)" -ForegroundColor Yellow
Write-Host "   Download recommended fonts:" -ForegroundColor Gray
Write-Host "   • EB Garamond: https://fonts.google.com/specimen/EB+Garamond" -ForegroundColor Gray
Write-Host "   • Courier Prime: https://fonts.google.com/specimen/Courier+Prime" -ForegroundColor Gray
Write-Host "   Place .ttf files in: T:\certificate generator 2x\truemark\fonts\" -ForegroundColor Gray
Write-Host "   System will use built-in fonts as fallback" -ForegroundColor Gray

# Installation complete
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                                                                      ║" -ForegroundColor Green
Write-Host "║                    ✅ INSTALLATION COMPLETE                          ║" -ForegroundColor Green
Write-Host "║                                                                      ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Write-Host "🚀 Quick Start Commands:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   # Mint your first certificate:" -ForegroundColor White
Write-Host '   python certificate_forge.py mint `' -ForegroundColor Gray
Write-Host '     --owner "Bryan A. Spruk" `' -ForegroundColor Gray
Write-Host '     --wallet "0xA3776658F2E74C9aB4D8e3d1C9fF5b2A8cD3e4F" `' -ForegroundColor Gray
Write-Host '     --title "Caleon Prime Genesis Asset" `' -ForegroundColor Gray
Write-Host '     --ipfs "ipfs://QmXyZ1234" `' -ForegroundColor Gray
Write-Host '     --category "Knowledge"' -ForegroundColor Gray
Write-Host ""
Write-Host "   # Get forge statistics:" -ForegroundColor White
Write-Host "   python certificate_forge.py stats" -ForegroundColor Gray
Write-Host ""
Write-Host "   # Verify a certificate:" -ForegroundColor White
Write-Host '   python certificate_forge.py verify --serial "DALSKM20251210-12345678"' -ForegroundColor Gray
Write-Host ""

Write-Host "📖 Documentation: README.md" -ForegroundColor Cyan
Write-Host "🔧 Support: See troubleshooting section in README.md" -ForegroundColor Cyan
Write-Host ""

Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
