import torch


def supports_flash_attention(device_id=0):
    """Check if GPU supports FlashAttention based on compute capability."""
    if not torch.cuda.is_available():
        return False

    major, minor = torch.cuda.get_device_capability(device_id)

    # Ampere (8.x), Ada Lovelace (8.9), or Hopper (9.0)
    is_sm8x = major == 8 and minor >= 0
    is_sm90 = major == 9 and minor == 0

    return is_sm8x or is_sm90


device = torch.cuda.current_device()
gpu_name = torch.cuda.get_device_name(device)
capability = torch.cuda.get_device_capability(device)
print(f"GPU: {gpu_name}")
print(f"Compute Capability: {capability[0]}.{capability[1]}")

print(supports_flash_attention())

# if yes
# Here is the link for the Visual Studio 17.9.0 Professional
# https://download.visualstudio.microsoft.com/download/pr/9a62f360-5491-46e0-b370-3b90f2545317/a56587d8284db240dce61145f1fc2f73984406b6a0440e0dbb59b997bc1823ac/vs_Professional.exe
#
# run - pip install flash-attn --no-build-isolation
# https://huggingface.co/jinaai/jina-embeddings-v3
