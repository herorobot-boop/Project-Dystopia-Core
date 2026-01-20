import cv2
import os
import sys

def extract_frame(video_path, output_path, position="middle"):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Failed to open video: {video_path}")
        return False

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames == 0:
        print("❌ No frames found in video.")
        return False

    if position == "middle":
        frame_number = total_frames // 2
    elif position == "start":
        frame_number = 0
    elif position == "end":
        frame_number = total_frames - 1
    else:
        frame_number = int(position)

    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(output_path, frame)
        print(f"✅ Frame saved to {output_path}")
        return True
    else:
        print("❌ Failed to read frame.")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python extract_frame.py input_video.mp4 output_image.jpg [position]")
    else:
        video = sys.argv[1]
        image = sys.argv[2]
        pos = sys.argv[3] if len(sys.argv) > 3 else "middle"
        extract_frame(video, image, pos)
