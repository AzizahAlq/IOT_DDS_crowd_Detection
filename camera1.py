import os
import cv2
import time
from base64 import b64encode
from cyclonedds.domain import DomainParticipant
from cyclonedds.topic import Topic
from cyclonedds.pub import DataWriter
from cyclonedds.idl import IdlStruct
from cyclonedds.idl.types import int32
from base64 import b64decode
from dataclasses import dataclass
from datetime import datetime


@dataclass
class VideoFrame(IdlStruct):
    camera_id: str  # Camera ID to identify each camera
    frame_data: str  # Base64-encoded frame data
    timestamp: float  # Timestamp of the frame (in seconds)


class CameraPublisher:
    def __init__(self, video_source, camera_id="camera_1"):
        self.camera_id = camera_id
        self.cap = cv2.VideoCapture(video_source)
        if not self.cap.isOpened():
            raise ValueError(f"Unable to open video source: {video_source}")

        # Get the frame rate (FPS) of the video
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        print(f"Video source {video_source} opened with FPS: {self.fps}")

        # Initialize CycloneDDS Participant
        self.participant = DomainParticipant()
        self.topic = Topic(self.participant, "VideoFrames", VideoFrame)
        self.writer = DataWriter(self.participant, self.topic)

    def publish_frames(self):
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                print("End of video or cannot read frame.")
                break

            # Resize frame to reduce size (optional)
            frame = cv2.resize(frame, (640, 360))

            # Encode frame to JPEG
            _, encoded_frame = cv2.imencode(".jpg", frame)
            frame_bytes = encoded_frame.tobytes()

            # Encode the frame as base64 for transmission
            frame_base64 = b64encode(frame_bytes).decode("utf-8")

            # Get the current timestamp as a float (seconds since epoch)
            timestamp = time.time()

            # Create and publish the VideoFrame message with camera_id and timestamp
            message = VideoFrame(camera_id=self.camera_id, frame_data=frame_base64, timestamp=timestamp)
            self.writer.write(message)

            print(f"Published a frame from {self.camera_id} at {timestamp}")
            time.sleep(1 / self.fps)  # Control frame rate based on the video FPS

        self.cap.release()

    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()
        # Clean up DDS participant
        self.participant.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Camera Publisher Script")
    parser.add_argument("--path", type=str, required=True, help="Path to the video file")
    parser.add_argument("--camera_id", type=str, default="camera_1", help="Camera ID (default: camera_1)")
    args = parser.parse_args()

    video_source = args.path
    camera_id = args.camera_id

    if not os.path.exists(video_source):
        raise ValueError(f"Error: The video source '{video_source}' does not exist.")

    publisher = CameraPublisher(video_source, camera_id)
    try:
        publisher.publish_frames()
    except KeyboardInterrupt:
        print("Terminating...")