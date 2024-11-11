Problems!

- CUDA driver not installed - decided to go with 11.8 (latest is 12.6)
- wrong command executed --device should be cuda not GPU or CUDA

# Windows Install CUDA

https://developer.nvidia.com/cuda-11-8-0-download-archive

# Windows (using chocolatey)
choco install ffmpeg

# Install Rust support
pip install setuptools-rust

# For CUDA 11.8 (more stable)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

pip install git+https://github.com/openai/whisper.git


# verify installation
```
import torch

# Check CUDA availability
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda}")
print(f"PyTorch version: {torch.__version__}")

# Check GPU device
if torch.cuda.is_available():
    print(f"GPU Device: {torch.cuda.get_device_name(0)}")

```


--------------------
# Install PyTorch CPU version
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install Whisper
pip install git+https://github.com/openai/whisper.git

# How to fix error:
```RuntimeError: don't know how to restore data location of torch.storage.UntypedStorage (tagged with CUDA) ``` 

Execution: 
``whisper --device CUDA --output_format txt --language Polish --model large .\agnieszka.m4a`` 


It's wrong parameter ;) yeah took me few min to figure it out

Should be 'cuda' with lower letters, also GPU doesn't work

Proper
``whisper --device cuda --output_format txt --language Polish --model large .\agnieszka.m4a``

Sample error for future generations. Leave a like if it helped.
``` 
C:\Users\xxxx\AppData\Local\pypoetry\Cache\virtualenvs\aidevs3-IgTKuNFy-py3.11\Lib\site-packages\whisper\__init__.py:150: FutureWarning: You are using `torch.load` with `weights_only=False` (the current default value), which us
es the default pickle module implicitly. It is possible to construct malicious pickle data which will execute arbitrary code during unpickling (See https://github.com/pytorch/pytorch/blob/main/SECURITY.md#untrusted-models for mo
re details). In a future release, the default value for `weights_only` will be flipped to `True`. This limits the functions that could be executed during unpickling. Arbitrary objects will no longer be allowed to be loaded via t
his mode unless they are explicitly allowlisted by the user via `torch.serialization.add_safe_globals`. We recommend you start setting `weights_only=True` for any use case where you don't have full control of the loaded file. Please open an issue on GitHub for any issues related to this experimental feature.
  checkpoint = torch.load(fp, map_location=device)
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "C:\Users\xxxx\AppData\Local\pypoetry\Cache\virtualenvs\aidevs3-IgTKuNFy-py3.11\Scripts\whisper.exe\__main__.py", line 7, in <module>
  File "C:\Users\xxxx\AppData\Local\pypoetry\Cache\virtualenvs\aidevs3-IgTKuNFy-py3.11\Lib\site-packages\whisper\transcribe.py", line 593, in cli
    model = load_model(model_name, device=device, download_root=model_dir)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\xxxx\AppData\Local\pypoetry\Cache\virtualenvs\aidevs3-IgTKuNFy-py3.11\Lib\site-packages\whisper\__init__.py", line 150, in load_model
    checkpoint = torch.load(fp, map_location=device)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\xxxx\AppData\Local\pypoetry\Cache\virtualenvs\aidevs3-IgTKuNFy-py3.11\Lib\site-packages\torch\serialization.py", line 1360, in load
    return _load(
           ^^^^^^
  File "C:\Users\xxxx\AppData\Local\pypoetry\Cache\virtualenvs\aidevs3-IgTKuNFy-py3.11\Lib\site-packages\torch\serialization.py", line 1848, in _load
    result = unpickler.load()
             ^^^^^^^^^^^^^^^^
  File "C:\Users\xxxx\AppData\Local\pypoetry\Cache\virtualenvs\aidevs3-IgTKuNFy-py3.11\Lib\site-packages\torch\serialization.py", line 1812, in persistent_load
    typed_storage = load_tensor(
                    ^^^^^^^^^^^^
  File "C:\Users\xxxx\AppData\Local\pypoetry\Cache\virtualenvs\aidevs3-IgTKuNFy-py3.11\Lib\site-packages\torch\serialization.py", line 1784, in load_tensor
    wrap_storage=restore_location(storage, location),
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\xxxx\AppData\Local\pypoetry\Cache\virtualenvs\aidevs3-IgTKuNFy-py3.11\Lib\site-packages\torch\serialization.py", line 1685, in restore_location
    return default_restore_location(storage, map_location)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\xxxx\AppData\Local\pypoetry\Cache\virtualenvs\aidevs3-IgTKuNFy-py3.11\Lib\site-packages\torch\serialization.py", line 604, in default_restore_location
    raise RuntimeError(
RuntimeError: don't know how to restore data location of torch.storage.UntypedStorage (tagged with CUDA)
```