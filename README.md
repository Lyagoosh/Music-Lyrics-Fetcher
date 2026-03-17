# 🎵 Music Lyrics Fetcher

[![Version](https://img.shields.io/badge/version-3.0.1-blue.svg)](https://github.com/Lyagoosh/Music-Lyrics-Fetcher/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://github.com/Lyagoosh/Music-Lyrics-Fetcher)

A desktop application that automatically adds lyrics to your MP3 and FLAC audio files. Simple, fast, and no API tokens required!

---

<img width="840" height="853" alt="Image" src="https://github.com/user-attachments/assets/7e0ded13-2c45-4ddb-911e-f9671ff8bcd4" />

## 📖 English Description

### 🎯 What is Music Lyrics Fetcher?

Music Lyrics Fetcher is a user-friendly desktop tool designed to automatically find and embed lyrics into your music files. Whether you have MP3 or FLAC files, this program will search multiple online sources to find the correct lyrics and save them directly into the file's metadata.

### ✨ Key Features

- **🎵 Dual Format Support** - Works with both MP3 and FLAC audio files
- **🔍 Multiple Lyrics Sources** - Searches from Lyrics.ovh and Lrclib.net
- **🎚️ Adjustable Priority** - Choose which source to try first
- **💾 Auto-Save Settings** - Remembers your folder and preferences
- **📝 Clean Lyrics** - Preserves all spaces and text structure
- **🎨 User-Friendly Interface** - Simple and intuitive design
- **🚀 Multi-threaded** - Interface stays responsive during search
- **🌐 No API Tokens** - Completely free, no registration needed

### 📋 How It Works

1. **Select Folder** - Choose the directory containing your MP3/FLAC files
2. **Set Priority** - Adjust which lyrics source to try first (optional)
3. **Start Search** - Click the button and watch the magic happen
4. **Enjoy** - Lyrics are automatically saved to your files

The program reads your files' metadata (artist and title), searches for matching lyrics online, and saves them directly into the files. If metadata is missing, it intelligently parses the filename to extract artist and title information.

### 🛠️ Technical Details

- **MP3 Files**: Lyrics are saved in ID3 tags (USLT - Unsychronized Lyrics)
- **FLAC Files**: Lyrics are saved in Vorbis Comments (lyrics field)
- **Sources**: Lyrics.ovh (fast API) and Lrclib.net (supports synchronized lyrics)
- **Settings**: Automatically saved in `settings.json`


## 📖 Описание на русском

### 🎯 Что такое Music Lyrics Fetcher?

Music Lyrics Fetcher — это удобный инструмент для автоматического поиска и добавления текстов песен в ваши музыкальные файлы. Программа поддерживает форматы MP3 и FLAC, ищет тексты в нескольких онлайн-источниках и сохраняет их прямо в метаданные файлов.

### ✨ Основные возможности

- **🎵 Поддержка двух форматов** - Работает с MP3 и FLAC файлами
- **🔍 Несколько источников текстов** - Поиск через Lyrics.ovh и Lrclib.net
- **🎚️ Настраиваемый приоритет** - Выбирайте, какой источник пробовать первым
- **💾 Автосохранение настроек** - Запоминает вашу папку и предпочтения
- **📝 Чистый текст** - Сохраняет все пробелы и структуру текста
- **🎨 Удобный интерфейс** - Простой и интуитивно понятный дизайн
- **🚀 Многопоточность** - Интерфейс не зависает во время поиска
- **🌐 Без API токенов** - Полностью бесплатно, не требует регистрации

### 📋 Как это работает

1. **Выберите папку** - Укажите директорию с вашими MP3/FLAC файлами
2. **Настройте приоритет** - Выберите порядок источников поиска (опционально)
3. **Начните поиск** - Нажмите кнопку и наблюдайте за процессом
4. **Готово** - Тексты автоматически сохраняются в ваши файлы

Программа читает метаданные ваших файлов (исполнитель и название песни), ищет соответствующие тексты в интернете и сохраняет их прямо в файлы. Если метаданные отсутствуют, программа умно анализирует имя файла, чтобы извлечь информацию об исполнителе и названии.

### 🛠️ Технические детали

- **MP3 файлы**: Текст сохраняется в ID3 тегах (USLT - несинхронизированные тексты)
- **FLAC файлы**: Текст сохраняется в Vorbis Comments (поле lyrics)
- **Источники**: Lyrics.ovh (быстрое API) и Lrclib.net (поддержка синхронизированных текстов)
- **Настройки**: Автоматически сохраняются в `settings.json`
