@echo off
setlocal
set NODE=C:\Users\a'su's\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin\node.exe
set PATH=C:\Users\a'su's\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin;%PATH%
cd /d "%~dp0"
echo [1/2] clean...
"%NODE%" .\node_modules\hexo\bin\hexo clean
echo [2/2] generate...
"%NODE%" .\node_modules\hexo\bin\hexo generate
echo.
echo Built into public\ (GitHub Pages layout, root=/buzhidaoo/)
echo For local look: run preview.bat
echo To publish:     run publish.bat
pause