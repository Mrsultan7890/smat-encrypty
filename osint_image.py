#!/usr/bin/env python3
"""
Smart-Encrypt OSINT Image Analyzer
Minimal implementation for cybersecurity research
"""

import os
import sqlite3
import hashlib
import requests
from PIL import Image, ExifTags
import imagehash
from urllib.parse import urljoin, urlparse
import threading
import time
from datetime import datetime
import json
import re
from bs4 import BeautifulSoup
import base64

class OSINTImageAnalyzer:
    def __init__(self, db_path="~/.smart_encrypt/osint.db"):
        self.db_path = os.path.expanduser(db_path)
        self.results_dir = os.path.expanduser("~/.smart_encrypt/osint_results")
        os.makedirs(self.results_dir, exist_ok=True)
        self.init_db()
        
        # Real platform URLs for scraping
        self.platforms = {
            'instagram': {
                'search_url': 'https://www.instagram.com/{username}/',
                'image_selectors': ['img[src*="scontent"]', 'img[alt*="Photo"]'],
                'headers': {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'}
            },
            'facebook': {
                'search_url': 'https://www.facebook.com/{username}',
                'image_selectors': ['img[src*="fbcdn"]', 'img[data-src]'],
                'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            },
            'twitter': {
                'search_url': 'https://twitter.com/{username}',
                'image_selectors': ['img[src*="pbs.twimg.com"]', 'img[alt*="Image"]'],
                'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            },
            'linkedin': {
                'search_url': 'https://www.linkedin.com/in/{username}',
                'image_selectors': ['img[src*="licdn.com"]'],
                'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            },
            'github': {
                'search_url': 'https://github.com/{username}',
                'image_selectors': ['img.avatar', 'img[src*="avatars.githubusercontent.com"]'],
                'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            },
            'reddit': {
                'search_url': 'https://www.reddit.com/user/{username}',
                'image_selectors': ['img[src*="redd.it"]', 'img[src*="reddit.com"]'],
                'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            },
            'tiktok': {
                'search_url': 'https://www.tiktok.com/@{username}',
                'image_selectors': ['img[src*="tiktokcdn.com"]'],
                'headers': {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'}
            },
            'pinterest': {
                'search_url': 'https://www.pinterest.com/{username}/',
                'image_selectors': ['img[src*="pinimg.com"]'],
                'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            },
            'snapchat': {
                'search_url': 'https://www.snapchat.com/add/{username}',
                'image_selectors': ['img[src*="snapchat.com"]'],
                'headers': {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'}
            },
            'youtube': {
                'search_url': 'https://www.youtube.com/@{username}',
                'image_selectors': ['img[src*="yt3.ggpht.com"]', 'img[src*="ytimg.com"]'],
                'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            },
            'telegram': {
                'search_url': 'https://t.me/{username}',
                'image_selectors': ['img[src*="telegram.org"]'],
                'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            },
            'discord': {
                'search_url': 'https://discord.com/users/{username}',
                'image_selectors': ['img[src*="cdn.discordapp.com"]'],
                'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            },
            'onlyfans': {
                'search_url': 'https://onlyfans.com/{username}',
                'image_selectors': ['img[src*="onlyfans.com"]', 'img[data-src*="onlyfans"]'],
                'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            },
            'pornhub': {
                'search_url': 'https://www.pornhub.com/users/{username}',
                'image_selectors': ['img[src*="phncdn.com"]', 'img[data-src*="phncdn"]'],
                'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            },
            'xvideos': {
                'search_url': 'https://www.xvideos.com/profiles/{username}',
                'image_selectors': ['img[src*="xvideos-cdn.com"]', 'img[data-src*="xvideos"]'],
                'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            },
            'xhamster': {
                'search_url': 'https://xhamster.com/users/{username}',
                'image_selectors': ['img[src*="xhcdn.com"]'],
                'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            },
            'redtube': {
                'search_url': 'https://www.redtube.com/users/{username}',
                'image_selectors': ['img[src*="redtube.com"]'],
                'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            },
            'chaturbate': {
                'search_url': 'https://chaturbate.com/{username}/',
                'image_selectors': ['img[src*="chaturbate.com"]'],
                'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            },
            'cam4': {
                'search_url': 'https://www.cam4.com/{username}',
                'image_selectors': ['img[src*="cam4.com"]'],
                'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            },
            'myfreecams': {
                'search_url': 'https://profiles.myfreecams.com/{username}',
                'image_selectors': ['img[src*="myfreecams.com"]'],
                'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            },
            'tinder': {
                'search_url': 'https://tinder.com/@{username}',
                'image_selectors': ['img[src*="tinder.com"]'],
                'headers': {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'}
            },
            'bumble': {
                'search_url': 'https://bumble.com/app/{username}',
                'image_selectors': ['img[src*="bumble.com"]'],
                'headers': {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'}
            },
            'badoo': {
                'search_url': 'https://badoo.com/profile/{username}',
                'image_selectors': ['img[src*="badoo.com"]'],
                'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            },
            'match': {
                'search_url': 'https://www.match.com/search?username={username}',
                'image_selectors': ['img[src*="match.com"]'],
                'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            },
            'pof': {
                'search_url': 'https://www.pof.com/viewprofile.aspx?profile_id={username}',
                'image_selectors': ['img[src*="pof.com"]'],
                'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            },
            'okcupid': {
                'search_url': 'https://www.okcupid.com/profile/{username}',
                'image_selectors': ['img[src*="okcupid.com"]'],
                'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            },
            'doodstream': {
                'search_url': 'https://doodstream.com/profile/{username}',
                'image_selectors': ['img[src*="doodstream.com"]', 'img[data-src*="dood"]'],
                'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            },
            'streamtape': {
                'search_url': 'https://streamtape.com/user/{username}',
                'image_selectors': ['img[src*="streamtape.com"]'],
                'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            },
            'mixdrop': {
                'search_url': 'https://mixdrop.co/user/{username}',
                'image_selectors': ['img[src*="mixdrop.co"]'],
                'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            },
            'uploadgig': {
                'search_url': 'https://uploadgig.com/user/{username}',
                'image_selectors': ['img[src*="uploadgig.com"]'],
                'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            },
            'rapidgator': {
                'search_url': 'https://rapidgator.net/user/{username}',
                'image_selectors': ['img[src*="rapidgator.net"]'],
                'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            },
            'mega': {
                'search_url': 'https://mega.nz/user/{username}',
                'image_selectors': ['img[src*="mega.nz"]'],
                'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            },
            'mediafire': {
                'search_url': 'https://www.mediafire.com/myfiles.php?user={username}',
                'image_selectors': ['img[src*="mediafire.com"]'],
                'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            },
            'anonfiles': {
                'search_url': 'https://anonfiles.com/user/{username}',
                'image_selectors': ['img[src*="anonfiles.com"]'],
                'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            },
            'gofile': {
                'search_url': 'https://gofile.io/user/{username}',
                'image_selectors': ['img[src*="gofile.io"]'],
                'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            }
        }
        
    def init_db(self):
        """Initialize OSINT database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS image_targets (
                id INTEGER PRIMARY KEY,
                case_id TEXT,
                image_path TEXT,
                image_hash TEXT,
                perceptual_hash TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS image_matches (
                id INTEGER PRIMARY KEY,
                case_id TEXT,
                target_id INTEGER,
                source_url TEXT,
                local_path TEXT,
                confidence REAL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (target_id) REFERENCES image_targets (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def add_target_image(self, image_path, case_id):
        """Add target image for analysis"""
        try:
            # Calculate hashes
            with Image.open(image_path) as img:
                # Perceptual hash for similarity
                phash = str(imagehash.phash(img))
                
                # File hash
                with open(image_path, 'rb') as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO image_targets (case_id, image_path, image_hash, perceptual_hash)
                VALUES (?, ?, ?, ?)
            ''', (case_id, image_path, file_hash, phash))
            
            target_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return target_id
            
        except Exception as e:
            print(f"Error adding target image: {e}")
            return None
    
    def extract_metadata(self, image_path):
        """Extract EXIF metadata from image"""
        try:
            with Image.open(image_path) as img:
                exif_data = {}
                if hasattr(img, '_getexif') and img._getexif():
                    exif = img._getexif()
                    for tag_id, value in exif.items():
                        tag = ExifTags.TAGS.get(tag_id, tag_id)
                        exif_data[tag] = str(value)
                return exif_data
        except:
            return {}
    
    def download_image(self, url, save_path):
        """Download image from URL with retry mechanism"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        for attempt in range(3):  # 3 retry attempts
            try:
                response = requests.get(url, headers=headers, timeout=15, stream=True, verify=False)
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    if 'image' in content_type:
                        with open(save_path, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                        
                        # Verify file was downloaded and is valid
                        if os.path.exists(save_path) and os.path.getsize(save_path) > 1024:
                            return True
                        
            except Exception as e:
                if attempt == 2:  # Last attempt
                    print(f"Failed to download {url}: {e}")
                time.sleep(1)  # Wait before retry
                
        return False
    
    def compare_images(self, img1_path, img2_path):
        """Compare two images using perceptual hashing"""
        try:
            with Image.open(img1_path) as img1, Image.open(img2_path) as img2:
                hash1 = imagehash.phash(img1)
                hash2 = imagehash.phash(img2)
                
                # Calculate similarity (0-1, higher = more similar)
                diff = hash1 - hash2
                similarity = max(0, 1 - (diff / 64.0))
                return similarity
        except:
            return 0.0
    
    def search_by_username(self, username, platforms, case_id, target_id, callback=None):
        """Search for username across multiple platforms"""
        matches_found = 0
        
        for platform_name in platforms:
            if platform_name not in self.platforms:
                continue
                
            platform = self.platforms[platform_name]
            url = platform['search_url'].format(username=username)
            
            if callback:
                callback(f"Searching {platform_name} for {username}...")
            
            matches = self.crawl_platform(url, platform, case_id, target_id, callback)
            matches_found += matches
            
            time.sleep(2)  # Rate limiting
        
        return matches_found
    
    def crawl_platform(self, url, platform_config, case_id, target_id, callback=None):
        """Crawl a specific platform"""
        try:
            response = requests.get(url, headers=platform_config['headers'], timeout=15)
            
            if response.status_code != 200:
                return 0
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find images using platform-specific selectors
            img_tags = []
            for selector in platform_config['image_selectors']:
                img_tags.extend(soup.select(selector))
            
            case_dir = os.path.join(self.results_dir, case_id)
            os.makedirs(case_dir, exist_ok=True)
            
            # Get target image for comparison
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT image_path FROM image_targets WHERE id = ?', (target_id,))
            target_path = cursor.fetchone()[0]
            conn.close()
            
            matches_found = 0
            
            for i, img_tag in enumerate(img_tags[:25]):  # Increased limit
                try:
                    img_url = img_tag.get('src') or img_tag.get('data-src')
                    if not img_url:
                        continue
                    
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif img_url.startswith('/'):
                        img_url = urljoin(url, img_url)
                    
                    # Skip data URLs and icons
                    if img_url.startswith('data:') or 'icon' in img_url.lower():
                        continue
                    
                    # Download image
                    filename = f"{urlparse(url).netloc}_{i}_{int(time.time())}.jpg"
                    local_path = os.path.join(case_dir, filename)
                    
                    if self.download_image(img_url, local_path):
                        # Compare with target
                        similarity = self.compare_images(target_path, local_path)
                        
                        if similarity > 0.5:  # 50% similarity threshold
                            # Extract metadata
                            metadata = self.extract_metadata(local_path)
                            metadata['source_platform'] = urlparse(url).netloc
                            metadata['image_size'] = os.path.getsize(local_path)
                            metadata['download_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                            
                            # Save match to database
                            conn = sqlite3.connect(self.db_path)
                            cursor = conn.cursor()
                            cursor.execute('''
                                INSERT INTO image_matches 
                                (case_id, target_id, source_url, local_path, confidence, metadata)
                                VALUES (?, ?, ?, ?, ?, ?)
                            ''', (case_id, target_id, img_url, local_path, similarity, json.dumps(metadata)))
                            conn.commit()
                            conn.close()
                            
                            matches_found += 1
                            
                            if callback:
                                callback(f"✓ Match: {similarity:.1%} similarity - {urlparse(url).netloc} - {os.path.getsize(local_path)} bytes")
                        else:
                            # Keep low-similarity images for manual review
                            if similarity > 0.3:
                                if callback:
                                    callback(f"⚠ Low match: {similarity:.1%} similarity - saved for review")
                            else:
                                os.remove(local_path)
                    
                except Exception as e:
                    continue
            
            return matches_found
            
        except Exception as e:
            if callback:
                callback(f"Error crawling {urlparse(url).netloc}: {str(e)}")
            return 0
    
    def crawl_site(self, url, case_id, target_id, callback=None):
        """Crawl a single site for images"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                return
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find image tags
            img_tags = soup.find_all('img', src=True)
            
            case_dir = os.path.join(self.results_dir, case_id)
            os.makedirs(case_dir, exist_ok=True)
            
            # Get target image for comparison
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT image_path FROM image_targets WHERE id = ?', (target_id,))
            target_path = cursor.fetchone()[0]
            conn.close()
            
            matches_found = 0
            
            for i, img_tag in enumerate(img_tags[:20]):  # Limit to 20 images per site
                try:
                    img_url = urljoin(url, img_tag['src'])
                    
                    # Skip data URLs and very small images
                    if img_url.startswith('data:') or 'icon' in img_url.lower():
                        continue
                    
                    # Download image
                    filename = f"img_{i}_{int(time.time())}.jpg"
                    local_path = os.path.join(case_dir, filename)
                    
                    if self.download_image(img_url, local_path):
                        # Compare with target
                        similarity = self.compare_images(target_path, local_path)
                        
                        if similarity > 0.7:  # 70% similarity threshold
                            # Extract metadata
                            metadata = self.extract_metadata(local_path)
                            
                            # Save match to database
                            conn = sqlite3.connect(self.db_path)
                            cursor = conn.cursor()
                            cursor.execute('''
                                INSERT INTO image_matches 
                                (case_id, target_id, source_url, local_path, confidence, metadata)
                                VALUES (?, ?, ?, ?, ?, ?)
                            ''', (case_id, target_id, img_url, local_path, similarity, str(metadata)))
                            conn.commit()
                            conn.close()
                            
                            matches_found += 1
                            
                            if callback:
                                callback(f"Match found: {similarity:.2%} similarity")
                        else:
                            # Remove non-matching image to save space
                            os.remove(local_path)
                    
                    if callback:
                        callback(f"Processed {i+1}/{len(img_tags)} images from {urlparse(url).netloc}")
                        
                except Exception as e:
                    continue
            
            if callback:
                callback(f"Found {matches_found} matches from {urlparse(url).netloc}")
                
        except Exception as e:
            if callback:
                callback(f"Error crawling {url}: {str(e)}")
    
    def start_username_scan(self, case_id, target_id, username, platforms, progress_callback=None):
        """Start username-based scan across platforms"""
        def scan_worker():
            if progress_callback:
                progress_callback(f"Starting OSINT scan for username: {username}")
            
            total_matches = self.search_by_username(username, platforms, case_id, target_id, progress_callback)
            
            if progress_callback:
                progress_callback(f"Scan completed! Found {total_matches} matches")
        
        thread = threading.Thread(target=scan_worker)
        thread.daemon = True
        thread.start()
        return thread
    
    def start_scan(self, case_id, target_id, urls, progress_callback=None):
        """Start scanning multiple URLs"""
        def scan_worker():
            total_urls = len(urls)
            for i, url in enumerate(urls):
                if progress_callback:
                    progress_callback(f"Scanning {i+1}/{total_urls}: {urlparse(url).netloc}")
                
                self.crawl_site(url, case_id, target_id, progress_callback)
                time.sleep(1)  # Rate limiting
            
            if progress_callback:
                progress_callback("Scan completed!")
        
        thread = threading.Thread(target=scan_worker)
        thread.daemon = True
        thread.start()
        return thread
    
    def get_matches(self, case_id):
        """Get all matches for a case"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT source_url, local_path, confidence, metadata, created_at
            FROM image_matches 
            WHERE case_id = ?
            ORDER BY confidence DESC
        ''', (case_id,))
        
        matches = cursor.fetchall()
        conn.close()
        return matches
    
    def generate_report(self, case_id):
        """Generate PDF report"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.units import inch
            
            matches = self.get_matches(case_id)
            
            report_path = os.path.join(self.results_dir, f"{case_id}_report.pdf")
            doc = SimpleDocTemplate(report_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            story.append(Paragraph(f"OSINT Image Analysis Report - Case: {case_id}", styles['Title']))
            story.append(Spacer(1, 12))
            
            # Summary
            story.append(Paragraph(f"Total Matches Found: {len(matches)}", styles['Heading2']))
            story.append(Paragraph(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            story.append(Spacer(1, 12))
            
            # Matches
            for i, (url, local_path, confidence, metadata, created_at) in enumerate(matches[:10]):  # Top 10 matches
                story.append(Paragraph(f"Match #{i+1}", styles['Heading3']))
                story.append(Paragraph(f"Confidence: {confidence:.2%}", styles['Normal']))
                story.append(Paragraph(f"Source: {url}", styles['Normal']))
                story.append(Paragraph(f"Found: {created_at}", styles['Normal']))
                
                # Add image if exists
                if os.path.exists(local_path):
                    try:
                        img = RLImage(local_path, width=2*inch, height=2*inch)
                        story.append(img)
                    except:
                        pass
                
                story.append(Spacer(1, 12))
            
            doc.build(story)
            return report_path
            
        except Exception as e:
            print(f"Error generating report: {e}")
            return None
    
    def get_available_platforms(self):
        """Get list of available platforms for scanning"""
        return list(self.platforms.keys())