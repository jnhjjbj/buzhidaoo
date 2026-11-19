@echo off
setlocal
set NODE=C:\Users\a'su's\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin\node.exe
set PY=C:\Users\a'su's\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe
set PATH=C:\Users\a'su's\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin;%PATH%
cd /d "%~dp0"
echo Publish: GitHub Pages + Netlify package
"%PY%" publish-all.py
if errorlevel 1 (
  echo.
  echo PUBLISH FAILED.
  pause
  exit /b 1
)
echo.
echo GitHub Pages : https://jnhjjbj.github.io/buzhidaoo/   (about 1 min)
echo Netlify      : drag deploy-netlify.zip to https://app.netlify.com/drop
pause