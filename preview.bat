@echo off
setlocal
set NODE=C:\Users\a'su's\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin\node.exe
set PATH=C:\Users\a'su's\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin;%PATH%
cd /d "%~dp0"
echo Starting local preview at http://localhost:4000
echo Close this window to stop.
"%NODE%" .\node_modules\hexo\bin\hexo server -p 4000
pause