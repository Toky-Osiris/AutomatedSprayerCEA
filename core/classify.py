
import torch
import torch.nn as nn
from torchvision import transforms

class NeuralNet(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes, dropout_rate=0.5):
        super(NeuralNet, self).__init__()
        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(dropout_rate)
        self.fc2 = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        x = self.flatten(x)
        x = self.fc1(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.fc2(x)
        return x

def predict_image(
    image,
    model_path='model_epoch_6.pth',
    input_size=3 * 780 * 780,
    hidden_size=500,
    num_classes=2,
    class_names=[0, 1],
    dropout_rate=0.5,
    device=None
):
    if device is None:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    model = NeuralNet(input_size, hidden_size, num_classes, dropout_rate).to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()

    transform = transforms.Compose([
        transforms.ToTensor()
    ])

    input_tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(input_tensor)
        _, predicted = torch.max(outputs, 1)

    return class_names[predicted.item()]
