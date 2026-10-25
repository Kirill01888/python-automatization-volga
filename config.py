"""Общие настройки тестового проекта."""
import os

BASE_URL = os.getenv("BASE_URL", "https://practice-automation.com").rstrip("/")

# Таймаут явных ожиданий, секунды
TIMEOUT = int(os.getenv("TIMEOUT", "10"))

WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
