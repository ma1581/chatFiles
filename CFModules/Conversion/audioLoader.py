from faster_whisper import WhisperModel

class AudioLoader:

    def __init__(self,loc):
        self.location=loc
    def get_segment(self,deviceType):
        model_size = "large-v3"
    # Run on GPU with FP16
        model = WhisperModel(model_size, device="cpu", compute_type="float32")
        self.segments, self.info = model.transcribe(self.location, beam_size=5)

    def get_text(self):
        data=""
        for i in self.segments:
            data+=i.text
        return data
    # or run on GPU with INT8
    # model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
    # or run on CPU with INT8
    # model = WhisperModel(model_size, device="cpu", compute_type="int8")


#    print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

 #   for segment in segments:
  #      print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))