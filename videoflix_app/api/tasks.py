from celery import shared_task
import os
import subprocess
import json
import logging
from videoflix_app.models import Movie
from django.conf import settings

logger = logging.getLogger(__name__)

@shared_task
def process_video(movie_id):
    """Process movie into multiple resolutions and create HLS manifest"""
    try:
        movie = Movie.objects.get(id=movie_id)
        source_path = movie.video_file.path
        setup_info = prepare_video_processing(movie_id, source_path)
        available_resolutions = convert_to_resolutions(setup_info)
        finalize_processing(movie, setup_info, available_resolutions)
        return f"Successfully processed movie {movie_id} into {len(available_resolutions)} resolutions"
    except Exception as e:
        logger.error(f"Error processing video {movie_id}: {e}", exc_info=True)
        raise

def prepare_video_processing(movie_id, source_path):
    """Prepare directories and variables for video processing"""
    filename = os.path.basename(source_path)
    name, _ = os.path.splitext(filename)
    
    # Create output directory for this movie
    output_dir = os.path.join(settings.MEDIA_ROOT, 'videos', str(movie_id))
    os.makedirs(output_dir, exist_ok=True)
    
    return {
        'movie_id': movie_id,
        'source_path': source_path,
        'output_dir': output_dir,
        'name': name,
        'resolutions': [
            {"name": "120p", "resolution": "160x120", "bitrate": "100k"},
            {"name": "360p", "resolution": "640x360", "bitrate": "500k"},
            {"name": "720p", "resolution": "1280x720", "bitrate": "1500k"},
            {"name": "1080p", "resolution": "1920x1080", "bitrate": "3000k"}
        ]
    }

def get_video_dimensions(source_path):
    """Get the dimensions of the source video"""
    cmd = [
        'ffprobe', 
        '-v', 'error', 
        '-select_streams', 'v:0', 
        '-show_entries', 'stream=width,height', 
        '-of', 'json', 
        source_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        info = json.loads(result.stdout)
        
        if 'streams' in info and info['streams']:
            return {
                'width': info['streams'][0]['width'],
                'height': info['streams'][0]['height']
            }
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get video dimensions: {e.stderr}")
    except json.JSONDecodeError:
        logger.error("Failed to parse ffprobe output")
    
    return {'width': 0, 'height': 0}

def should_skip_resolution(source_dims, target_resolution):
    """
    Check if we should skip generating this resolution
    Returns True if source is SMALLER than target (should skip)
    """
    target_width, target_height = map(int, target_resolution.split('x'))
    # Nur überspringen, wenn Zielauflösung GRÖSSER als Original ist
    is_target_larger = source_dims['width'] < target_width or source_dims['height'] < target_height
    print(f"Source: {source_dims}, Target: {target_width}x{target_height}, Skip: {is_target_larger}")
    return is_target_larger

def convert_video(source_path, output_file, resolution, bitrate):
    """Convert video to specific resolution"""
    cmd = [
        'ffmpeg',
        '-i', source_path,
        '-vf', f'scale={resolution}',
        '-b:v', bitrate,
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
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error converting video: {e.stderr}")
        return False

def convert_to_resolutions(setup_info):
    """Convert video to multiple resolutions"""
    available_resolutions = []
    source_dims = get_video_dimensions(setup_info['source_path'])
    
    for res in setup_info['resolutions']:
        if should_skip_resolution(source_dims, res["resolution"]):
            logger.info(f"Skipping resolution {res['name']} - source too small")
            continue
        
        output_file = os.path.join(
            setup_info['output_dir'], 
            f"{setup_info['name']}_{res['name']}.mp4"
        )
        
        if convert_video(setup_info['source_path'], output_file, res['resolution'], res['bitrate']):
            available_resolutions.append(res["name"])
    
    return available_resolutions

def create_hls_manifest(setup_info, available_resolutions):
    """Create HLS manifest and segment files"""
    master_path = os.path.join(setup_info['output_dir'], f"{setup_info['name']}_master.m3u8")
    
    with open(master_path, 'w') as f:
        f.write("#EXTM3U\n")
        f.write("#EXT-X-VERSION:3\n")
        
        res_map = {
            "120p": {"resolution": "160x120", "bandwidth": "128000"},
            "360p": {"resolution": "640x360", "bandwidth": "600000"},
            "720p": {"resolution": "1280x720", "bandwidth": "2000000"},
            "1080p": {"resolution": "1920x1080", "bandwidth": "4000000"}
        }
        
        for res in available_resolutions:
            create_hls_segments(setup_info, res)
            
            # Add this resolution to the master playlist
            f.write(f"#EXT-X-STREAM-INF:BANDWIDTH={res_map[res]['bandwidth']},RESOLUTION={res_map[res]['resolution']}\n")
            f.write(f"{res}/playlist.m3u8\n")
    
    return master_path

def create_hls_segments(setup_info, resolution):
    """Create HLS segments for a specific resolution"""
    res_dir = os.path.join(setup_info['output_dir'], resolution)
    os.makedirs(res_dir, exist_ok=True)
    
    input_file = os.path.join(
        setup_info['output_dir'], 
        f"{setup_info['name']}_{resolution}.mp4"
    )
    
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
    
    try:
        subprocess.run(segment_cmd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error creating HLS segments: {e.stderr}")
        return False

def finalize_processing(movie, setup_info, available_resolutions):
    """Update movie model with processing results"""
    manifest_path = create_hls_manifest(setup_info, available_resolutions)
    relative_path = os.path.relpath(manifest_path, settings.MEDIA_ROOT)
    
    # Update movie with available resolutions and manifest
    movie.available_resolutions = available_resolutions
    movie.hls_manifest = relative_path
    movie.is_processed = True
    movie.save()