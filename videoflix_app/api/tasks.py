import subprocess
import os
from celery import shared_task
import json
from videoflix_app.models import Movie
from django.conf import settings

@shared_task
def process_video(movie_id):
    """Process movie into multiple resolutions and create HLS manifest"""
    try:
        movie = Movie.objects.get(id=movie_id)
        source_path = movie.video_file.path
        filename = os.path.basename(source_path)
        name, _ = os.path.splitext(filename)
        
        output_dir = os.path.join(settings.MEDIA_ROOT, 'videos', str(movie_id))
        os.makedirs(output_dir, exist_ok=True)
        
        resolutions = [
            {"name": "120p", "resolution": "160x120", "bitrate": "100k"},
            {"name": "360p", "resolution": "640x360", "bitrate": "500k"},
            {"name": "720p", "resolution": "1280x720", "bitrate": "1500k"},
            {"name": "1080p", "resolution": "1920x1080", "bitrate": "3000k"}
        ]
        
        available_resolutions = []
        
        for res in resolutions:
            if should_skip_resolution(source_path, res["resolution"]):
                continue
            
        output_file = os.path.join(output_dir, f"{name}_{res['name']}.mp4")
        
        cmd = [
                'ffmpeg',
                '-i', source_path,
                '-vf', f'scale={res["resolution"]}',
                '-b:v', res['bitrate'],
                '-c:v', 'libx264',
                '-crf', '23',
                '-preset', 'medium',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-movflags', '+faststart',
                output_file
            ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            available_resolutions.append(res["name"])
        except subprocess.CalledProcessError as e:
            print(f"Error converting to {res['name']}: {e}")
            print(f"Output: {e.stdout}")
            print(f"Error: {e.stderr}")
        
        manifest_path = create_hls_manifest(movie_id, output_dir, name, available_resolutions)
        relative_path = os.path.relpath(manifest_path, settings.MEDIA_ROOT)
        
        # Update movie with available resolutions and manifest
        movie.available_resolutions = available_resolutions
        movie.hls_manifest = relative_path
        movie.is_processed = True
        movie.save()
        
        return f"Successfully processed movie {movie_id} into {len(available_resolutions)} resolutions"
        
    except Exception as e:
        print(f"Error processing video {movie_id}: {e}")
        raise

def should_skip_resolution(source_path, target_resolution):
    """Check if we should skip generating this resolution based on source dimensions"""
    # Get video dimensions
    cmd = [
        'ffprobe', 
        '-v', 'error', 
        '-select_streams', 'v:0', 
        '-show_entries', 'stream=width,height', 
        '-of', 'json', 
        source_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    info = json.loads(result.stdout)
    
    if 'streams' in info and info['streams']:
        width = info['streams'][0]['width']
        height = info['streams'][0]['height']
        
        # Parse target resolution
        target_width, target_height = map(int, target_resolution.split('x'))
        
        # Skip if original is smaller than target
        if width < target_width or height < target_height:
            return True
    
    return False

def create_hls_manifest(movie_id, output_dir, name, available_resolutions):
    """Create HLS manifest and segment files for adaptive streaming"""
    # Create master playlist
    master_path = os.path.join(output_dir, f"{name}_master.m3u8")
    
    with open(master_path, 'w') as f:
        f.write("#EXTM3U\n")
        f.write("#EXT-X-VERSION:3\n")
        
        # Resolution mappings
        res_map = {
            "120p": {"resolution": "160x120", "bandwidth": "128000"},
            "360p": {"resolution": "640x360", "bandwidth": "600000"},
            "720p": {"resolution": "1280x720", "bandwidth": "2000000"},
            "1080p": {"resolution": "1920x1080", "bandwidth": "4000000"}
        }
        
        # Process each available resolution
        for res in available_resolutions:
            res_dir = os.path.join(output_dir, res)
            os.makedirs(res_dir, exist_ok=True)
            
            # Input file path
            input_file = os.path.join(output_dir, f"{name}_{res}.mp4")
            
            # Create segments for this resolution
            segment_cmd = [
                'ffmpeg',
                '-i', input_file,
                '-c:v', 'copy',
                '-c:a', 'copy',
                '-f', 'hls',
                '-hls_time', '10',
                '-hls_playlist_type', 'vod',
                '-hls_segment_filename', 
                os.path.join(res_dir, f"segment_%03d.ts"),
                os.path.join(res_dir, f"playlist.m3u8")
            ]
            
            subprocess.run(segment_cmd, check=True, capture_output=True, text=True)
            
            # Add this resolution to the master playlist
            f.write(f"#EXT-X-STREAM-INF:BANDWIDTH={res_map[res]['bandwidth']},RESOLUTION={res_map[res]['resolution']}\n")
            f.write(f"{res}/playlist.m3u8\n")
    
    return master_path