@echo off
call "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat" -vcvars_ver=14.44
if errorlevel 1 exit /b %errorlevel%
"C:\Program Files\Microsoft Visual Studio\18\Community\VC\Tools\MSVC\14.44.35207\bin\Hostx64\x64\cl.exe" /O2 /std:c11 /TC /Fe:"C:\Users\ikuto\projects\conway-99-graph\build\rook-drat-checker\drat-trim.exe" /Fo:"C:\Users\ikuto\projects\conway-99-graph\build\rook-drat-checker\drat-trim.obj" "C:\Users\ikuto\projects\conway-99-graph\build\rook-drat-checker\drat-trim.c"
exit /b %errorlevel%
