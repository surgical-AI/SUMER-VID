ECHO OFF
setLocal Enabledelayedexpansion
set /A num=1
for %%i in (".\GallbladderDissection\*.mp4") do (
ffmpeg -i "%%i" -q:v 6 .\GallbladderDissection\GallbladderDissection!num!.avi
set /A num=!num!+1
) 
PAUSE