from pathlib import Path
import shlex
import subprocess as sp
import os


def generate(prefix: str):
    f_name: Path = Path(f"~/.cache/vlssync/tests/{prefix}.mp4").expanduser()

    if not f_name.exists():
        f_name.parent.mkdir(parents=True, exist_ok=True)

        # Generate synthetic pattern.
        # Make the pattern gray: https://davidwalsh.name/convert-video-grayscale
        # Place the moov atom at the beginning of the file: https://superuser.com/questions/606653/ffmpeg-converting-media-type-aswell-as-relocating-moov-atom
        # Use superfast preset and tune zerolatency for all frames to be key frames https://lists.ffmpeg.org/pipermail/ffmpeg-user/2016-January/030127.html (not a must)
        # Make the file much smaller than 50MB.
        sp.run(shlex.split(
            f'ffmpeg -y -f lavfi -i testsrc=size=1920x1080:rate=1 -vf hue=s=0 -vcodec libx264 -preset superfast -tune zerolatency -pix_fmt yuv420p -t 1000 -movflags +faststart {f_name}'))

        # Add zero padding to the end of the file
        # https://stackoverflow.com/questions/12768026/write-zeros-to-file-blocks
        stat = os.stat(f_name)
        with open(f_name, 'r+') as of:
            of.seek(0, os.SEEK_END)
            of.write('\0' * (50 * 1024 * 1024 - stat.st_size))
            of.flush()


if __name__ == '__main__':
    generate("some")
