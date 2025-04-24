import tkinter as tk
from tkinter import messagebox
import pyttsx3
import speech_recognition as sr
from PIL import Image, ImageTk
import os
import cv2
from ultralytics import YOLO
import numpy as np

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Load YOLO model (Make sure you have the trained model or path)
model = YOLO('runs/detect/train/weights/best.pt')

# Function to perform object detection on an image
def detect_objects(image_path):
    try:
        detection_results = model.predict(image_path)
        detected_objects = []
        for result in detection_results:
            if result.boxes is not None and len(result.boxes) > 0:
                for box in result.boxes:
                    class_id = int(box.cls[0])
                    detected_objects.append(class_names[class_id])  # Get class names
        return list(set(detected_objects))  # Remove duplicates
    except Exception as e:
        print(f"Error during object detection: {e}")
        return []

# Function to perform speech recognition (voice command)
def recognize_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for command...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio).lower()
        print(f"Recognized command: {command}")
        return command
    except sr.UnknownValueError:
        print("Sorry, I didn't understand that.")
        return None
    except sr.RequestError:
        print("Sorry, there was an issue with the speech recognition service.")
        return None

# Function to speak text using pyttsx3
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to handle the "Start Recognition" button press
def start_recognition():
    # Load image (dummy for now)
    image_path = 'test_image.jpg'  # Replace with actual path
    if not os.path.exists(image_path):
        messagebox.showerror("Error", "Image not found.")
        return
    
    detected_objects = detect_objects(image_path)
    detected_objects_str = ", ".join(detected_objects) if detected_objects else "No objects detected."
    
    # Show the image in the UI
    img = Image.open(image_path)
    img = img.resize((300, 300))
    img_tk = ImageTk.PhotoImage(img)
    image_label.config(image=img_tk)
    image_label.image = img_tk
    
    # Speak out the result
    speak(f"Objects detected: {detected_objects_str}")
    status_label.config(text="Ready for voice command")

# Function to handle the "Ask About Object" voice command
def ask_about_object():
    speak("Please say the object you're looking for.")
    command = recognize_command()
    if command:
        detected_objects = detect_objects('test_image.jpg')  # Replace with actual image path
        if any(obj.lower() in command for obj in detected_objects):
            speak(f"Yes, there is a {command} in the image.")
        else:
            speak(f"No, there is no {command} in the image.")
    else:
        speak("I couldn't hear your command. Please try again.")

# Set up the Tkinter window
root = tk.Tk()
root.title("Object Recognition for Visually Impaired")
root.geometry("500x500")

# Add a label for the image
image_label = tk.Label(root)
image_label.pack(pady=20)

# Add a status label
status_label = tk.Label(root, text="Press 'Start Recognition' to detect objects.")
status_label.pack()

# Add buttons for interactions
start_button = tk.Button(root, text="Start Recognition", command=start_recognition)
start_button.pack(pady=10)

ask_button = tk.Button(root, text="Ask About Object", command=ask_about_object)
ask_button.pack(pady=10)

# Run the Tkinter main loop
root.mainloop()
