from moviepy import VideoFileClip
import os

input_file = "Screen Recording 2026-05-14 123703.mp4"
output_file = "Screen_Recording_Compressed.mp4"

print(f"Loading {input_file}...")
clip = VideoFileClip(input_file)
duration = clip.duration
print(f"Video duration: {duration} seconds")

# Target 95MB
target_size_bytes = 95 * 1024 * 1024
target_size_bits = target_size_bytes * 8

# Calculate bitrate (bits per second)
audio_bitrate_kbps = 128
audio_bitrate_bits = audio_bitrate_kbps * 1024
video_bitrate_bits = (target_size_bits / duration) - audio_bitrate_bits

if video_bitrate_bits < 0:
    print("Error: Target size is too small for this duration even with just audio.")
    exit(1)

video_bitrate_kbps = int(video_bitrate_bits / 1024)
print(f"Calculated video bitrate: {video_bitrate_kbps}k")

print(f"Compressing video...")
clip.write_videofile(
    output_file, 
    bitrate=f"{video_bitrate_kbps}k", 
    audio_bitrate=f"{audio_bitrate_kbps}k"
)
print("Compression complete!")
