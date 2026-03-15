# Quick Test Script - Mint a Test Certificate
# Run this to verify the forge is working correctly

Write-Host ""
Write-Host "🧪 TrueMark Forge - Quick Test" -ForegroundColor Cyan
Write-Host "=" * 70
Write-Host ""

$FORGE_DIR = "T:\certificate generator 2x\truemark\forge_v2.0"
Set-Location $FORGE_DIR

# Generate test data
$timestamp = Get-Date -Format "yyyyMMddHHmmss"
$testOwner = "Test User $(Get-Random -Maximum 9999)"
$testWallet = "0x$(Get-Random -Maximum 99999999 | Format-Hex | Select-Object -ExpandProperty Hex)".PadRight(42, '0')
$testIPFS = "ipfs://QmTest$timestamp"

Write-Host "📝 Test Parameters:" -ForegroundColor Yellow
Write-Host "   Owner:    $testOwner" -ForegroundColor Gray
Write-Host "   Wallet:   $testWallet" -ForegroundColor Gray
Write-Host "   IPFS:     $testIPFS" -ForegroundColor Gray
Write-Host ""

Write-Host "🔨 Minting test certificate..." -ForegroundColor Yellow
Write-Host ""

python certificate_forge.py mint `
  --owner "$testOwner" `
  --wallet "$testWallet" `
  --title "Forge Test Certificate - $timestamp" `
  --ipfs "$testIPFS" `
  --category "Knowledge"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ TEST PASSED - Forge is operational!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📁 Check output directory:" -ForegroundColor Cyan
    Write-Host "   T:\certificate generator 2x\Vault_System_1.0\certificates\issued\" -ForegroundColor Gray
} else {
    Write-Host ""
    Write-Host "❌ TEST FAILED - See errors above" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "   1. Run: .\install.ps1" -ForegroundColor Gray
    Write-Host "   2. Check: pip install -r requirements.txt" -ForegroundColor Gray
    Write-Host "   3. See: README.md troubleshooting section" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
