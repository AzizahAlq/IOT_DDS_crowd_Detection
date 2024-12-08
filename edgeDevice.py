# edge device code 
import os
import cv2
import numpy as np
import argparse
import time
from ultralytics import YOLO
from cyclonedds.domain import DomainParticipant
from cyclonedds.topic import Topic
from cyclonedds.sub import DataReader
from cyclonedds.pub import DataWriter
from cyclonedds.idl import IdlStruct
from cyclonedds.core import Qos , Policy
from cyclonedds.idl.types import int32
from base64 import b64decode
from dataclasses import dataclass

@dataclass
class CrowdCount(IdlStruct):
    camera_id: str
    count: int32
    description: str
    timestamp: float  # Timestamp of the frame (in seconds)

# Define the VideoFrame structure
@dataclass
class VideoFrame(IdlStruct):
    camera_id: str  # Camera ID to identify each camera
    frame_data: str  # Base64-encoded frame data
    timestamp: float  # Timestamp of the frame (in seconds)

class PeopleDetector:
    CONFIDENCE_THRESHOLD = 0.3
    FONT_SIZE = 0.5
    TEXT_COLOR = (0, 255, 255)
    INFO_BOX_COLOR = (138, 72, 48)
    TEXT_THICKNESS = 1

    COUNT_LABEL_POSITION = (15, 22)
    COUNT_TEXT_POSITION = (100, 22)

    def __init__(self, model_version: str) -> None:
        self.count = 0
        self.model_version = model_version
        self.model = self.initialize_model()
        #qos=Qos(Policy.Reliability.BestEffort, Policy.Durability.Volatile, Policy.PresentationAccessScope.Instance(coherent_access=False, ordered_access=False), Policy.DestinationOrder.BySourceTimestamp, Policy.TimeBasedFilter(0))

        qos=Qos(Policy.Reliability.BestEffort, Policy.Durability.Volatile, Policy.TimeBasedFilter(0))
        self.participant = DomainParticipant()
        self.video_topic = Topic(self.participant, "VideoFrames", VideoFrame)
        self.reader = DataReader(self.participant, self.video_topic , qos)

        # Initialize DDS Publisher for Crowd Count
        self.crowd_topic = Topic(self.participant, "crowd_count", CrowdCount)
        self.writer = DataWriter(self.participant, self.crowd_topic, qos=Qos(Policy.Reliability.BestEffort, Policy.Durability.Volatile))

    def initialize_model(self):
        if self.model_version == "face":
            model = YOLO("model/yolov5x.pt")  # Adjust model path as needed
        else:
            raise ValueError("Unsupported model version. Please use 'face'.")
        return model

    def decode_frame(self, base64_data):
        frame_bytes = b64decode(base64_data)
        frame = np.frombuffer(frame_bytes, dtype=np.uint8)
        return cv2.imdecode(frame, cv2.IMREAD_COLOR)

    def display_count_box(self, image: np.ndarray) -> None:
        cv2.rectangle(image, (0, 0), (130, 35), self.INFO_BOX_COLOR, -1)
        cv2.putText(image, 'People: ', self.COUNT_LABEL_POSITION, cv2.FONT_HERSHEY_SIMPLEX,
                    self.FONT_SIZE, self.TEXT_COLOR, self.TEXT_THICKNESS)
        cv2.putText(image, str(self.count), self.COUNT_TEXT_POSITION, cv2.FONT_HERSHEY_SIMPLEX,
                    self.FONT_SIZE, self.TEXT_COLOR, self.TEXT_THICKNESS)

    def process_video(self):
        print("Waiting for video frames...")
        while True:
            samples = self.reader.take()
            for sample in samples:
                try:
                    # Check if sample contains valid data
                    if hasattr(sample, 'frame_data'):
                        # Extract camera ID and frame data
                        camera_id = sample.camera_id
                        frame = self.decode_frame(sample.frame_data)  # Use `frame_data` directly
                        frame = cv2.resize(frame, (1280, 720))  

                        # Record inference time
                        start_time = cv2.getTickCount()

                        # Process the frame using the model
                        results = self.model(frame)
                        human_boxes = results[0].boxes if results else []

                        self.count = 0
                        for box in human_boxes:
                            if box.cls == 0 and box.conf >= self.CONFIDENCE_THRESHOLD:  
                                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                                conf = box.conf.cpu().numpy().item()
                                frame = cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                                frame = cv2.putText(frame, f'Person: {conf:.2f}', (int(x1), int(y1) - 10), 
                                                    cv2.FONT_HERSHEY_SIMPLEX, self.FONT_SIZE, self.TEXT_COLOR, self.TEXT_THICKNESS)
                                self.count += 1

                        # End time for inference
                        end_time = cv2.getTickCount()
                        total_time_ms = (end_time - start_time) / cv2.getTickFrequency() * 1000

                        # Log the inference time and details
                        print(f"Camera ID: {camera_id} - Inference time: {total_time_ms:.2f}ms - Detected: {self.count} persons")

                        # Publish the person count via DDS, including camera_id
                        message = CrowdCount(camera_id=camera_id, count=self.count, description="Crowd detected", timestamp=time.time())
                        self.writer.write(message)

                        # Display the count box
                        self.display_count_box(frame)
                        cv2.imshow('output', frame)

                        if cv2.waitKey(10) & 0xFF == ord('q'):
                            return
                    else:
                        print("No valid frame data found.")
                except Exception as e:
                    print(f"Error processing sample: {e}")

    def __del__(self):
        cv2.destroyAllWindows()

if __name__ == "__main__":
    detector = PeopleDetector(model_version="face")
    detector.process_video()
