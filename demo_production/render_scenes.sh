#!/usr/bin/env bash
set -e

BASE="/home/blank/sakshi-ai-hackathon/demo_production"
SLIDES="$BASE/slides"
AUDIO="$BASE/audio"
FRAMES="$BASE/avatar_frames"
SCENES="$BASE/scenes"

mkdir -p "$SCENES"

render_scene() {
  local num="$1"
  local slide="$2"
  local audio="$3"
  local out="$SCENES/scene_${num}.mp4"

  echo "=== Rendering Scene $num ($slide) ==="
  ffmpeg -y \
    -loop 1 -i "$SLIDES/$slide" \
    -stream_loop -1 -framerate 30 -i "$FRAMES/frame_%03d.png" \
    -i "$AUDIO/$audio" \
    -filter_complex "[0:v][1:v] overlay=x=W-w-50:y=H-h-40:shortest=1 [v]" \
    -map "[v]" -map 2:a \
    -c:v libx264 -preset fast -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k -ar 44100 \
    -shortest \
    "$out"
}

render_scene "1" "slide_1_hook.png" "scene_1_hook.mp3"
render_scene "2" "slide_2_diagnostic.png" "scene_2_diagnostic.mp3"
render_scene "3" "slide_3_dag.png" "scene_3_dag.mp3"
render_scene "4" "slide_4_bkt.png" "scene_4_bkt.mp3"
render_scene "5" "slide_5_misconception.png" "scene_5_misconception.mp3"
render_scene "6" "slide_6_scheduler.png" "scene_6_scheduler.mp3"
render_scene "7" "slide_7_teacher.png" "scene_7_teacher.mp3"
render_scene "8" "slide_8_outro.png" "scene_8_outro.mp3"

echo "=== Concatenating all scenes into final video ==="
cat << 'EOF' > "$BASE/concat_list.txt"
file 'scenes/scene_1.mp4'
file 'scenes/scene_2.mp4'
file 'scenes/scene_3.mp4'
file 'scenes/scene_4.mp4'
file 'scenes/scene_5.mp4'
file 'scenes/scene_6.mp4'
file 'scenes/scene_7.mp4'
file 'scenes/scene_8.mp4'
EOF

ffmpeg -y -f concat -safe 0 -i "$BASE/concat_list.txt" \
  -c copy \
  "/home/blank/sakshi-ai-hackathon/demo_video.mp4"

echo "🎉 Demo video rendered successfully at /home/blank/sakshi-ai-hackathon/demo_video.mp4"
ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 "/home/blank/sakshi-ai-hackathon/demo_video.mp4"
