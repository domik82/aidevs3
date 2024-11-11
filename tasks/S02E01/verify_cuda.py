import torch

# Check CUDA availability
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda}")
print(f"PyTorch version: {torch.__version__}")

# Check GPU device
if torch.cuda.is_available():
    print(f"GPU Device: {torch.cuda.get_device_name(0)}")

# import torch
# import whisper
# devices = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
# model = whisper.load_model("large" , device =devices)
