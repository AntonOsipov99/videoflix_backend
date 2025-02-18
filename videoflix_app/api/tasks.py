import subprocess
import os
from celery import shared_task

@shared_task
def convert_480p(source):
    file_name, _ = os.path.splitext(source)
    target = file_name + '_480p.mp4'
    source_linux = source.replace("\\", "/").replace("C:", "/mnt/c")
    target_linux = target.replace("\\", "/").replace("C:", "/mnt/c")
    
    cmd = [
        'ffmpeg',
        '-i', source_linux,
        '-s', 'hd480',
        '-c:v', 'libx264',
        '-crf', '23',
        '-c:a', 'aac',
        '-strict', '-2',
        target_linux
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True  # Wirft eine Exception bei Fehlern
        )
        print(f"Konvertierung erfolgreich: {target_linux}")
        return target_linux
    except subprocess.CalledProcessError as e:
        print(f"Fehler bei der Konvertierung: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        raise
