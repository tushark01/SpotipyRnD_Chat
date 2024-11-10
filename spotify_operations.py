import streamlit as st
from authentication import get_spotify_client
import pandas as pd
from datetime import datetime

class SpotifyOperations:
    def __init__(self):
        self.spotify = get_spotify_client()
        
    def search_spotify(self, query, search_type='track', limit=5):
        """Search Spotify for tracks, artists, or albums"""
        try:
            results = self.spotify.search(q=query, type=search_type, limit=limit)
            return results
        except Exception as e:
            st.error(f"Error searching Spotify: {str(e)}")
            return None

    def get_track_features(self, track_id):
        """Get audio features for a track"""
        try:
            features = self.spotify.audio_features([track_id])[0]
            return {
                'danceability': features['danceability'],
                'energy': features['energy'],
                'tempo': features['tempo'],
                'valence': features['valence'],
                'instrumentalness': features['instrumentalness']
            }
        except:
            return None

    def get_artist_top_tracks(self, artist_id, country='US'):
        """Get top tracks for an artist"""
        try:
            results = self.spotify.artist_top_tracks(artist_id, country)
            return results['tracks']
        except:
            return None

    def create_playlist(self, name, description="", public=True):
        """Create a new playlist"""
        try:
            user_id = self.spotify.current_user()['id']
            playlist = self.spotify.user_playlist_create(user_id, name, public=public, description=description)
            return playlist['id']
        except Exception as e:
            st.error(f"Error creating playlist: {str(e)}")
            return None

    def add_tracks_to_playlist(self, playlist_id, track_uris):
        """Add tracks to a playlist"""
        try:
            self.spotify.playlist_add_items(playlist_id, track_uris)
            return True
        except:
            return False

    def get_similar_tracks(self, track_id, limit=5):
        """Get recommendations based on a track"""
        try:
            recommendations = self.spotify.recommendations(seed_tracks=[track_id], limit=limit)
            return recommendations['tracks']
        except:
            return None

    def process_spotify_results(self, results, search_type='track'):
        """Process and format Spotify search results"""
        if not results:
            return "No results found."
        
        formatted_results = []
        
        if search_type == 'track':
            tracks = results['tracks']['items']
            for track in tracks:
                # Get audio features for each track
                features = self.get_track_features(track['id'])
                
                formatted_results.append({
                    'id': track['id'],
                    'name': track['name'],
                    'artist': track['artists'][0]['name'],
                    'artist_id': track['artists'][0]['id'],
                    'album': track['album']['name'],
                    'release_date': track['album']['release_date'],
                    'preview_url': track['preview_url'],
                    'spotify_url': track['external_urls']['spotify'],
                    'popularity': track['popularity'],
                    'duration_ms': track['duration_ms'],
                    'features': features
                })
        
        elif search_type == 'artist':
            artists = results['artists']['items']
            for artist in artists:
                # Get top tracks for each artist
                top_tracks = self.get_artist_top_tracks(artist['id'])
                top_track_names = [track['name'] for track in top_tracks[:3]] if top_tracks else []
                
                formatted_results.append({
                    'id': artist['id'],
                    'name': artist['name'],
                    'genres': artist.get('genres', []),
                    'popularity': artist['popularity'],
                    'spotify_url': artist['external_urls']['spotify'],
                    'followers': artist['followers']['total'],
                    'top_tracks': top_track_names
                })
        
        return formatted_results

    def display_track_results(self, results):
        """Display track results with enhanced information"""
        for track in results:
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.markdown(f"### {track['name']}")
                    st.write(f"🎤 Artist: {track['artist']}")
                    st.write(f"💿 Album: {track['album']}")
                    release_date = datetime.strptime(track['release_date'], '%Y-%m-%d').strftime('%B %d, %Y')
                    st.write(f"📅 Release Date: {release_date}")
                    st.write(f"⭐ Popularity: {track['popularity']}/100")
                    
                with col2:
                    if track['features']:
                        st.write("📊 Track Features:")
                        features_df = pd.DataFrame({
                            'Feature': track['features'].keys(),
                            'Value': [f"{v*100:.0f}%" if k != 'tempo' else f"{v:.0f} BPM" 
                                    for k, v in track['features'].items()]
                        })
                        st.dataframe(features_df, hide_index=True)
                
                with col3:
                    if track['preview_url']:
                        st.write("🎵 Preview:")
                        st.audio(track['preview_url'])
                    st.markdown(f"[Open in Spotify]({track['spotify_url']})")
                    
                    # Add button to get similar songs
                    if st.button(f"Find Similar Songs", key=f"similar_{track['id']}"):
                        similar_tracks = self.get_similar_tracks(track['id'])
                        if similar_tracks:
                            st.write("Similar Songs:")
                            for similar in similar_tracks:
                                st.write(f"- [{similar['name']} by {similar['artists'][0]['name']}]({similar['external_urls']['spotify']})")

                st.divider()

    def display_artist_results(self, results):
        """Display artist results with enhanced information"""
        for artist in results:
            with st.container():
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"### {artist['name']}")
                    st.write(f"👥 Followers: {artist['followers']:,}")
                    st.write(f"⭐ Popularity: {artist['popularity']}/100")
                    if artist['genres']:
                        st.write("🎵 Genres: " + ", ".join(artist['genres']))
                    
                with col2:
                    st.write("🎶 Top Tracks:")
                    for track in artist['top_tracks']:
                        st.write(f"- {track}")
                    st.markdown(f"[Open in Spotify]({artist['spotify_url']})")
                
                st.divider()

    def create_recommendation_playlist(self, tracks, playlist_name):
        """Create a playlist from recommended tracks"""
        playlist_id = self.create_playlist(playlist_name, "Generated by Music Assistant")
        if playlist_id:
            track_uris = [track['uri'] for track in tracks]
            if self.add_tracks_to_playlist(playlist_id, track_uris):
                return f"Playlist created successfully! Open it in Spotify: https://open.spotify.com/playlist/{playlist_id}"
        return "Failed to create playlist"
    

    