"""
testing ffmpeg_extract_subclip
"""
import os
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

input_fname = os.path.join(r'C:\Users\Carla Pugh\Box\Pugh Lab Shared Drive\4. Data Base\ACS-October2019\ACS 2019 Aligned Videos', 'P001_G_N.Camera1.mkv')
output_fname = r'C:\Users\Carla Pugh\PycharmProjects\VideoSlicing\test_slice.mkv'
test_start_seconds = 0
test_stop_seconds = 10
# open up a video, slice the video, write the videoest_stop = 0
ffmpeg_extract_subclip(input_fname, test_start_seconds, test_stop_seconds, targetname=output_fname)



