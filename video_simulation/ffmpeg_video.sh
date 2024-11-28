rm -rf temp
mkdir temp


ffmpeg -threads 0 -i assets/video.mkv \
-c:v libx264 \
-preset superfast \
-tune zerolatency \
-profile:v baseline \
-level 3.0 \
-pix_fmt yuv420p \
-g 60 \
-sc_threshold 0 \
-bufsize 2M \
-maxrate 2M \
-f segment \
-segment_time 4 \
-segment_format mpegts \
"temp/segment_%d.ts"