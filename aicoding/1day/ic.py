import torch
from datasets import load_dataset
from transformers import EfficientNetImageProcessor, EfficientNetForImageClassification

#모델 로딩
dataset = load_dataset("huggingface/cats-image")
image = dataset["test"]["image"][0]


# dataset = load_dataset("huggingface/cats-image")
# print(dataset)

#입력 데이터 로딩 및 전처리
preprocessor = EfficientNetImageProcessor.from_pretrained("google/efficientnet-b0")
model = EfficientNetForImageClassification.from_pretrained("google/efficientnet-b0")


#모델 실행
inputs = preprocessor(image, return_tensors="pt")

with torch.no_grad():
    logits = model(**inputs).logits

#출력 후 처리
# model predicts one of the 1000 ImageNet classes
predicted_label = logits.argmax(-1).item()
print(model.config.id2label[predicted_label]),
