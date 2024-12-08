# IoT-Based Crowd Detection System using Docker, DDS, and Flask

## Introduction

This project demonstrates the development of an **IoT-based crowd detection system** that utilizes **edge devices**, **Data Distribution Service (DDS)** for communication, and a **Flask-based web server** for displaying  massages streams from multiple sources. Each edge device simulates an IoT camera processing video input to detect the number of people present in the scene. The detected crowd count is sent to a central DDS server, and the video feed is streamed from the camera processing video input to the edge devices

The system is designed with modularity and scalability in mind, allowing the addition of more edge devices, easy swapping of detection models, and flexible communication via DDS. This system is suitable for real-world IoT scenarios where local edge processing is essential, and cloud-based decision-making or monitoring is required.

---

## Table of Contents

1. Overview of the System Architecture
2. System Components
3. DDS Communication
4. Dockerized Edge Devices
5. Flask-Based Web Interface
6. Video Processing and Crowd Detection
7. Setting Up the System
8. Running the System
9. Understanding the Code
10. Scaling the System
11. Potential Use Cases
12. Conclusion

---

## Overview of the System Architecture

The system architecture of this project simulates a distributed IoT environment where **edge devices** (each represented by a Docker container) detect crowds from video streams and communicate the results to a **central DDS server**. The video streams, along with the real-time crowd detection data, are then displayed on a web interface hosted by a **Flask server**.

At the heart of the system is **Docker**, which encapsulates each edge device and the DDS server into separate containers, providing isolation, scalability, and ease of deployment. The **DDS (Data Distribution Service)** protocol allows real-time communication between the edge devices and the central server, ensuring low-latency data transmission.

The key components of the system are:

- **Dockerized Edge Devices**: Each device processes video feeds locally using **YOLOv5** for crowd detection and sends the crowd count data to the DDS server.
- **DDS Communication**: Facilitates real-time messaging between edge devices and the DDS server.
- **Flask-Based Web Interface**: A lightweight web server displays live video streams and crowd detection results in real-time.
  
---

## System Components

The following sections describe each major component of the system in detail.

### 1. Edge Devices

Each **edge device** simulates an IoT camera by processing pre-recorded video files and detecting the number of people in the scene using a machine learning model. The processed video frames are sent to the Flask server, and the crowd count is communicated via DDS. Edge devices are designed to run inside **Docker containers**, which allows for easy scaling and deployment.

#### Responsibilities:
- Process video frames using **YOLOv5** to detect people.
- Publish the detected crowd count via DDS.
- Send the processed video frames to the Flask server for visualization.

### 2. Data Distribution Service (DDS)

**DDS (Data Distribution Service)** is a middleware protocol used for real-time data exchange between systems. In this project, DDS facilitates communication between the edge devices and the central DDS server. Each edge device publishes its crowd detection data, and the server acts as a subscriber that listens for the incoming data.

#### DDS Key Concepts:
- **DomainParticipant**: Represents a node in the DDS network.
- **Topic**: Defines the type of data being exchanged (e.g., crowd count).
- **DataWriter**: Edge devices publish data using DataWriters.
- **DataReader**: The DDS server receives data using DataReaders.

### 3. Flask Web Server

The **Flask server** is responsible for hosting the web interface that displays live video streams and crowd detection results. It accepts video frames from edge devices and renders them in real-time on a webpage, along with the crowd count data. The Flask server also allows for interaction between different components via RESTful APIs.

#### Responsibilities:
- Serve the web interface.
- Stream video frames received from edge devices.
- Display crowd count data on the webpage.

---

## DDS Communication

The communication between edge devices and the DDS server is based on the **publish-subscribe** pattern. Each edge device publishes crowd count data to a topic, and the DDS server subscribes to this topic to receive real-time updates. The system is designed to ensure low-latency, real-time communication, which is crucial for IoT systems where decisions need to be made quickly based on incoming data.

