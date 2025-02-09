import subprocess
import shlex

def convert_480p(source):
    base_name = source.replace('.mp4', '')
    new_file_name = base_name + '_480.mp4'
    
    cmd = [
        '/usr/bin/ffmpeg',
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
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"FFMPEG Error: {e.stderr}")
        return False
    except Exception as e:
        print(f"General Error: {str(e)}")
        return False