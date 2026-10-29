@echo off
setlocal EnableDelayedExpansion

title TicketFlow - Application Shutdown
cd /d "%~dp0"

echo ============================================================
echo   TicketFlow - Application Shutdown Utility
echo ============================================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$conn = Get-NetTCPConnection -LocalPort 8501 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1;" ^
  "if (-not $conn) { Write-Host '[*] TicketFlow is NOT currently running on port 8501. Nothing to stop.' -ForegroundColor Yellow; exit 0 };" ^
  "$proc = Get-CimInstance Win32_Process -Filter ('ProcessId = ' + $conn.OwningProcess) -ErrorAction SilentlyContinue;" ^
  "if (-not ($proc.CommandLine -match 'streamlit')) { Write-Host ('[WARNING] Port 8501 is occupied by an unverified process (PID: ' + $conn.OwningProcess + '). TicketFlow will NOT terminate an unrelated process.') -ForegroundColor Red; exit 1 };" ^
  "Write-Host ('[*] Verified active TicketFlow instance: PID ' + $conn.OwningProcess + ' on port 8501.') -ForegroundColor Cyan;" ^
  "if ('%~1' -ne '/y' -and '%~1' -ne '-y') { $ans = Read-Host 'Are you sure you want to stop TicketFlow? [Y/N]'; if ($ans -notmatch '^[yY]') { Write-Host '[*] Shutdown cancelled by user. TicketFlow remains running.' -ForegroundColor Yellow; exit 0 } };" ^
  "Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue;" ^
  "Write-Host '[SUCCESS] TicketFlow has been stopped successfully.' -ForegroundColor Green;"

echo.
if /I not "%~1"=="/y" if /I not "%~1"=="-y" pause