#### Key DDS Components:
- **Participant**: Both the edge devices and the DDS server create a `DomainParticipant` to join the same DDS domain.
- **Topic**: The `Topic` object represents the type of data being exchanged, in this case, `CrowdCount`.
- **DataWriter**: Edge devices create a `DataWriter` to publish the crowd count.
- **DataReader**: The DDS server uses a `DataReader` to receive the published crowd count data.

Each `CrowdCount` message contains:
- **count**: The number of people detected in the video frame.
- **description**: A short description or identifier, such as the edge device ID.

---

## Dockerized Edge Devices

The edge devices run inside Docker containers, making the system scalable and easy to deploy. Each container runs an instance of the `crowd_detection.py` script, which processes video files, performs crowd detection using the **YOLOv5** model, and sends the results to the Flask server and the DDS server.

Docker provides isolation for each edge device, ensuring that they can run independently of each other, and allows the system to be easily scaled by simply spinning up new containers. This makes it possible to simulate a large-scale IoT network with multiple edge devices.

---

## Flask-Based Web Interface

The **Flask web server** provides a user-friendly interface for visualizing the results from the edge devices. The video feeds are displayed side by side, and each feed shows the number of people detected in real-time.

#### Flask Responsibilities:
- **Render HTML Templates**: The web server renders an `index.html` template that displays the video streams.
- **Stream Video**: The server receives video frames from the edge devices via HTTP POST requests and streams them to the client browser using `multipart/x-mixed-replace`, which allows for real-time video display.
- **Handle Incoming Requests**: The server handles requests from the edge devices to receive the video frames and crowd detection data.

---

## Video Processing and Crowd Detection

The edge devices use **YOLOv5** (You Only Look Once), a pre-trained deep learning model, to detect objects in the video frames. YOLOv5 is known for its high accuracy and speed, making it ideal for real-time applications like crowd detection.

The video processing pipeline is as follows:
1. **Capture Video Frames**: The video file is loaded, and frames are processed in sequence.
2. **Run YOLOv5 Inference**: Each frame is passed through the YOLOv5 model to detect objects (in this case, people).
3. **Draw Bounding Boxes**: Detected people are highlighted with bounding boxes on the frame.
4. **Send Frames to Flask Server**: The processed frame is sent to the Flask server for display.
5. **Send Crowd Count via DDS**: The number of people detected in the frame is published to the DDS server.

---

## Setting Up the System

The system is entirely Dockerized, so setup is relatively straightforward. Follow the steps below to set up and run the system on your machine.

### Prerequisites:
- **Docker**: Ensure Docker is installed and running on your machine.
- **Docker Compose**: Docker Compose is used to manage the multi-container setup.
- **Python 3.x**: Required for running the Python scripts inside the containers.

### Project Structure:

The project directory is structured as follows:

```
/IoT-BasedCrowdDetectionSystem/
│
├── /data/
│   └── /videos/                 # Directory containing the pre-recorded video files
│       ├── crowd_scene1.mp4
│       └── crowd_scene2.mp4
│       └── crowd_scene3.mp4
├── /model/                # Directory containing the yolo models for AI crowd detection
│   └── yolov5s.pt
│   └── yolov5xu.pt
│   └── yolov8n.pt
│
├── /templates/
│   └── index.html               # HTML template for the Flask web interface
│
├── edgeDevice.py            # Script for edge device     
├── cloudserver.py           # Flask web and DDS server script
├── requirements.txt         # Python dependencies
└── README.md                # This readme file
```

---

## Running the System

Follow these steps to run the system:

### Step 1: Clone the Repository

Clone the project repository to your local machine.

### Step 2: Prepare Video Files

Ensure the pre-recorded video files are placed inside the `/data/videos/` directory. This will be used as input for the edge devices.

### Step 3: Build Docker Containers

Use Docker Compose to build the Docker containers for the edge devices, DDS server, and Flask server.

```bash
docker-compose build
```

