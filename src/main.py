from concurrent.futures import ProcessPoolExecutor
from functools import cache
import os
import sys
import time
import cv2 as cv
import pygame

ASCII_SCALE = " .:-=+*#%@"
FALLBACK_FPS = 60


@cache
def get_ascii_symbol(pixel: float):
    return ASCII_SCALE[pixel // 36]


def main():
    with ProcessPoolExecutor(2) as executor:
        executor.submit(video_process)
        executor.submit(audio_process)


def video_process():
    capture = cv.VideoCapture("src/video/bad-apple.mp4")
    capture.set(cv.CAP_PROP_POS_FRAMES, 0)

    video_fps = capture.get(cv.CAP_PROP_FPS)
    if video_fps is None or video_fps <= 0:
        video_fps = FALLBACK_FPS

    frame_duration = 1 / video_fps
    next_frame_time = time.perf_counter()

    print("\033[2J", end="")

    while True:
        ret, frame = capture.read()
        if ret is False:
            break

        frame_to_ascii(frame)

        next_frame_time += frame_duration
        time.sleep(next_frame_time - time.perf_counter())


def audio_process():
    pygame.mixer.init()

    pygame.mixer.music.load("./src/sound/bad-apple.wav")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        time.sleep(1 / 60)


def frame_to_ascii(frame: cv.MatLike):
    gray_scale_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    term_cols, term_lines = os.get_terminal_size()
    resized_frame = cv.resize(gray_scale_frame, (term_cols, term_lines))

    ascii_frame = "\n".join(
        "".join(get_ascii_symbol(line) for line in row) for row in resized_frame
    )

    sys.stdout.write("\033[H")
    sys.stdout.write(ascii_frame)
    sys.stdout.flush()


if __name__ == "__main__":
    main()
