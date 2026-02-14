import pytest
from unittest.mock import patch, MagicMock, call
from spotify_player import SpotifyPlayer, CallbackHandler


class TestSpotifyPlayerUserInput1:
    """Test suite for Spotify Player when user input is 1."""
    
    def setup_method(self):
        """Set auth_code before each test"""
        CallbackHandler.auth_code = 'test_auth_code'
    
    @patch('spotify_player.time.sleep')
    @patch('spotify_player.HTTPServer')
    @patch('spotify_player.threading.Thread')
    @patch('spotify_player.webbrowser.open')
    @patch('spotify_player.requests.get')
    @patch('spotify_player.requests.put')
    @patch('spotify_player.requests.post')
    @patch('builtins.input')
    def test_input_1_plays_lofi_beats(self, mock_input, mock_post, mock_put, mock_get, mock_browser, mock_thread, mock_server, mock_sleep):
        """Test that when user input is 1, it plays lofi beats focus music."""
        
        # Mock user inputs: first input is '1' for lofi beats, second for selecting track
        mock_input.side_effect = ['1', '1']
        
        # Mock HTTP server
        mock_server_instance = MagicMock()
        mock_server.return_value = mock_server_instance
        
        # Mock thread
        mock_thread.return_value = MagicMock()
        
        # Mock OAuth token exchange response
        token_response = MagicMock()
        token_response.json.return_value = {
            'access_token': 'test_oauth_token',
            'refresh_token': 'test_refresh_token'
        }
        token_response.raise_for_status.return_value = None
        
        # Mock devices response
        devices_response = MagicMock()
        devices_response.json.return_value = {
            'devices': [
                {'id': 'device_123', 'name': 'Test Device', 'type': 'Computer'}
            ]
        }
        devices_response.raise_for_status.return_value = None
        
        # Mock playlist search response
        playlist_response = MagicMock()
        playlist_response.json.return_value = {
            'playlists': {
                'items': [
                    {
                        'name': 'Lo-Fi Beats',
                        'uri': 'spotify:playlist:lo-fi-beats-123',
                        'owner': {'display_name': 'Spotify'},
                        'tracks': {'total': 50}
                    }
                ]
            }
        }
        playlist_response.raise_for_status.return_value = None
        
        # Response for playback
        playback_response = MagicMock()
        playback_response.status_code = 204
        
        # Set up mocks
        mock_post.return_value = token_response
        mock_get.side_effect = [devices_response, playlist_response]
        mock_put.return_value = playback_response
        
        # Create player and run
        player = SpotifyPlayer(client_id='test_id', client_secret='test_secret')
        result = player.play_adhd_focus_music()
        
        # Verify playback was started
        assert result is True
        mock_put.assert_called_once()
    
    @patch('spotify_player.time.sleep')
    @patch('spotify_player.HTTPServer')
    @patch('spotify_player.threading.Thread')
    @patch('spotify_player.webbrowser.open')
    @patch('spotify_player.requests.get')
    @patch('spotify_player.requests.put')
    @patch('spotify_player.requests.post')
    @patch('builtins.input')
    def test_input_1_searches_for_lofi_beats(self, mock_input, mock_post, mock_put, mock_get, mock_browser, mock_thread, mock_server, mock_sleep):
        """Test that input 1 searches for 'lofi beats focus' query."""
        
        mock_input.side_effect = ['1', '1']
        
        # Mock HTTP server
        mock_server_instance = MagicMock()
        mock_server.return_value = mock_server_instance
        mock_thread.return_value = MagicMock()
        
        # Mock token response
        token_response = MagicMock()
        token_response.json.return_value = {
            'access_token': 'test_token',
            'refresh_token': 'test_refresh'
        }
        token_response.raise_for_status.return_value = None
        
        # Mock devices
        devices_response = MagicMock()
        devices_response.json.return_value = {
            'devices': [{'id': 'dev_1', 'name': 'My Device'}]
        }
        devices_response.raise_for_status.return_value = None
        
        # Mock playlist search
        playlist_response = MagicMock()
        playlist_response.json.return_value = {
            'playlists': {
                'items': [
                    {
                        'name': 'Lo-Fi Relaxing Beats',
                        'uri': 'spotify:playlist:test_uri',
                        'owner': {'display_name': 'Test Owner'},
                        'tracks': {'total': 45}
                    }
                ]
            }
        }
        playlist_response.raise_for_status.return_value = None
        
        # Mock playback
        playback_response = MagicMock()
        playback_response.status_code = 204
        
        mock_post.return_value = token_response
        mock_get.side_effect = [devices_response, playlist_response]
        mock_put.return_value = playback_response
        
        player = SpotifyPlayer(client_id='test_id', client_secret='test_secret')
        player.play_adhd_focus_music()
        
        # Verify that search was called with lofi beats focus query
        search_calls = [c for c in mock_get.call_args_list if 'search' in str(c)]
        assert len(search_calls) >= 1
        assert 'lofi beats focus' in str(search_calls[0])
    
    @patch('spotify_player.time.sleep')
    @patch('spotify_player.HTTPServer')
    @patch('spotify_player.threading.Thread')
    @patch('spotify_player.webbrowser.open')
    @patch('spotify_player.requests.get')
    @patch('spotify_player.requests.put')
    @patch('spotify_player.requests.post')
    @patch('builtins.input')
    def test_input_1_starts_playback(self, mock_input, mock_post, mock_put, mock_get, mock_browser, mock_thread, mock_server, mock_sleep):
        """Test that input 1 triggers playback to start."""
        
        mock_input.side_effect = ['1', '1']
        
        # Mock HTTP server
        mock_server_instance = MagicMock()
        mock_server.return_value = mock_server_instance
        mock_thread.return_value = MagicMock()
        
        # Mock responses
        token_response = MagicMock()
        token_response.json.return_value = {
            'access_token': 'test_token',
            'refresh_token': 'refresh'
        }
        token_response.raise_for_status.return_value = None
        
        devices_response = MagicMock()
        devices_response.json.return_value = {
            'devices': [{'id': 'device_1', 'name': 'Speaker'}]
        }
        devices_response.raise_for_status.return_value = None
        
        playlist_response = MagicMock()
        playlist_response.json.return_value = {
            'playlists': {
                'items': [
                    {
                        'name': 'Lofi Study Beats',
                        'uri': 'spotify:playlist:study123',
                        'owner': {'display_name': 'Music Curator'},
                        'tracks': {'total': 60}
                    }
                ]
            }
        }
        playlist_response.raise_for_status.return_value = None
        
        playback_response = MagicMock()
        playback_response.status_code = 204
        
        mock_post.return_value = token_response
        mock_get.side_effect = [devices_response, playlist_response]
        mock_put.return_value = playback_response
        
        player = SpotifyPlayer(client_id='test_id', client_secret='test_secret')
        result = player.play_adhd_focus_music()
        
        # Verify that start_playback (PUT request) was called
        assert mock_put.called
        assert result is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
