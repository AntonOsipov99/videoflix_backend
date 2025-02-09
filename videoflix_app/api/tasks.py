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
        
    try:
            result = subprocess.run(cmd, 
                                capture_output=True, 
                                text=True,
                                check=True,
                                shell=False)
            return result
    except subprocess.CalledProcessError as e:
            print(f"Error during conversion: {e.stderr}")
            raise
    except Exception as e:
            print(f"Unexpected error: {str(e)}")
            raise