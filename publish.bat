@echo off
setlocal
set NODE=C:\Users\a'su's\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin\node.exe
set PY=C:\Users\a'su's\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe
set PATH=C:\Users\a'su's\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin;%PATH%
cd /d "%~dp0"
echo [1/3] clean...
"%NODE%" .\node_modules\hexo\bin\hexo clean
echo [2/3] generate...
"%NODE%" .\node_modules\hexo\bin\hexo generate
echo [3/3] publish to GitHub Pages...
"%PY%" deploy-pages.py
if errorlevel 1 (
  echo.
  echo PUBLISH FAILED.
  pause
  exit /b 1
)
echo.
echo Live: https://jnhjjbj.github.io/buzhidaoo/   (wait ~1 min)
pause