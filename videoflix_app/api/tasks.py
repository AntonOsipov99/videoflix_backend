import subprocess

def convert_480p(source):
    base_name = source.replace('.mp4', '')
    new_file_name = base_name + '_480.mp4'
    cmd = [
            'ffmpeg',
            '-i',
            source,
            '-s',
            'hd480',
            '-c:v',
            'libx264',
            '-crf',
            '23',
            '-c:a',
            'aac',
            '-strict',
            '-2',
            new_file_name
        ]
    run = subprocess.run(cmd, capture_output=True)