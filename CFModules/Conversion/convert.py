#!/usr/bin/env python3
# -- coding: utf-8 --
"""
Created on Tue Nov 11 11:50:45 2023

@author: ninadhegde
"""
import fitz  # PyMuPDF library
from PIL import Image
import pytesseract
# import tkinter as tk
# from tkinter import filedialog
# import speech_recognition as sr
# from moviepy.editor import VideoFileClip, AudioFileClip
# import os
# import vosk


def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file and returns it as a string.

    Parameters:
    - pdf_path (str): Path to the PDF file.

    Returns:
    - str: Extracted text from the PDF.
    """
    text = ""
    try:
        # Open the PDF file
        pdf_document = fitz.open(pdf_path)

        # Iterate through each page
        for page_num in range(pdf_document.page_count):
            # Get the page
            page = pdf_document[page_num]

            # Extract text from the page
            text += page.get_text()

        # Close the PDF file
        pdf_document.close()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")

    return text

def extract_text_from_image(image_path):
    # Open the image file
    img = Image.open(image_path)

    # Use Tesseract to do OCR on the image
    text = pytesseract.image_to_string(img)

    return text

# Example usage
if __name__ == "_main_":
    # Get the file path using a file dialog
    file_path = open_file_dialog()

    if file_path:
        try:
            if file_path.lower().endswith(('.pdf')):
                result_text = extract_text_from_pdf(file_path)
            elif file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                result_text = extract_text_from_image(file_path)
            elif file_path.lower().endswith(('.wav', '.mp3')):
                result_text = extract_text_from_audio(file_path)
            elif file_path.lower().endswith(('.mp4', '.avi', '.mkv', '.mov')):
                result_text = extract_text_from_video(file_path)
            else:
                print("Unsupported file format.")
                exit()

            print("Extracted Text:")
            print(result_text)
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("No file selected. Exiting.")