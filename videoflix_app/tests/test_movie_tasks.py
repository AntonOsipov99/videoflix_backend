import pytest
from unittest.mock import patch, MagicMock
from videoflix_app.api.tasks import (
    process_video, prepare_video_processing,
    convert_to_resolutions, finalize_processing
)

@pytest.mark.django_db
def test_prepare_video_processing(sample_movie, settings):
    setup_info = prepare_video_processing(
        sample_movie.id, 
        sample_movie.video_file.path
    )
    
    assert setup_info['movie_id'] == sample_movie.id
    assert setup_info['source_path'] == sample_movie.video_file.path
    assert 'output_dir' in setup_info
    assert len(setup_info['resolutions']) == 4

@pytest.mark.django_db
@patch('videoflix_app.api.tasks.convert_to_resolutions')
@patch('videoflix_app.api.tasks.finalize_processing')
def test_process_video(mock_finalize, mock_convert, sample_movie):
    mock_convert.return_value = ['360p', '720p']
    
    result = process_video(sample_movie.id)
    
    mock_convert.assert_called_once()
    mock_finalize.assert_called_once()
    assert "Successfully processed" in result
    
@pytest.mark.django_db
def test_convert_to_resolutions(sample_movie):
    setup_info = prepare_video_processing(
        sample_movie.id, 
        sample_movie.video_file.path
    )
    
    with patch('videoflix_app.api.tasks.get_video_dimensions') as mock_dimensions:
        mock_dimensions.return_value = {'width': 1920, 'height': 1080}
        
        with patch('videoflix_app.api.tasks.convert_video') as mock_convert:
            mock_convert.return_value = True
            
            resolutions = convert_to_resolutions(setup_info)
            
            assert isinstance(resolutions, list)
            assert len(resolutions) > 0
            assert mock_convert.call_count >= 1

@pytest.mark.django_db
def test_finalize_processing(sample_movie):
    setup_info = prepare_video_processing(
        sample_movie.id, 
        sample_movie.video_file.path
    )
    available_resolutions = ['360p', '720p']

    with patch('videoflix_app.api.tasks.create_hls_manifest') as mock_manifest:
        mock_manifest.return_value = '/media/videos/1/test_master.m3u8'

        finalize_processing(sample_movie, setup_info, available_resolutions)
        
        sample_movie.refresh_from_db()
        assert sample_movie.is_processed is True
        assert sample_movie.available_resolutions == available_resolutions
        assert 'test_master.m3u8' in sample_movie.hls_manifest