This command will build all the necessary Docker images for the system.

### Step 4: Run the System
Once the containers are built, you can start the system using Docker Compose.

```bash
docker-compose up
```

This command will start all containers, including the edge devices, DDS server, and Flask web server.

### Step 5: Access the Flask Web Interface
Open your web browser and go to http://localhost:5001 to access the web interface. You should see the live video streams from the edge devices along with the detected crowd counts.

---

### Run Locally

To run the crowd detection project locally, you need to set up a Python virtual environment and install all necessary dependencies. Follow these steps:

1. **Create a Virtual Environment**:
   First, you need to create a virtual environment in your project directory. Run the following command to create it:
   
```bash
   python3 -m venv venv
```
This will create a new folder named `venv` in your project directory, which will contain your virtual environment.

2. **Activate the Virtual Environment**:
To activate the virtual environment, run the appropriate command based on your operating system:

- On **macOS/Linux**:

```bash
source venv/bin/activate
```

- On **Windows**:

```bash
  venv\Scripts\activate
```

3. **Install Dependencies**:
Once the virtual environment is activated, install the project dependencies using `pip`. The dependencies are listed in the `requirements.txt` file. Run the following command to install them:

```bash
pip install -r requirements.txt
```

4. **Run Locally**:
Now to run the crowd detection locally without using Docker, you can use the following command. This will execute the crowd detection on the specified video file (`crowd_scene1.mp4` in this case):

```bash
python local_crowd_detection.py --path data/videos/crowd_scene1.mp4 #to run detection on video 1
python local_crowd_detection.py --path data/videos/crowd_scene2.mp4 #to run detection on video 2
```

Make sure that the necessary dependencies are installed, and the `local_crowd_detection.py` script is properly configured to read the video file and perform detection using the YOLOv5 model. You can adjust the `--path` argument to point to any video file or device of your choice.

---

## Understanding the Code
The following sections provide a detailed explanation of the key scripts used in the project.

**1. crowd_detection.py**  
This script is responsible for processing video files on the edge devices. It uses YOLOv5 for detecting people in the video frames and sends the crowd count via DDS. The video frames are also sent to the Flask server for real-time display.

**2. dds_server.py**  
This script runs on the central DDS server. It listens for incoming crowd count data from the edge devices and logs the received data.

**3. app.py**  
This script runs the Flask web server. It serves the web interface and handles incoming video frames from the edge devices. It streams the video frames in real-time and displays the crowd count data.


## **Scaling the System**
The system is highly scalable. You can add more edge devices by simply copying the edge_device service definition in the docker-compose.yml file and pointing it to a new video file or direct feed from IOT Camera devices. Each new edge device will automatically join the DDS domain and start publishing crowd count data to the central server.

To scale the system, follow these steps:
- Add New Video Files: Place new video files in the /data/videos/ directory.
- Duplicate Edge Device Definition: In the docker-compose.yml file, copy the edge_device service definition and modify it for the new device.
- Rebuild and Run: Rebuild the Docker containers and start the system again.

## Potential Use Cases
This system can be adapted for various real-world applications, such as:

- Smart City Surveillance: Detect crowds in public spaces to monitor foot traffic and ensure public safety.
- Event Management: Monitor crowd density at large events to prevent overcrowding and ensure a smooth flow of people.
- Retail Analytics: Use crowd detection in stores to monitor customer behavior and optimize store layouts.
- COVID-19 Safety: Monitor crowd sizes in public spaces to ensure compliance with social distancing regulations.


## Summary
This project demonstrates a comprehensive solution for building an IoT-based crowd detection system using Docker, DDS, and Flask. It showcases the power of Docker for containerizing edge devices, DDS for real-time communication, and Flask for providing a web interface for visualization. The system is modular, scalable, and flexible, making it a great foundation for developing more complex IoT applications. Whether for smart city surveillance, event management, or retail analytics, this system can be adapted to meet a wide range of real-world use cases.