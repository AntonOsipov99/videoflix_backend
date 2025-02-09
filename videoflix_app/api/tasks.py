import subprocess
import os

def convert_480p(source):
    file_name, _ = os.path.splitext(source)
    target = file_name + '_480p.mp4'
    source_linux = "/mnt/" + source.replace("\\", "/").replace("C:", "c")
    target_linux = "/mnt/" + target.replace("\\", "/").replace("C:", "c")
    cmd = 'ffmpeg -i "{}" -s hd480 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(source_linux, target_linux)
    run = subprocess.run(cmd, capture_output=True, shell=True)