# backend_storage/VideoChunkManager.py
import os

class VideoChunkManager:
    def __init__(self, base_path='/data'):
        self.base_path = base_path
        self.streams_path = os.path.join(base_path, 'streams')
        self.metadata_path = os.path.join(base_path, 'metadata')
        
    def generate_chunk_filename(self, stream_id, quality, chunk_number):
        """
        Generate a consistent chunk filename
        
        :param stream_id: Unique stream identifier
        :param quality: Video quality (1080p, 720p, etc.)
        :param chunk_number: Chunk sequence number
        :return: Filename for the chunk
        """
        return f'chunk_{chunk_number:03d}.ts'
    
    def save_video_chunk(self, stream_id, quality, chunk_data, chunk_number):
        """
        Save a video chunk to the appropriate directory
        
        :param stream_id: Unique stream identifier
        :param quality: Video quality
        :param chunk_data: Actual video chunk data
        :param chunk_number: Chunk sequence number
        """
        # Ensure the directories for the stream exist
        os.makedirs(os.path.join(self.streams_path, f'stream_{stream_id}', quality), exist_ok=True)
        
        # Generate chunk filename
        filename = self.generate_chunk_filename(stream_id, quality, chunk_number)
        
        # Path for the chunk
        chunk_path = os.path.join(self.streams_path, f'stream_{stream_id}', quality, filename)
        
        # Save chunk to disk
        with open(chunk_path, 'wb') as f:
            f.write(chunk_data)
        
        # Update the m3u8 playlist for this chunk
        self.update_m3u8_playlist(stream_id, quality, filename)
    
    def update_m3u8_playlist(self, stream_id, quality, chunk_filename):
        """
        Update the m3u8 playlist for a specific stream and quality
        
        :param stream_id: Unique stream identifier
        :param quality: Video quality
        :param chunk_filename: Filename of the new chunk
        """
        playlist_path = os.path.join(self.metadata_path, f'stream_{stream_id}', f'{quality}.m3u8')
        
        # Append chunk information to the playlist
        with open(playlist_path, 'a') as f:
            f.write(f"#EXTINF:10.0,\n{quality}/{chunk_filename}\n")
