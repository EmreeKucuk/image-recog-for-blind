import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import pyttsx3
import threading
import os
import numpy as np
import speech_recognition as sr
import time
from itertools import cycle
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions

# === Model ve motor yükleme ===
model = MobileNetV2(weights='imagenet')
engine = pyttsx3.init()

# === Görsel tanıma fonksiyonu ===
def classify_image(img_path):
    img = Image.open(img_path).resize((224, 224))
    x = np.array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    preds = model.predict(x)
    label = decode_predictions(preds, top=1)[0][0][1]
    return label

# === Sesli konuşma ve animasyon ===
def speak(text):
    def run():
        animate_wave(True)
        engine.say(text)
        engine.runAndWait()
        animate_wave(False)
    threading.Thread(target=run).start()

# === Dalga animasyonu ===
def animate_wave(state):
    if state:
        wave_label.pack()
        cycle_wave()
    else:
        wave_label.pack_forget()

def cycle_wave():
    def animate():
        for img in wave_images:
            wave_label.configure(image=img)
            wave_label.image = img
            time.sleep(0.1)
            if not wave_label.winfo_ismapped():
                break
    threading.Thread(target=animate).start()

# === Sesli komut dinleme ===
def listen_for_hello():
    r = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        r.adjust_for_ambient_noise(source)
        print("Sesli komut bekleniyor... (Sadece 'hello' komutunu algılar)")
        audio = r.listen(source)
        try:
            command = r.recognize_google(audio).lower()
            if "hello" in command:
                print("Komut algılandı, sesli sorgu etkin.")
                speak("Merhaba, bir nesne sorabilirsiniz.")
                listen_for_question()
        except sr.UnknownValueError:
            print("Anlaşılamadı.")
        listen_for_hello()

def listen_for_question():
    r = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
        try:
            query = r.recognize_google(audio).lower()
            if "what is this" in query or "bu ne" in query:
                if current_label:
                    speak(f"Bu bir {current_label}")
        except sr.UnknownValueError:
            speak("Anlayamadım.")

# === Görsel yükleme ===
def load_and_classify_image():
    global current_label
    file_path = filedialog.askopenfilename(filetypes=[("Görseller", "*.jpg *.png *.jpeg")])
    if not file_path:
        return
    img = Image.open(file_path).resize((250, 250))
    img_tk = ImageTk.PhotoImage(img)
    image_label.config(image=img_tk)
    image_label.image = img_tk
    label.config(text="Nesne tanımlanıyor...")

    def classify():
        label_name = classify_image(file_path)
        current_label = label_name
        label.config(text=f"Nesne: {label_name}")
        speak(label_name)

    threading.Thread(target=classify).start()

# === Arayüz Kurulumu ===
root = tk.Tk()
root.title("Görme Engelliler İçin Nesne Tanıma")
root.geometry("400x500")

btn_load = tk.Button(root, text="Görsel Seç", command=load_and_classify_image)
btn_load.pack(pady=10)

image_label = tk.Label(root)
image_label.pack(pady=10)

label = tk.Label(root, text="", font=("Arial", 14))
label.pack(pady=10)

wave_images = [ImageTk.PhotoImage(Image.open(f"wave/frame{i}.png").resize((100, 50))) for i in range(1, 6)]
wave_label = tk.Label(root)

current_label = None

# === Ses dinleme başlat ===
threading.Thread(target=listen_for_hello).start()

root.mainloop()