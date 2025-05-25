import glob
import os
from datetime import datetime
import time
from threading import Thread

import cv2
from sendemail import send_email
import streamlit as st

if 'clicked' not in st.session_state:
    st.session_state.clicked = False

def click_button(arg):
    st.session_state.clicked = arg

def clean_folder():
    images = glob.glob("./images/*")
    for image in images:
        os.remove(image)

st.title("Motion Detector")

if not st.session_state.clicked:
    start_button = st.button("Start Camera", on_click=click_button, icon="🎥", args=[True])
else:
    stop_button = st.button("Stop Camera", icon="🎥", on_click=click_button, args=[False])

streamlit_image = st.image([])

if st.session_state.clicked:
    # Start a Webcam
    print("Starting Camera...")
    video_capture = cv2.VideoCapture(0)  # 0 to use main camera and 1 to use external camera
    time.sleep(1)

    first_frame = None

    status_list = []

    count = 1

    while True:
        status = 0
        date = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
        check, frame = video_capture.read()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.putText(img=frame, text=f"{date}", org=(50, 50),
                    fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale=4, color=(20, 100, 200),
                    thickness=2, lineType=cv2.LINE_AA)

        gray_blurred = cv2.GaussianBlur(gray, (25, 25), 0)
        if first_frame is None:
            first_frame = gray_blurred

        delta_frame = cv2.absdiff(first_frame, gray_blurred)
        thresh_frame = cv2.threshold(delta_frame, 60, 255, cv2.THRESH_BINARY)[1]
        dilated_frame = cv2.dilate(thresh_frame, None, iterations=2)
        # cv2.imshow('My Video', dilated_frame)

        contours, check = cv2.findContours(dilated_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            if cv2.contourArea(contour) < 5000:
                continue
            x, y, w, h = cv2.boundingRect(contour)
            grn_rectangle = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
            if grn_rectangle.any():
                status = 1
                cv2.imwrite(f"images/{count}.jpg", frame)
                count += 1
                all_image_paths = glob.glob("images/*")
                index = int(len(all_image_paths) / 2)
                image_object = all_image_paths[index]

        status_list.append(status)
        status_list = status_list[-2:]

        print(status_list)

        if status_list[0] == 1 and status_list[1] == 0:
            email_thread = Thread(target=send_email, args=(image_object,))
            email_thread.daemon = True
            clean_thread = Thread(target=clean_folder)
            clean_thread.daemon = True

            email_thread.start()
            clean_thread.start()

        # cv2.imshow('Video', frame)
        # key = cv2.waitKey(1)
        # if key == ord("q"):
        #     break

        streamlit_image.image(frame)

    # video_capture.release()

