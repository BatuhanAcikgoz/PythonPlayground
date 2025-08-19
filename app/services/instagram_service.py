import requests
import json
import time
import random
import re
from datetime import datetime
from typing import List, Dict, Optional
from app.utils.cache_helper import CacheManager


class InstagramService:
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15"
        ]

    def get_headers(self) -> Dict[str, str]:
        """Random user agent ile headers döndürür"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }

    def fetch_posts_from_instagram(self, username: str) -> List[Dict]:
        """Instagram'dan postları çeker"""
        posts = []

        try:
            # API yöntemi dene
            api_url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
            api_headers = self.get_headers()
            api_headers['X-IG-App-ID'] = '936619743392459'

            response = requests.get(api_url, headers=api_headers, timeout=15)

            if response.status_code == 200:
                data = response.json()
                user_data = data.get('data', {}).get('user', {})
                media_items = user_data.get('edge_owner_to_timeline_media', {}).get('edges', [])

                for i, edge in enumerate(media_items):
                    node = edge.get('node', {})
                    if node:
                        post_id = node.get('id', i)
                        image_url = node.get('display_url', '')
                        caption_edges = node.get('edge_media_to_caption', {}).get('edges', [])
                        caption = caption_edges[0].get('node', {}).get('text', '') if caption_edges else ''
                        likes = node.get('edge_liked_by', {}).get('count', 0) or node.get('edge_media_preview_like',
                                                                                          {}).get('count', 0)
                        timestamp = node.get('taken_at_timestamp', 0)
                        post_date = datetime.fromtimestamp(timestamp).strftime(
                            '%Y-%m-%d') if timestamp else 'Bilinmiyor'
                        shortcode = node.get('shortcode', '')
                        post_url = f'https://www.instagram.com/p/{shortcode}/'

                        posts.append({
                            'id': post_id,
                            'image_url': image_url,
                            'caption': caption,
                            'likes': likes,
                            'post_date': post_date,
                            'post_url': post_url
                        })

            print(f"Instagram'dan {len(posts)} post çekildi: {username}")

        except Exception as e:
            print(f"Instagram API hatası ({username}): {str(e)}")

        return posts

    def get_cached_posts(self, username: str, db) -> Optional[List[Dict]]:
        """Cache'den postları çeker"""
        cache_key = CacheManager.get_cache_key("instagram_posts", username)
        cached_data = CacheManager.get_cached_data(cache_key, db)

        if cached_data:
            print(f"Instagram postları cache'den alındı: {username}")
            return cached_data.get('posts', [])

        return None

    def cache_posts(self, username: str, posts: List[Dict], db, expires_in_hours: int = 1):
        """Postları cache'e kaydeder"""
        cache_key = CacheManager.get_cache_key("instagram_posts", username)
        cache_data = {
            'posts': posts,
            'username': username,
            'updated_at': datetime.utcnow().isoformat()
        }

        CacheManager.set_cache_data(cache_key, cache_data, expires_in_hours, db)
        print(f"Instagram postları cache'e kaydedildi: {username}")

    def get_posts(self, username: str, db, force_refresh: bool = False) -> List[Dict]:
        """Postları cache'den veya Instagram'dan çeker"""
        # Force refresh değilse önce cache'e bak
        if not force_refresh:
            cached_posts = self.get_cached_posts(username, db)
            if cached_posts is not None:
                return cached_posts

        # Cache'de yoksa veya force refresh ise Instagram'dan çek
        fresh_posts = self.fetch_posts_from_instagram(username)

        # Yeni veriyi cache'e kaydet (1 saat)
        if fresh_posts:
            self.cache_posts(username, fresh_posts, db, expires_in_hours=1)

        return fresh_posts