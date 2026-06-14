$python = 'C:\Python314\python.exe'

Write-Output 'Checking Python packages:'
& $python -m pip list

Write-Output '`nChecking FFmpeg:'
& 'C:\Users\thada\ffmpeg\bin\ffmpeg.exe' -version

Write-Output '`nChecking Ollama:'
& 'C:\Users\thada\AppData\Local\Programs\Ollama\ollama.exe' --version

Write-Output '`nChecking if pyaudio imports:'
& $python -c "try: import pyaudio; print('pyaudio version: ' + pyaudio.__version__); except ImportError: print('pyaudio not installed');"

Write-Output '`nChecking speechbrain:'
& $python -c "try: import speechbrain; print('speechbrain installed'); except ImportError: print('speechbrain not installed');"

Write-Output '`nChecking pyannote.audio:'
& $python -c "try: import pyannote.audio; print('pyannote.audio installed'); except ImportError: print('pyannote.audio not installed');"

Write-Output '`nChecking other packages:'
& $python -c "import torch; print('torch: ' + torch.__version__); import whisper; print('whisper installed'); import numpy; print('numpy: ' + numpy.__version__); import pandas; print('pandas: ' + pandas.__version__); import torchaudio; print('torchaudio: ' + torchaudio.__version__);"