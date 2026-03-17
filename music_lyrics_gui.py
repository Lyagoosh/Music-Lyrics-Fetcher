import os
import sys
import time
import threading
import requests
import re
import json
import webbrowser
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, USLT
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen import File
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog

class MultiSourceLyricsFetcher:
    """Fetching lyrics from multiple sources"""
    
    def __init__(self, sources_order=None):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        
        # Available sources
        self.available_sources = {
            "Lyrics.ovh": self.get_lyrics_ovh,
            "Lrclib.net": self.get_lyrics_lrclib
        }
        
        # Set source priority order
        if sources_order:
            self.sources_priority = [(name, self.available_sources[name]) 
                                    for name in sources_order if name in self.available_sources]
        else:
            # Default order
            self.sources_priority = [
                ("Lyrics.ovh", self.get_lyrics_ovh),
                ("Lrclib.net", self.get_lyrics_lrclib)
            ]
    
    def get_lyrics_ovh(self, artist, title):
        """Source 1: Lyrics.ovh - simple and fast"""
        try:
            artist_encoded = requests.utils.quote(artist) if artist else ""
            title_encoded = requests.utils.quote(title)
            
            url = f"https://api.lyrics.ovh/v1/{artist_encoded}/{title_encoded}"
            response = self.session.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                lyrics = data.get('lyrics')
                if lyrics and len(lyrics) > 50:
                    return lyrics
            return None
        except Exception as e:
            print(f"Lyrics.ovh error: {e}")
            return None
    
    def get_lyrics_lrclib(self, artist, title):
        """Source 2: Lrclib.net - with synchronized lyrics support"""
        try:
            url = "https://lrclib.net/api/get"
            params = {
                "artist_name": artist if artist else "",
                "track_name": title
            }
            response = self.session.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                lyrics = data.get('plainLyrics')
                if not lyrics:
                    lyrics = data.get('syncedLyrics')
                if lyrics and len(lyrics) > 50:
                    return lyrics
            return None
        except Exception as e:
            print(f"Lrclib.net error: {e}")
            return None
    
    def fetch_lyrics(self, artist, title):
        """
        Try all sources in the given order
        Returns (lyrics, source_name)
        """
        if not title:
            return None, None
        
        # Clean title from extra characters
        title = re.sub(r'[^\w\s\-\(\)\[\]]', '', title)
        if artist:
            artist = re.sub(r'[^\w\s\-\.]', '', artist)
        
        # Try each source in priority order
        for source_name, source_func in self.sources_priority:
            try:
                lyrics = source_func(artist, title)
                if lyrics:
                    # Minimal cleaning (preserve structure)
                    lyrics = self.minimal_clean(lyrics)
                    if lyrics and len(lyrics) > 50:
                        return lyrics, source_name
            except Exception as e:
                print(f"Error with {source_name}: {e}")
                continue
            
            # Small delay between requests
            time.sleep(0.5)
        
        return None, None
    
    def minimal_clean(self, text):
        """Minimal text cleaning - preserve all spaces and structure"""
        if not text:
            return None
        
        # Only remove extra spaces at line ends
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove spaces only at start and end of line
            line = line.strip()
            if line:
                cleaned_lines.append(line)
            else:
                # Keep empty lines as separators
                cleaned_lines.append('')
        
        # Remove multiple empty lines at start and end
        while cleaned_lines and not cleaned_lines[0]:
            cleaned_lines.pop(0)
        while cleaned_lines and not cleaned_lines[-1]:
            cleaned_lines.pop()
        
        return '\n'.join(cleaned_lines)


class LyricsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Lyrics Fetcher")
        self.root.geometry("670x650")
        self.root.resizable(False, False)
        
        # Set window icon from embedded file
        if hasattr(sys, '_MEIPASS'):
            icon_path = os.path.join(sys._MEIPASS, "MusicLyricsFetcher.ico")
        else:
            icon_path = "MusicLyricsFetcher.ico"
        try:
            self.root.iconbitmap(default=icon_path)
        except:
            pass  # Ignore if icon not found
        
        # Variables
        self.work_folder = tk.StringVar(value=os.path.expanduser("~"))
        self.is_running = False
        self.fetcher = None
        
        # Source order (default)
        self.sources_order = [
            "Lyrics.ovh",
            "Lrclib.net"
        ]
        
        # Create interface
        self.create_widgets()
        
        # Load saved settings
        self.load_settings()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(title_frame, text="Music Lyrics Fetcher", 
                                font=('Arial', 16, 'bold'))
        title_label.pack()
        
        # Format support subtitle
        format_label = ttk.Label(title_frame, text="Supports MP3 and FLAC", 
                                font=('Arial', 9), foreground='green')
        format_label.pack()
        
        # Folder selection frame
        folder_frame = ttk.LabelFrame(main_frame, text="📁 Working folder with audio files", padding="8")
        folder_frame.pack(fill=tk.X, pady=(0, 8))
        
        path_frame = ttk.Frame(folder_frame)
        path_frame.pack(fill=tk.X, pady=(0, 3))
        
        self.folder_entry = ttk.Entry(path_frame, textvariable=self.work_folder, width=50)
        self.folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        browse_btn = ttk.Button(path_frame, text="📂 Browse...", command=self.browse_folder)
        browse_btn.pack(side=tk.RIGHT)
        
        self.folder_stats = ttk.Label(folder_frame, text="", font=('Arial', 8))
        self.folder_stats.pack(anchor=tk.W)
        
        self.work_folder.trace('w', lambda *args: self.update_folder_stats())
        
        # Source settings frame
        sources_frame = ttk.LabelFrame(main_frame, text="🔧 Lyrics Sources Settings", padding="8")
        sources_frame.pack(fill=tk.X, pady=(0, 8))
        
        # Info
        ttk.Label(sources_frame, 
                 text="Select source priority order:",
                 font=('Arial', 9)).pack(anchor=tk.W, pady=(0, 3))
        
        # Source list frame
        list_frame = ttk.Frame(sources_frame)
        list_frame.pack(fill=tk.X, pady=(0, 3))
        
        # Source listbox
        self.sources_listbox = tk.Listbox(list_frame, height=2, selectmode=tk.SINGLE,
                                          font=('Arial', 10), exportselection=False)
        self.sources_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Control buttons
        button_frame = ttk.Frame(list_frame)
        button_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        ttk.Button(button_frame, text="↑ Move Up", width=15, command=self.move_source_up).pack(pady=(0, 2))
        ttk.Button(button_frame, text="↓ Move Down", width=15, command=self.move_source_down).pack(pady=(0, 2))
        ttk.Button(button_frame, text="↻ Reset", width=15, command=self.reset_sources).pack(pady=(0, 2))
        
        # Update list
        self.update_sources_list()
        
        # Start button
        button_frame_main = ttk.Frame(main_frame)
        button_frame_main.pack(fill=tk.X, pady=(0, 8))
        
        self.start_button = ttk.Button(button_frame_main, text="🚀 START LYRICS SEARCH", 
                                       command=self.start_search)
        self.start_button.pack(fill=tk.X)
        
        # Progress bar
        self.progress_frame = ttk.Frame(main_frame)
        self.progress_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X)
        
        # Status
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(status_frame, text="Status:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=(0, 5))
        self.status_label = ttk.Label(status_frame, text="Ready to work", font=('Arial', 9))
        self.status_label.pack(side=tk.LEFT)
        
        # Log control buttons
        log_buttons = ttk.Frame(main_frame)
        log_buttons.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(log_buttons, text="🧹 Clear Log", command=self.clear_log).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(log_buttons, text="📂 Open Folder", command=self.open_folder).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(log_buttons, text="📋 Copy Log", command=self.copy_log).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(log_buttons, text="❓ About", command=self.show_about).pack(side=tk.LEFT)
        
        # Log output
        log_frame = ttk.LabelFrame(main_frame, text="📝 Execution Log", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD, 
                                                  font=('Consolas', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Color tags for log
        self.log_text.tag_config('success', foreground='green')
        self.log_text.tag_config('error', foreground='red')
        self.log_text.tag_config('warning', foreground='orange')
        self.log_text.tag_config('info', foreground='blue')
        self.log_text.tag_config('source', foreground='purple')
        
        # Detailed progress bar (hidden by default)
        self.progress_detailed_frame = ttk.Frame(main_frame)
        self.progress_var = tk.DoubleVar()
        self.progress_bar_detailed = ttk.Progressbar(self.progress_detailed_frame, 
                                                     variable=self.progress_var, maximum=100)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.after(100, self.update_folder_stats)
    
    def update_sources_list(self):
        """Update sources listbox"""
        self.sources_listbox.delete(0, tk.END)
        for source in self.sources_order:
            self.sources_listbox.insert(tk.END, source)
    
    def move_source_up(self):
        """Move source up in priority"""
        selection = self.sources_listbox.curselection()
        if selection and selection[0] > 0:
            idx = selection[0]
            self.sources_order[idx], self.sources_order[idx-1] = self.sources_order[idx-1], self.sources_order[idx]
            self.update_sources_list()
            self.sources_listbox.selection_set(idx-1)
            self.save_settings()
    
    def move_source_down(self):
        """Move source down in priority"""
        selection = self.sources_listbox.curselection()
        if selection and selection[0] < len(self.sources_order) - 1:
            idx = selection[0]
            self.sources_order[idx], self.sources_order[idx+1] = self.sources_order[idx+1], self.sources_order[idx]
            self.update_sources_list()
            self.sources_listbox.selection_set(idx+1)
            self.save_settings()
    
    def reset_sources(self):
        """Reset sources to default order"""
        self.sources_order = [
            "Lyrics.ovh",
            "Lrclib.net"
        ]
        self.update_sources_list()
        self.save_settings()
        self.log("↻ Source order reset to default", 'info')
    
    def browse_folder(self):
        folder = filedialog.askdirectory(
            title="Select folder with audio files (MP3 or FLAC)",
            initialdir=self.work_folder.get() if os.path.exists(self.work_folder.get()) else os.path.expanduser("~")
        )
        if folder:
            self.work_folder.set(folder)
            self.log(f"📁 Selected folder: {folder}", 'info')
            self.update_folder_stats()
    
    def update_folder_stats(self):
        folder = self.work_folder.get()
        if os.path.exists(folder):
            mp3_count = len([f for f in os.listdir(folder) if f.lower().endswith('.mp3')])
            flac_count = len([f for f in os.listdir(folder) if f.lower().endswith('.flac')])
            total = mp3_count + flac_count
            
            if total > 0:
                self.folder_stats.config(text=f"📊 Found: MP3: {mp3_count}, FLAC: {flac_count}, Total: {total}", 
                                        foreground='green')
            else:
                self.folder_stats.config(text="⚠ No MP3/FLAC files found", foreground='orange')
        else:
            self.folder_stats.config(text="❌ Folder does not exist", foreground='red')
    
    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    
                    # Load folder
                    folder = settings.get('folder', '')
                    if folder and os.path.exists(folder):
                        self.work_folder.set(folder)
                    
                    # Load source order
                    sources = settings.get('sources_order')
                    if sources and len(sources) == 2:
                        self.sources_order = sources
                        self.update_sources_list()
                    
            self.log("✅ Settings loaded", 'success')
        except:
            pass
    
    def save_settings(self):
        """Save settings to file"""
        try:
            settings = {
                'folder': self.work_folder.get().strip(),
                'sources_order': self.sources_order
            }
            with open('settings.json', 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            self.log(f"❌ Error saving settings: {e}", 'error')
            return False
    
    def log(self, message, tag=None):
        self.log_text.insert(tk.END, message + "\n", tag)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
    
    def copy_log(self):
        log_content = self.log_text.get(1.0, tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(log_content)
        self.log("📋 Log copied to clipboard", 'info')
    
    def show_about(self):
        about_text = """Music Lyrics Fetcher v3.0

Program for automatically adding lyrics to audio files.

🎵 Supported formats:
• MP3 (ID3 tags)
• FLAC (Vorbis Comments)

📚 Lyrics sources:
• Lyrics.ovh - fast and simple API
• Lrclib.net - with synchronized lyrics support

🎛️ Features:
• Adjustable source priority
• Preserves all spaces and text structure
• Auto-save settings

© 2026 by Lyagoosh"""

        # Create custom about dialog with clickable link
        about_dialog = tk.Toplevel(self.root)
        about_dialog.title("About")
        about_dialog.geometry("400x350")
        about_dialog.resizable(False, False)
        about_dialog.transient(self.root)
        about_dialog.grab_set()
        
        # Center the dialog
        about_dialog.update_idletasks()
        x = (about_dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (about_dialog.winfo_screenheight() // 2) - (350 // 2)
        about_dialog.geometry(f"+{x}+{y}")
        
        # Content frame
        content_frame = ttk.Frame(about_dialog, padding="20")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(content_frame, text="Music Lyrics Fetcher", 
                                font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Version
        version_label = ttk.Label(content_frame, text="Version 3.0", 
                                   font=('Arial', 10))
        version_label.pack(pady=(0, 15))
        
        # Description
        desc_text = """Program for automatically adding lyrics 
to MP3 and FLAC audio files.

🎵 Supported formats: MP3, FLAC
📚 Lyrics sources: Lyrics.ovh, Lrclib.net
🎛️ Adjustable source priority

Free and open source software."""
        
        desc_label = ttk.Label(content_frame, text=desc_text, 
                               font=('Arial', 9), justify=tk.CENTER)
        desc_label.pack(pady=(0, 15))
        
        # Copyright with clickable link
        copyright_frame = ttk.Frame(content_frame)
        copyright_frame.pack(pady=(0, 15))
        
        copyright_label = ttk.Label(copyright_frame, text="© 2026 ", 
                                     font=('Arial', 9))
        copyright_label.pack(side=tk.LEFT)
        
        # Clickable link
        link_label = tk.Label(copyright_frame, text="Lyagoosh", 
                               font=('Arial', 9, 'underline'), 
                               fg='blue', cursor='hand2')
        link_label.pack(side=tk.LEFT)
        link_label.bind('<Button-1>', lambda e: webbrowser.open('https://github.com/Lyagoosh'))
        
        # Close button
        close_btn = ttk.Button(content_frame, text="Close", 
                               command=about_dialog.destroy)
        close_btn.pack(pady=(10, 0))
    
    def open_folder(self):
        folder = self.work_folder.get()
        if os.path.exists(folder):
            import subprocess
            import platform
            
            if platform.system() == 'Windows':
                os.startfile(folder)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', folder])
            else:
                subprocess.run(['xdg-open', folder])
        else:
            messagebox.showerror("Error", "Folder does not exist!")
    
    def set_status(self, text, is_error=False):
        self.status_label.config(text=text, foreground='red' if is_error else 'black')
        self.root.update_idletasks()
    
    def get_audio_files(self, directory):
        """Get list of audio files (MP3 and FLAC)"""
        audio_files = []
        for file in os.listdir(directory):
            if file.lower().endswith(('.mp3', '.flac')):
                audio_files.append(os.path.join(directory, file))
        return audio_files
    
    def parse_filename(self, filename):
        """Parse filename to extract artist and title"""
        name_without_ext = os.path.splitext(filename)[0]
        separators = [' - ', ' -', '- ', '-', '_', ' – ', ' — ', '|', '//', '\\']
        
        for sep in separators:
            if sep in name_without_ext:
                parts = name_without_ext.split(sep, 1)
                if len(parts) == 2:
                    artist = parts[0].strip()
                    title = parts[1].strip()
                    if artist and title:
                        return artist, title
        
        return None, name_without_ext.strip()
    
    def get_song_metadata(self, file_path):
        """Get metadata from audio file (MP3 or FLAC)"""
        filename = os.path.basename(file_path)
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_ext == '.mp3':
                # Handle MP3
                try:
                    audio = EasyID3(file_path)
                    title = audio.get('title', [None])[0]
                    artist = audio.get('artist', [None])[0]
                    album = audio.get('album', [None])[0]
                except:
                    audio = File(file_path, easy=True)
                    if audio is None:
                        audio = EasyID3()
                    title = audio.get('title', [None])[0]
                    artist = audio.get('artist', [None])[0]
                    album = audio.get('album', [None])[0]
            
            elif file_ext == '.flac':
                # Handle FLAC
                try:
                    audio = FLAC(file_path)
                    title = audio.get('title', [None])[0] if audio.get('title') else None
                    artist = audio.get('artist', [None])[0] if audio.get('artist') else None
                    album = audio.get('album', [None])[0] if audio.get('album') else None
                except:
                    audio = File(file_path, easy=True)
                    if audio is None:
                        audio = FLAC()
                    title = audio.get('title', [None])[0] if audio.get('title') else None
                    artist = audio.get('artist', [None])[0] if audio.get('artist') else None
                    album = audio.get('album', [None])[0] if audio.get('album') else None
            
            else:
                return filename, None, None
            
            if title and artist:
                return title, artist, album
            
            file_artist, file_title = self.parse_filename(filename)
            
            final_title = title or file_title or filename
            final_artist = artist or file_artist
            
            if final_artist:
                final_artist = final_artist.replace('_', ' ').replace('.', ' ')
            
            return final_title, final_artist, album
            
        except Exception as e:
            self.log(f"  ⚠ Error reading metadata: {e}", 'warning')
            artist, title = self.parse_filename(filename)
            return title or filename, artist, None
    
    def add_lyrics_to_audio(self, file_path, lyrics):
        """Add lyrics to audio file metadata (MP3 or FLAC)"""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_ext == '.mp3':
                # For MP3 use ID3 tags
                audio = MP3(file_path, ID3=ID3)
                
                try:
                    audio.add_tags()
                except:
                    pass
                
                if audio.tags.getall('USLT'):
                    audio.tags.delall('USLT')
                
                uslt = USLT(encoding=3, lang='eng', desc='', text=lyrics)
                audio.tags.add(uslt)
                audio.save()
                
            elif file_ext == '.flac':
                # For FLAC use Vorbis Comments
                audio = FLAC(file_path)
                
                # Remove old lyrics tags
                if 'lyrics' in audio:
                    audio.pop('lyrics')
                if 'LYRICS' in audio:
                    audio.pop('LYRICS')
                
                # Add new lyrics
                audio['lyrics'] = lyrics
                audio.save()
            
            return True
            
        except Exception as e:
            self.log(f"  ✗ Error adding lyrics: {e}", 'error')
            return False
    
    def search_lyrics_thread(self):
        """Main thread for lyrics search"""
        try:
            work_dir = self.work_folder.get()
            
            if not os.path.exists(work_dir):
                self.log(f"❌ Folder does not exist: {work_dir}", 'error')
                self.set_status("Error: folder does not exist", is_error=True)
                self.is_running = False
                self.start_button.config(state=tk.NORMAL, text="🚀 START LYRICS SEARCH")
                self.progress_bar.stop()
                return
            
            # Show current source order
            sources_text = " → ".join(self.sources_order)
            self.log(f"📋 Source order: {sources_text}", 'info')
            
            self.fetcher = MultiSourceLyricsFetcher(self.sources_order)
            
            self.log("\n" + "="*60, 'info')
            self.log("🔍 SEARCHING AUDIO FILES", 'info')
            self.log("="*60, 'info')
            self.log(f"📁 Folder: {work_dir}", 'info')
            
            audio_files = self.get_audio_files(work_dir)
            
            if not audio_files:
                self.log("❌ No MP3/FLAC files found!", 'error')
                self.set_status("No audio files found", is_error=True)
                self.is_running = False
                self.start_button.config(state=tk.NORMAL, text="🚀 START LYRICS SEARCH")
                self.progress_bar.stop()
                return
            
            mp3_count = len([f for f in audio_files if f.lower().endswith('.mp3')])
            flac_count = len([f for f in audio_files if f.lower().endswith('.flac')])
            self.log(f"✅ Found files: MP3: {mp3_count}, FLAC: {flac_count}, Total: {len(audio_files)}", 'success')
            
            successful = 0
            failed = 0
            
            # Show detailed progress bar
            self.progress_detailed_frame.pack(fill=tk.X, pady=(5, 0))
            self.progress_bar_detailed.pack(fill=tk.X)
            self.progress_var.set(0)
            
            for i, audio_file in enumerate(audio_files, 1):
                if not self.is_running:
                    self.log("\n⏹ Process stopped by user", 'warning')
                    break
                
                filename = os.path.basename(audio_file)
                file_ext = os.path.splitext(audio_file)[1].upper()
                self.log(f"\n[{i}/{len(audio_files)}] {filename} ({file_ext})", 'info')
                
                self.progress_var.set((i-1) / len(audio_files) * 100)
                self.root.update_idletasks()
                
                title, artist, album = self.get_song_metadata(audio_file)
                self.log(f"  Title: {title}")
                if artist:
                    self.log(f"  Artist: {artist}")
                else:
                    self.log(f"  Artist: not specified", 'warning')
                
                self.log("  🔎 Searching lyrics...")
                
                # Search lyrics according to selected order
                lyrics, source = self.fetcher.fetch_lyrics(artist, title)
                
                if not lyrics:
                    self.log("  ✗ Lyrics not found in any source", 'error')
                    failed += 1
                    continue
                
                self.log(f"  ✓ Lyrics found in: {source}", 'source')
                self.log(f"  ✓ Lyrics received (length: {len(lyrics)} characters)", 'success')
                
                # Show first 200 characters preserving structure
                preview_lines = lyrics.split('\n')[:3]
                preview = ' | '.join(preview_lines)
                if len(preview) > 100:
                    preview = preview[:100] + "..."
                self.log(f"  📄 Lyrics preview: {preview}", 'info')
                
                if self.add_lyrics_to_audio(audio_file, lyrics):
                    successful += 1
                    self.log(f"  ✅ Lyrics successfully added to file!", 'success')
                else:
                    failed += 1
                
                # Delay between requests
                time.sleep(0.5)
            
            self.progress_var.set(100)
            
            self.log("\n" + "="*60, 'info')
            self.log("📊 RESULTS:", 'info')
            self.log(f"✅ Successfully processed: {successful}", 'success')
            self.log(f"❌ Failed to process: {failed}", 'error')
            self.log("="*60, 'info')
            
            if failed == 0 and successful > 0:
                self.set_status("✅ LYRICS SEARCH COMPLETED SUCCESSFULLY!")
                self.log("\n✨ ALL LYRICS SUCCESSFULLY ADDED!", 'success')
            elif successful > 0:
                self.set_status("⚠ Search completed, but not all lyrics found")
                self.log("\n⚠ Some lyrics not found in sources", 'warning')
            else:
                self.set_status("❌ No lyrics found", is_error=True)
                self.log("\n❌ Failed to find lyrics for songs", 'error')
            
        except Exception as e:
            self.log(f"\n❌ CRITICAL ERROR: {e}", 'error')
            self.set_status(f"Error: {str(e)[:50]}...", is_error=True)
        finally:
            self.is_running = False
            self.start_button.config(state=tk.NORMAL, text="🚀 START LYRICS SEARCH")
            self.progress_bar.stop()
            self.progress_detailed_frame.pack_forget()
    
    def start_search(self):
        """Start lyrics search"""
        if self.is_running:
            self.is_running = False
            self.start_button.config(text="🚀 START LYRICS SEARCH")
            self.log("\n⏹ Stopping process...", 'warning')
            return
        
        if not os.path.exists(self.work_folder.get()):
            messagebox.showerror("Error", "Selected folder does not exist!\nPlease select an existing folder with audio files.")
            return
        
        self.save_settings()
        
        self.is_running = True
        self.start_button.config(text="⏹ STOP")
        self.progress_bar.start()
        self.set_status("Searching lyrics...")
        
        self.clear_log()
        
        # Hide detailed progress bar before start
        self.progress_detailed_frame.pack_forget()
        
        thread = threading.Thread(target=self.search_lyrics_thread, daemon=True)
        thread.start()
    
    def on_closing(self):
        """Handle window closing"""
        if self.is_running:
            if messagebox.askyesno("Confirm", 
                                   "Search is still in progress. Are you sure you want to exit?"):
                self.is_running = False
                self.save_settings()
                self.root.destroy()
        else:
            self.save_settings()
            self.root.destroy()

def main():
    root = tk.Tk()
    app = LyricsApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
