ECHO OFF
setLocal Enabledelayedexpansion
set /A num=1
for %%i in (".\CleaningCoagulation\*.mp4") do (
ffmpeg -i "%%i" -q:v 6 .\CleaningCoagulation\CleaningCoagulation!num!.avi
set /A num=!num!+1
) 
PAUSE