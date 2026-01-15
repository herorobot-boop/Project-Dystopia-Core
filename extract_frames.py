import cv2
import os

def extract_frames(video_path, output_dir, interval=5):
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    count = 0
    frame_id = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if count % interval == 0:
            fname = f"{output_dir}/{frame_id:05d}.png"
            cv2.imwrite(fname, frame)
            frame_id += 1
        count += 1
    cap.release()
    print(f"✅ {frame_id}枚のフレームを抽出しました")
