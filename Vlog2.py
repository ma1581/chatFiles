import requests
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from environment import env 
import cv2
import time
import shutil

from streamlit.logger import get_logger
logging = get_logger(__name__)


class Vlogger:
    def __init__(self) -> None:
        self.processor= BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        self.model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

    def __process_vid(self,uploaded_file_path):

        frame_sampling_rate = env['frameSamplingRate']
        frame_count = 0

        cap = cv2.VideoCapture(uploaded_file_path)
        text=""
        print("the text is :" + str(uploaded_file_path)) 


        while cap.isOpened():
            print('working')
            ret, frame = cap.read()

            if not ret or frame is None:
                break
            
            # Convert to RGB if needed
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame)
            inputs = self.processor(pil_image, return_tensors="pt")
            
            out = self.model.generate(**inputs)
            text+=self.processor.decode(out[0], skip_special_tokens=True)
            text+='\n'
             
            frame_count+=1
            cap.set(cv2.CAP_PROP_POS_MSEC, frame_count * frame_sampling_rate * 1000)
        return text


        # uploaded files must be mp4 and 
    def vid_to_text(self,uploaded_files):

        text=""
        count=1
        for uploaded_file in uploaded_files:
            text+="image captions of the  video "+ str(count)+':\n'
            text+=self.__process_vid(uploaded_file)
            count+=1
            text+='\n'
        from chat import delete_tempFiles
        # delete_tempFiles(env['uploadedVidsDirectory'])
        return text


        #must be jpg
    def image_to_text(self,uploaded_file):
        pass

