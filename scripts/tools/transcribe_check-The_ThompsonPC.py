#!/usr/bin/env python3
"""Transcribe voice messages to check for authorizations"""
import whisper
import sys

model = whisper.load_model("base")
result = model.transcribe(r"C:\Users\thada\.openclaw\media\inbound\file_20---8c3a33db-3ae9-4095-b8dd-90dc27edb2cc.ogg")
print(result["text"])