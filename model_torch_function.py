import torch
from torchvision import models, transforms
from PIL import Image
#Отдельная функция для определения пневмонии на рентген снимке:

def detect_xray(path):
    # LABEL 1 for pneumonia and LABEL 0 for normal X-RAY
    with Image.open(path) as ip:
        img_tensor = transforms.ToTensor()(ip)

    transform_norm = transforms.Normalize(mean = (0.485, 0.456, 0.406),
                                        std = (0.229, 0.224, 0.225))
    transform_resize = transforms.Resize((224, 224))

    normalized_imgTensor = transform_norm(img_tensor)
    ready_imgTensor = transform_resize(normalized_imgTensor)

    model = models.resnet50(pretrained = False)
    for param in model.parameters():
        param.requires_grad = False
    model.fc = torch.nn.Linear(model.fc.in_features, 2)  
    model.load_state_dict(torch.load('./X-ray-pytorch-trained-model.pth',
                                    map_location = torch.device('cpu')))
    model.eval(); 

    with torch.no_grad():
        prediction = model(ready_imgTensor.unsqueeze(0))
        pred_label = torch.argmax(prediction).item()
    
    return pred_label