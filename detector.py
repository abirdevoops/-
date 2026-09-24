import numpy as np
import torch
from PIL import ExifTags, Image
from transformers import AutoImageProcessor, AutoModelForImageClassification

MODEL_ID = "rahulshendre/deepfake-detector-model-v1"

def _kind(label):
    s=str(label).lower()
    if any(x in s for x in ["fake","ai","generated","synthetic","deepfake"]): return "fake"
    if any(x in s for x in ["real","human","authentic","natural"]): return "real"
    return "unknown"

class TruthLensDetector:
    def __init__(self, model_id=MODEL_ID):
        self.model_id=model_id
        self.device="cuda" if torch.cuda.is_available() else "cpu"
        self.processor=AutoImageProcessor.from_pretrained(model_id)
        self.model=AutoModelForImageClassification.from_pretrained(model_id)
        self.model.to(self.device).eval()

    @torch.inference_mode()
    def predict(self,image):
        image=image.convert("RGB")
        inputs=self.processor(images=image,return_tensors="pt")
        inputs={k:v.to(self.device) for k,v in inputs.items()}
        probs=torch.softmax(self.model(**inputs).logits[0],dim=-1).cpu().numpy()
        labels=[self.model.config.id2label.get(i,str(i)) for i in range(len(probs))]
        fake=sum(float(p) for p,l in zip(probs,labels) if _kind(l)=="fake")
        real=sum(float(p) for p,l in zip(probs,labels) if _kind(l)=="real")
        if fake==0 and real==0 and len(probs)==2:
            real=float(probs[0]); fake=float(probs[1])
        total=fake+real
        if total: fake,real=fake/total,real/total
        idx=int(np.argmax(probs))
        return {
            "model_name":self.model_id,
            "fake_probability":fake*100,
            "real_probability":real*100,
            "raw_label":labels[idx],
            "model_note":"Probabilistic experimental classifier. This score is not proof of authenticity."
        }

def analyze_metadata(image,image_bytes,filename):
    exif={}
    try:
        for k,v in image.getexif().items():
            exif[ExifTags.TAGS.get(k,str(k))]=str(v)
    except Exception: pass
    ext=filename.rsplit(".",1)[-1].lower() if "." in filename else ""
    size_kb=len(image_bytes)/1024
    return {
        "has_exif":bool(exif),"exif_count":len(exif),"exif":exif,
        "format":ext,"size_kb":size_kb,
        "note":f"Format: {ext.upper() or 'unknown'} • File size: {size_kb:.1f} KB • "
                + ("Some EXIF metadata is present." if exif else "No readable EXIF metadata found.")
    }

def build_explanation(result,metadata):
    fake,real=result["fake_probability"],result["real_probability"]
    if fake>=75:
        status="LIKELY AI-GENERATED"; confidence=round(fake)
        headline="The visual model found a strong synthetic-media signal."
        action="Verify the original source, date and context before sharing."
    elif real>=75:
        status="LIKELY REAL"; confidence=round(real)
        headline="The visual model found a stronger natural-image signal."
        action="This is not proof of authenticity. Verify important claims with the original source."
    else:
        status="NEEDS HUMAN REVIEW"; confidence=round(max(fake,real))
        headline="The signal is not strong enough for a confident classification."
        action="Do not label the image from this score alone. Perform source and context verification."
    reasons=[]
    if fake>=75: reasons.append(f"The visual classifier assigns {fake:.1f}% probability to an AI/deepfake class.")
    elif real>=75: reasons.append(f"The visual classifier assigns {real:.1f}% probability to a real/natural class.")
    else: reasons.append(f"The visual classifier is uncertain ({fake:.1f}% AI vs {real:.1f}% real).")
    if metadata["has_exif"]:
        reasons.append(f"Readable EXIF metadata was found ({metadata['exif_count']} fields); metadata can be edited or removed.")
    else:
        reasons.append("No readable EXIF metadata was found; missing metadata is not evidence that an image is fake.")
    return {"status":status,"confidence":confidence,"headline":headline,"action":action,"reasons":reasons}
