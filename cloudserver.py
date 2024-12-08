import threading
import csv
import os
import time
from collections import deque
from cyclonedds.domain import DomainParticipant
from cyclonedds.topic import Topic
from cyclonedds.sub import DataReader
from cyclonedds.idl import IdlStruct
from cyclonedds.idl.types import int32
from cyclonedds.core import Qos , Policy
from dataclasses import dataclass
import matplotlib.pyplot as plt

# To store metrics
latencies = []
throughput_data = deque(maxlen=10)  # Store throughput over 10-second windows
messages_received = 0
start_time = time.time()
time_elapsed = []  # Store time elapsed for plotting

# Define your DDS topic structure
@dataclass
class CrowdCount(IdlStruct):
    camera_id: str
    count: int32
    description: str
    timestamp: float  # Timestamp field for latency measurement

# File path to save CSV data
csv_file_path = '/Users/azizahalq/Desktop/IOT_TASK/crowd_count_data.csv'
latest_data = {"history": []}  # Change to a list to hold historical data

# Lock for thread-safe writes to the CSV
lock = threading.Lock()

# Function to write data to CSV file
def save_to_csv(device_id, crowd_count):
    try:
        file_exists = os.path.isfile(csv_file_path)
        with open(csv_file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['Device ID', 'Crowd Count'])  # Removed timestamp and description
            # Write the received data to the CSV
            writer.writerow([device_id, crowd_count])
    except Exception as e:
        print(f"Error writing to CSV: {e}")

# DDS Subscriber function (reading directly)
def dds_subscriber():
    global messages_received, start_time
    qos=Qos(Policy.Reliability.BestEffort, Policy.Durability.Volatile, Policy.TimeBasedFilter(0))  
    # Define QoS policies
    #qos = participant.qos()
    #qos.reliability.kind = 'BEST_EFFORT'
    #qos.durability.kind = 'VOLATILE'  # Default for edge node's DataReader
    #qos.presentation.access_scope = 'INSTANCE'
   # qos.presentation.ordered_access = True
    #qos.time_based_filter.minimum_separation = 0
    try:
        participant = DomainParticipant()
        topic = Topic(participant, "crowd_count", CrowdCount)  # Ensure correct topic name and type
        reader = DataReader(participant, topic, qos )

        print("DDS Subscriber started.")
        while True:
            sample = reader.read()  # Directly read without taking samples
            current_time = time.time()

            if sample:
                for msg in sample:
                    device_id = msg.camera_id  # Ensure correct field mapping from IDL
                    crowd_count = msg.count
                    latency = (current_time - msg.timestamp) * 1000  # Calculate latency in ms
                    
                    # Store the latency and timestamp for plotting
                    latencies.append(latency)
                    time_elapsed.append(current_time - start_time)

                    # Save to CSV file directly   
                    if device_id:
                        with lock:
                            save_to_csv(device_id, crowd_count)

                        # Update historical data
                        latest_data["history"].append({"device_id": device_id, "crowd_count": crowd_count})
                    
                    # Calculate throughput every second
                    elapsed_time = current_time - start_time
                    if elapsed_time >= 1.0:
                        throughput = messages_received / elapsed_time
                        throughput_data.append(throughput)
                        messages_received = 0
                        start_time = current_time
                        print(f"Throughput: {throughput:.2f} messages/sec")
                        
                    messages_received += 1
            
            else:
                print("No samples received")
                
    except Exception as e:
        print(f"Error in DDS Subscriber: {e}")

# Function to generate the latency plot using Matplotlib
def create_latency_plot(ax):
    if len(latencies) > 0 and len(time_elapsed) > 0:
        ax[0].clear()  # Clear previous plot in ax1
        # Use the minimum length for both lists
        min_length = min(len(latencies), len(time_elapsed))
        ax[0].plot(time_elapsed[:min_length], latencies[:min_length], color='blue', label='Latency (ms)')
        ax[0].set_xlabel("Time (s)")
        ax[0].set_ylabel("Latency (ms)", color='blue')
        ax[0].set_title("Latency over Time")
        ax[0].legend(loc="upper left")
        ax[0].grid(True)

# Function to generate the throughput plot using Matplotlib
def create_throughput_plot(ax):
    if len(throughput_data) > 0:
        ax[1].clear()  # Clear previous plot in ax2
        # Use only the last n elements of time_elapsed that correspond to the length of throughput_data
        ax[1].plot(time_elapsed[-len(throughput_data):], list(throughput_data), color='green', label='Throughput (msgs/sec)')
        ax[1].set_xlabel("Time (s)")
        ax[1].set_ylabel("Throughput (msgs/sec)", color='green')
        ax[1].set_title("Throughput over Time")
        ax[1].legend(loc="upper left")
        ax[1].grid(True)

# DDS Subscriber in a separate thread
def start_subscriber_thread():
    threading.Thread(target=dds_subscriber, daemon=True).start()

# Main function to run the subscriber and plotting
if __name__ == "__main__":
    start_subscriber_thread()  # Start the DDS subscriber thread

    plt.ion()  # Enable interactive mode to update the plot
    fig, ax = plt.subplots(2, 1, figsize=(10, 10))  # Create two subplots

    # Loop to continuously update and show plots in the main thread
    try:
        while True:
            create_latency_plot(ax)  # Generate the latency plot
            create_throughput_plot(ax)  # Generate the throughput plot
            plt.tight_layout()  # Adjust layout for better spacing
            plt.draw()  # Update the plot
            plt.pause(0.2)  # Pause to allow the plot to update
    except KeyboardInterrupt:
        print("Terminating the program...")