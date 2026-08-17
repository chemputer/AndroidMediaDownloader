#!/usr/bin/env python3
"""Media Downloader Kivy App with custom resolution, codec controls, and FFmpeg post-processing."""

import glob
import os
import re
import subprocess
import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.switch import Switch
from kivy.uix.textinput import TextInput

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

try:
    from RedDownloader import RedDownloader
except ImportError:
    RedDownloader = None


def get_system_clipboard() -> str:
    """Retrieve text from Android or system clipboard."""
    try:
        text = Clipboard.paste()
        if text:
            return text.strip()
    except Exception:
        pass

    try:
        res = subprocess.run(
            ["termux-clipboard-get"], capture_output=True, text=True, timeout=2
        )
        return res.stdout.strip()
    except Exception:
        return ""


def get_download_path() -> str:
    """Determine standard public download directory."""
    target = "/sdcard/Download"
    if not os.path.exists(target):
        target = os.path.expanduser("~/downloads")
        os.makedirs(target, exist_ok=True)
    return target


class SettingsPopup(Popup):
    """Configuration menu for container format defaults."""

    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app_instance = app_instance
        self.title = "Format & Container Settings"
        self.size_hint = (0.9, 0.5)

        layout = GridLayout(cols=2, padding=dp(12), spacing=dp(10))

        # Video Container Option
        layout.add_widget(Label(text="Video Container:", font_size="15sp"))
        self.video_container_spinner = Spinner(
            text=self.app_instance.pref_video_container,
            values=("mp4", "mkv"),
            font_size="15sp",
        )
        layout.add_widget(self.video_container_spinner)

        # Audio Container Option
        layout.add_widget(Label(text="Audio Format:", font_size="15sp"))
        self.audio_container_spinner = Spinner(
            text=self.app_instance.pref_audio_container,
            values=("mp3", "mp4", "m4a", "ogg", "oga"),
            font_size="15sp",
        )
        layout.add_widget(self.audio_container_spinner)

        # Save Button
        save_btn = Button(
            text="Save Settings",
            size_hint_y=None,
            height=dp(45),
            font_size="16sp",
        )
        save_btn.bind(on_press=self.save_settings)

        main_box = BoxLayout(orientation="vertical", spacing=dp(10))
        main_box.add_widget(layout)
        main_box.add_widget(save_btn)

        self.content = main_box

    def save_settings(self, instance):
        self.app_instance.pref_video_container = (
            self.video_container_spinner.text.lower()
        )
        self.app_instance.pref_audio_container = (
            self.audio_container_spinner.text.lower()
        )
        self.app_instance.set_status(
            f"Settings saved: Video[{self.app_instance.pref_video_container.upper()}], "
            f"Audio[{self.app_instance.pref_audio_container.upper()}]"
        )
        self.dismiss()


class MediaDownloaderApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pref_video_container = "mp4"
        self.pref_audio_container = "mp3"

    def build(self):
        Window.maximize()

        self.root_layout = BoxLayout(
            orientation="vertical", padding=dp(12), spacing=dp(10)
        )

        # Header Row with Settings
        header_row = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=dp(40)
        )
        header_row.add_widget(
            Label(
                text="Media Downloader Pro",
                font_size="20sp",
                bold=True,
                halign="left",
            )
        )

        settings_btn = Button(
            text="Settings", size_hint_x=None, width=dp(90), font_size="14sp"
        )
        settings_btn.bind(on_press=self.open_settings_popup)
        header_row.add_widget(settings_btn)
        self.root_layout.add_widget(header_row)

        # URL Input & Clipboard Paste
        input_row = BoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(48),
        )
        self.url_input = TextInput(
            hint_text="Paste YouTube or Reddit URL...",
            multiline=False,
            font_size="15sp",
        )
        input_row.add_widget(self.url_input)

        paste_btn = Button(
            text="Paste", size_hint_x=None, width=dp(80), font_size="15sp"
        )
        paste_btn.bind(on_press=self.paste_clipboard)
        input_row.add_widget(paste_btn)
        self.root_layout.add_widget(input_row)

        # Download Controls Grid
        controls_grid = GridLayout(
            cols=2, spacing=dp(8), size_hint_y=None, height=dp(100)
        )

        controls_grid.add_widget(
            Label(text="Audio Only:", font_size="15sp", halign="left")
        )
        self.audio_switch = Switch(active=False, size_hint_x=None, width=dp(60))
        self.audio_switch.bind(active=self.on_mode_change)
        controls_grid.add_widget(self.audio_switch)

        controls_grid.add_widget(
            Label(text="Max Resolution:", font_size="15sp", halign="left")
        )
        self.res_spinner = Spinner(
            text="1080p",
            values=("Best", "1080p", "720p", "480p", "360p"),
            font_size="15sp",
        )
        controls_grid.add_widget(self.res_spinner)
        self.root_layout.add_widget(controls_grid)

        # Action Button
        self.download_btn = Button(
            text="Start Download",
            size_hint_y=None,
            height=dp(50),
            font_size="18sp",
        )
        self.download_btn.bind(on_press=self.start_download)
        self.root_layout.add_widget(self.download_btn)

        # Output Log Window
        self.status_label = Label(
            text="Status: Ready", font_size="14sp", halign="left", valign="top"
        )
        self.status_label.bind(size=self.status_label.setter("text_size"))
        self.root_layout.add_widget(self.status_label)

        return self.root_layout

    def open_settings_popup(self, instance):
        popup = SettingsPopup(app_instance=self)
        popup.open()

    def on_mode_change(self, instance, active: bool):
        self.res_spinner.disabled = active
        mode_str = (
            f"Audio ({self.pref_audio_container.upper()})"
            if active
            else f"Video ({self.pref_video_container.upper()})"
        )
        self.set_status(f"Mode changed to: {mode_str}")

    def paste_clipboard(self, instance):
        text = get_system_clipboard()
        if text:
            self.url_input.text = text
            self.set_status("Pasted link from clipboard.")
        else:
            self.set_status("Error: Clipboard empty or inaccessible.")

    def set_status(self, text: str):
        Clock.schedule_once(
            lambda dt: setattr(self.status_label, "text", f"Status: {text}")
        )

    def start_download(self, instance):
        url = self.url_input.text.strip()
        if not url:
            self.set_status("Error: Please enter a valid URL.")
            return

        self.download_btn.disabled = True
        audio_only = self.audio_switch.active
        target_res = self.res_spinner.text

        threading.Thread(
            target=self._worker_process,
            args=(url, audio_only, target_res),
            daemon=True,
        ).start()

    def _worker_process(self, url: str, audio_only: bool, target_res: str):
        download_dir = get_download_path()
        is_reddit = "reddit.com" in url.lower() or "redd.it" in url.lower()

        try:
            if is_reddit:
                self._handle_reddit_download(
                    url, download_dir, audio_only, target_res
                )
            else:
                self._handle_ytdlp_download(
                    url, download_dir, audio_only, target_res
                )
        except Exception as err:
            self.set_status(f"Download Error: {str(err)}")
        finally:
            Clock.schedule_once(
                lambda dt: setattr(self.download_btn, "disabled", False)
            )

    def _handle_ytdlp_download(
        self, url: str, target_dir: str, audio_only: bool, target_res: str
    ):
        if yt_dlp is None:
            raise ImportError(
                "yt-dlp missing. Install via 'pip install yt-dlp'."
            )

        output_template = os.path.join(target_dir, "%(title)s.%(ext)s")
        opts = {"outtmpl": output_template, "quiet": True}

        if audio_only:
            opts.update(
                {
                    "format": "bestaudio/best",
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": self.pref_audio_container,
                        "preferredquality": "0",
                    }],
                }
            )
            self.set_status(
                f"Downloading audio ({self.pref_audio_container.upper()})..."
            )
        else:
            # Map target resolution to height constraint
            res_num = (
                re.sub(r"\D", "", target_res) if target_res != "Best" else None
            )

            if res_num:
                format_str = (
                    f"bestvideo[height<={res_num}]+bestaudio/best[height<={res_num}]/best"
                )
            else:
                format_str = "bestvideo+bestaudio/best"

            opts.update({
                "format": format_str,
                "merge_output_format": self.pref_video_container,
            })

            # Add FFmpeg downscale filter ensuring NO upscaling
            if res_num:
                max_h = int(res_num)
                opts["postprocessor_args"] = [
                    "-vf",
                    f"scale=-2:'min({max_h},ih)'",
                ]

            self.set_status(
                f"Downloading video ({target_res}, {self.pref_video_container.upper()})..."
            )

        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])

        self.set_status(f"Complete! Saved to {target_dir}")

    def _handle_reddit_download(
        self, url: str, target_dir: str, audio_only: bool, target_res: str
    ):
        if RedDownloader is None:
            raise ImportError(
                "RedDownloader missing. Install via 'pip install RedDownloader'."
            )

        self.set_status("Downloading Reddit submission...")

        if audio_only:
            RedDownloader.Download(
                url=url, outputpath=target_dir, MakeMP3=True
            )
            # Post-process to requested audio format if different from default MP3
            if self.pref_audio_container != "mp3":
                self._post_process_reddit_media(
                    target_dir, audio=True, target_res=target_res
                )
        else:
            RedDownloader.Download(url=url, outputpath=target_dir)
            self._post_process_reddit_media(
                target_dir, audio=False, target_res=target_res
            )

        self.set_status(f"Reddit download complete! Saved to {target_dir}")

    def _post_process_reddit_media(
        self, target_dir: str, audio: bool, target_res: str
    ):
        """Perform downscaling and container adjustments on downloaded Reddit files via FFmpeg."""
        list_of_files = glob.glob(os.path.join(target_dir, "*"))
        if not list_of_files:
            return

        latest_file = max(list_of_files, key=os.path.getctime)
        base, ext = os.path.splitext(latest_file)

        if audio:
            target_ext = f".{self.pref_audio_container}"
            if ext.lower() != target_ext:
                out_file = base + target_ext
                cmd = [
                    "ffmpeg",
                    "-y",
                    "-i",
                    latest_file,
                    "-vn",
                    "-acodec",
                    "copy" if target_ext in [".m4a", ".mp4"] else "libmp3lame",
                    out_file,
                ]
                subprocess.run(cmd, capture_output=True)
                if os.path.exists(out_file):
                    os.remove(latest_file)
        else:
            target_ext = f".{self.pref_video_container}"
            res_num = (
                re.sub(r"\D", "", target_res) if target_res != "Best" else None
            )

            out_file = base + "_conv" + target_ext
            cmd = ["ffmpeg", "-y", "-i", latest_file]

            if res_num:
                max_h = int(res_num)
                cmd.extend(["-vf", f"scale=-2:'min({max_h},ih)'"])

            cmd.extend(["-c:a", "copy", out_file])
            res = subprocess.run(cmd, capture_output=True)

            if res.returncode == 0 and os.path.exists(out_file):
                os.remove(latest_file)
                os.rename(out_file, base + target_ext)


if __name__ == "__main__":
    MediaDownloaderApp().run()
