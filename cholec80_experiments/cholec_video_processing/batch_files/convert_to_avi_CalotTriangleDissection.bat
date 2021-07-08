ECHO OFF
setLocal Enabledelayedexpansion
set /A num=1
for %%i in (".\CalotTriangleDissection\*.mp4") do (
ffmpeg -i "%%i" -q:v 6 .\CalotTriangleDissection\CalotTriangleDissection!num!.avi
set /A num=!num!+1
) 
PAUSE