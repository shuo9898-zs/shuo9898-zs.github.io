"""Build the homepage preview from DuoRoad's existing demo recordings.

Usage: python scripts/build_duoroad_preview.py /path/to/ffmpeg
"""
import argparse
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('ffmpeg', help='Path to an installed ffmpeg executable')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
media = root / 'dualsense' / 'media'
output = root / 'assets' / 'videos' / 'previews' / 'duoroad.mp4'
output.parent.mkdir(parents=True, exist_ok=True)
clips = [
    ('interaction-overview.mp4', 7.5),  # End before the static motion-capture figure.
    ('human-data-collection.mp4', 7.5),  # Live driver view, gaze, and segmentation.
    ('mm-av-data-collection.mp4', 5),  # Four live RGB camera views.
]
command = [args.ffmpeg, '-y']
filters = []
for index, (filename, duration) in enumerate(clips):
    command += ['-t', str(duration), '-i', str(media / filename)]
    filters.append(
        f'[{index}:v]setpts=PTS-STARTPTS,fps=24,'
        'scale=960:540:force_original_aspect_ratio=decrease,'
        'pad=960:540:(ow-iw)/2:(oh-ih)/2:color=white,setsar=1'
        f'[v{index}]'
    )
filters.append('[v0][v1][v2]concat=n=3:v=1:a=0[out]')
command += ['-filter_complex', ';'.join(filters), '-map', '[out]', '-an',
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '24',
            '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(output)]
subprocess.run(command, check=True)
print(output)
