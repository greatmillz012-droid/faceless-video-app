import os

magick_dir = r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\bin"
magick_exe = r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"
if os.path.isdir(magick_dir):
    os.environ["PATH"] = magick_dir + os.pathsep + os.environ.get("PATH", "")
    os.environ["IMAGEMAGICK_BINARY"] = magick_exe

from moviepy.config import change_settings

change_settings({"IMAGEMAGICK_BINARY": magick_exe})

from PIL import Image
from moviepy.editor import AudioFileClip, ColorClip, CompositeVideoClip, TextClip, VideoFileClip

if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

VIDEO_W, VIDEO_H = 1080, 1920


def render_video(background_path: str, audio_path: str, words: list[dict], output_path: str) -> str:
    audio = AudioFileClip(audio_path)
    duration = audio.duration

    bg = VideoFileClip(background_path)
    bg = bg.without_audio()
    bg = bg.resize(height=VIDEO_H)
    if bg.w < VIDEO_W:
        bg = bg.resize(width=VIDEO_W)
    bg = bg.crop(x_center=bg.w / 2, y_center=bg.h / 2, width=VIDEO_W, height=VIDEO_H)

    if bg.duration < duration:
        n_loops = int(duration // bg.duration) + 1
        from moviepy.video.compositing.concatenate import concatenate_videoclips

        bg = concatenate_videoclips([bg] * n_loops)
    bg = bg.subclip(0, duration)

    caption_clips = []
    chunk = []
    chunk_start = None
    MAX_CHUNK_WORDS = 4

    for w in words:
        if chunk_start is None:
            chunk_start = w["start"]
        chunk.append(w["word"])
        if len(chunk) >= MAX_CHUNK_WORDS:
            caption_clips.append(_make_caption_clip(" ".join(chunk), chunk_start, w["end"]))
            chunk, chunk_start = [], None
    if chunk:
        caption_clips.append(_make_caption_clip(" ".join(chunk), chunk_start, words[-1]["end"]))

    final = CompositeVideoClip([bg, *caption_clips], size=(VIDEO_W, VIDEO_H))
    final = final.set_audio(audio)
    final = final.set_duration(duration)

    final.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="medium",
        bitrate="6000k",
    )
    return output_path


def _make_caption_clip(text: str, start: float, end: float):
    txt = TextClip(
        text.upper(),
        fontsize=70,
        font="Arial-Bold",
        color="white",
        stroke_color="black",
        stroke_width=3,
        method="caption",
        size=(VIDEO_W - 120, None),
        align="center",
    )
    txt = txt.set_position(("center", VIDEO_H * 0.72))
    txt = txt.set_start(start).set_end(end)
    return txt
