@echo off
setlocal
set NODE=C:\Users\a'su's\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin\node.exe
set PY=C:\Users\a'su's\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe
set PATH=C:\Users\a'su's\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin;%PATH%
cd /d "%~dp0"
echo [1/1] publish: GitHub Pages + Netlify (auto build)
"%PY%" publish-all.py
if errorlevel 1 (
  echo.
  echo PUBLISH FAILED.
  pause
  exit /b 1
)
echo.
echo GitHub Pages : https://jnhjjbj.github.io/buzhidaoo/     (about 1 min)
echo Netlify      : https://serene-elf-swws.netlify.app     (auto build, about 1 min)
pause