@echo off
pyinstaller ^
  --onefile ^
  --clean ^
  --noupx ^
  --win-private-assemblies ^
  --noconsole ^
  --icon .\pivimage.ico ^
  --noconfirm ^
  --add-binary "Ressources\opencv_ffmpeg344.dll;." ^
  --add-binary "Ressources\opencv_ffmpeg344_64.dll;." ^
  pivimage.py
pause
