<div align="center">

# ⚡ Universal Video Downloader (UVD)
### *Minimalist Terminal Edition • Powered by yt-dlp & FFmpeg*

[![GitHub License](https://img.shields.io/github/license/faelsete/universal-video-downloader?style=for-the-badge&color=white&labelColor=black)](LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-white?style=for-the-badge&logo=python&logoColor=white&labelColor=black)](https://www.python.org/)
[![yt-dlp](https://img.shields.io/badge/Engine-yt--dlp-white?style=for-the-badge&logo=youtube&logoColor=white&labelColor=black)](https://github.com/yt-dlp/yt-dlp)
[![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-white?style=for-the-badge&labelColor=black)](https://github.com/TomSchimansky/CustomTkinter)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-white?style=for-the-badge&labelColor=black)](CONTRIBUTING.md)

<p align="center">
  <b>The modern, distraction-free desktop application for downloading high-definition videos and studio-grade audio from over 1,800 platforms.</b><br>
  <i>Auto-platform detection • TikTok without watermark • Instagram Reels • YouTube 4K/8K • Facebook • MP3 320kbps • Full Playlists</i>
</p>

[Features](#-key-features) •
[Supported Platforms](#-supported-platforms) •
[Installation](#-quick-start) •
[Usage](#-usage-guide) •
[Architecture](#-tech-stack) •
[Guia em Português](#-guia-rápido-em-português) •
[License](#-license)

---

</div>

## 🖥️ Preview (Terminal UI Aesthetic)

```text
+---------------------------------------------------------------------------------------+
| >_ UNIVERSAL VIDEO DOWNLOADER                                               ● ONLINE  |
| Reconhecimento automático • YouTube • TikTok sem logo • Instagram • Facebook • 1800+  |
+---------------------------------------------------------------------------------------+
| LINK DO VÍDEO OU PLAYLIST:                              [ TIKTOK | SEM MARCA D'ÁGUA ] |
| [ https://www.tiktok.com/@user/video/73918237198273...        ] [  Colar  ] [ Limpar ] |
| ▶ Tutorial Incrível [@creator] 00:45 (Máx: 1080p)                                      |
| [X] Auto-detectar ao copiar link (Ctrl+C)     [ ] Download automático ao colar        |
+---------------------------------------------------------------------------------------+
| TIPO DE DOWNLOAD:   [ 🎬 VÍDEO COMPLETO ]   [ 🎵 APENAS ÁUDIO ]                       |
| RESOLUÇÃO: [ 1080p (Full HD)          ▼ ]   FORMATO:  [ MP4 (Universal)           ▼ ] |
| [X] Embutir capa/thumbnail original          [ ] Baixar legendas embutidas            |
+---------------------------------------------------------------------------------------+
| SALVAR EM: [ C:\Users\faelf\Downloads                                 ] [ Alterar ]   |
|                                                                                       |
|                       [ ⬇  INICIAR DOWNLOAD ]                                         |
| [===================================>                   ] 74.2% • 18.5 MB/s • 00:03   |
+---------------------------------------------------------------------------------------+
| >_ CONSOLE TERMINAL:                                                     [Limpar Log] |
| [11:54:02] [DETECTADO] [ TIKTOK | SEM MARCA D'ÁGUA ]                                  |
| [11:54:03] [FORMATO] VÍDEO: Resolução 1080p | Formato MP4                             |
| [11:54:05] [BAIXANDO] 74.2% | Velocidade: 18.5 MB/s | Restante: 00:03                 |
| [11:54:08] [SUCESSO] Salvo com sucesso em C:\Users\faelf\Downloads\...                |
+---------------------------------------------------------------------------------------+
```

---

## ⚡ Key Features

- 🛡️ **Autonomous Anti-Bot Bypass & Cookie Engine**:
  - Automatically overcomes YouTube's aggressive **BotGuard**, **SABR streaming**, and `n-sig` signature challenges (`Sign in to confirm you're not a bot` & `The page needs to be reloaded`).
  - Auto-detects active browser sessions (`Google Chrome`, `Safari`, `Brave`, `Firefox`, `Microsoft Edge`) without manual setup.
  - Integrates **EJS (Embedded JavaScript)** challenge solver via `deno`/`node` for full 4K/8K stream extraction.
  - Automatically caches valid sessions into `cookies.txt` locally for instant, silent subsequent downloads.
- 🎯 **Automatic Platform Detection**: Paste any URL and UVD instantly recognizes the platform (`YouTube`, `TikTok`, `Instagram`, `Facebook`, `X/Twitter`, `Reddit`, `Twitch`, `Vimeo`, `Kwai`, etc.).
- 🚫 **No Watermark Downloads**:
  - **TikTok**: Directly downloads the clean source video stream without the floating TikTok logo.
  - **Instagram**: Captures original uncompressed Reels and Posts directly from Meta's CDN.
  - **Facebook**: Downloads public Reels and Watch videos in highest HD quality available.
- 🎬 **Video Mode (Up to 4K/8K UHD)**:
  - Resolutions: `Best Available (4K/8K)`, `2160p (4K UHD)`, `1440p (2K QHD)`, `1080p (Full HD)`, `720p (HD)`, `480p (SD)`, and `360p`.
  - Output Formats: `MP4`, `MKV`, `WEBM`, `MOV`.
- 🎵 **Audio-Only Extraction (Studio Quality)**:
  - Formats: `MP3`, `M4A (AAC)`, `WAV (Lossless)`, `FLAC (Lossless Studio)`, `OPUS`.
  - Bitrates: `320 kbps (Maximum Fidelity)`, `256 kbps`, `192 kbps`, `128 kbps`.
- 🖼️ **Embedded Album Art & Metadata**:
  - Automatically embeds original high-resolution thumbnail and ID3 tags directly into MP3 and MP4 files using `mutagen`.
- 📑 **Full Playlist & Channel Support**:
  - Automatically detects playlists and lets you download all videos ordered and numbered with one click.
- 📋 **Smart Clipboard Watcher (Ctrl+C / Cmd+C)**:
  - Copy any video link in your browser and UVD automatically captures and prepares it for download.
- ⚡ **1-Click Auto Download**:
  - Option to trigger download immediately upon link paste.
- 💻 **Terminal Dark Aesthetic**:
  - Clean monochrome dark palette (`#0a0c10` / `#ffffff`) inspired by modern developer terminals. Zero visual clutter or distracting neon colors.
- 📟 **Real-Time Terminal Console**:
  - Embedded live log window showing exact speeds, FFmpeg operations, and progress.

---

## 🌐 Supported Platforms

| Platform | Video Support | Audio Extraction | Special Features |
| :--- | :---: | :---: | :--- |
| **YouTube** | ✅ Up to 4K/8K | ✅ MP3 320k / M4A | Shorts, Playlists, Channels, Subtitles, Anti-Bot Bypass |
| **TikTok** | ✅ Full HD | ✅ Original Audio | **100% No Watermark / Sem Marca d'água** |
| **Instagram** | ✅ Full HD | ✅ High Quality | Reels, Posts, Carousel videos |
| **Facebook** | ✅ 1080p HD | ✅ Clear Audio | Reels, Watch, Public feed videos |
| **Twitter / X** | ✅ Native MP4 | ✅ Audio | Fast direct CDN download |
| **Reddit** | ✅ Audio+Video merged | ✅ Audio | Automatic audio/video sync |
| **Twitch** | ✅ Source 1080p60 | ✅ Audio | Clips and VODs |
| **Vimeo** | ✅ Up to 4K | ✅ Audio | High-bitrate streams |
| **1,800+ Others** | ✅ Universal | ✅ Universal | Powered by `yt-dlp` core |

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+** (Verified up to Python 3.13)
- **FFmpeg** (Required for merging video and audio streams)
  - macOS: `brew install ffmpeg`
  - Windows: `winget install Gyan.FFmpeg` or download from [ffmpeg.org](https://ffmpeg.org/)
- **JavaScript Runtime** (Optional, recommended for YouTube challenge solver):
  - macOS: `brew install deno`
  - Windows: `winget install DenoLand.Deno`

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/faelsete/universal-video-downloader.git
   cd universal-video-downloader
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   - **macOS**: Double-click `iniciar.command` in Finder or run:
     ```bash
     ./iniciar.command
     ```
   - **Windows**: Double-click `iniciar.bat` in Explorer or run:
     ```powershell
     python app.py
     ```
   - **Linux**:
     ```bash
     python3 app.py
     ```

---

## 📖 Usage Guide

1. **Copy a link** from YouTube, TikTok, Instagram, Facebook, or any supported site.
2. If `Auto-detectar ao copiar link (Ctrl+C / Cmd+C)` is enabled, the link will appear in the app automatically. Otherwise, click **Colar**.
3. Choose your desired output:
   - **Vídeo Completo**: Select resolution (4K, 1080p, 720p...) and format (MP4, MKV...).
   - **Apenas Áudio**: Select format (MP3, M4A, WAV...) and bitrate (320 kbps, 256 kbps...).
4. Click **[ ⬇ INICIAR DOWNLOAD ]** and monitor real-time speed in the terminal console.
5. When finished, click **Abrir Pasta** to immediately access your downloaded file!

---

## 🛡️ How the Anti-Bot System Works

YouTube aggressively limits automated downloaders using **BotGuard**, **PO Tokens**, and dynamic **SABR streaming** (often resulting in errors like `Sign in to confirm you're not a bot` or `The page needs to be reloaded`). 

UVD completely eliminates this friction with a 3-layer automated engine:
1. **Auto Browser Detection**: On launch, UVD automatically checks your default installed browser (`Google Chrome`, `Safari`, `Brave`, etc.) and reads your session to authenticate with YouTube.
2. **Remote EJS Challenge Solver**: Configured with `'remote_components': {'ejs:github'}`, allowing `yt-dlp` and `deno` to dynamically resolve YouTube's JavaScript `n-sig` challenges in real time.
3. **Automatic Cookie Caching**: Once cookies are read, UVD saves them locally to `cookies.txt` (ignored by git). Subsequent downloads are instant, silent, and require zero keychain or browser checks.

---

## 🛠️ Tech Stack

- **GUI Framework**: [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) (Modern, dark-themed responsive desktop UI)
- **Download Engine**: [yt-dlp](https://github.com/yt-dlp/yt-dlp) (Industry standard universal video extractor)
- **Media Processing**: [FFmpeg](https://ffmpeg.org/) (High-performance muxing, audio transcoding, and subtitle embedding)
- **Metadata & ID3**: [Mutagen](https://github.com/quodlibet/mutagen) (Tagging and album art embedding)

---

## 🇧🇷 Guia Completo em Português

### Como executar:
- **No macOS**: Dê dois cliques no arquivo `iniciar.command` no Finder. Ele carrega automaticamente o ambiente do Homebrew, detecta o Python e o FFmpeg e abre o app.
- **No Windows**: Dê dois cliques no arquivo `iniciar.bat`.

### Como funciona o Contorno Anti-Bot 100% Automático:
- O YouTube agora exige confirmação de humano para diversos vídeos em alta resolução (4K/8K), gerando bloqueios como *"Sign in to confirm you're not a bot"* ou *"The page needs to be reloaded"*.
- O UVD detecta automaticamente o seu navegador instalado (ex: **Google Chrome** no macOS) e usa a sua sessão para autenticar de forma transparente.
- Após o primeiro acesso, o aplicativo salva uma cópia local segura em `cookies.txt` (protegida pelo `.gitignore`), permitindo que os downloads seguintes aconteçam em **menos de 3 segundos** e sem pedir nenhuma permissão.
- O resolvedor de desafios JavaScript (**EJS**) já vem configurado de fábrica, garantindo compatibilidade total com o novo streaming dinâmico do YouTube.

### Passo a passo para baixar:
1. Abra o aplicativo (`iniciar.command` no Mac ou `iniciar.bat` no Windows).
2. Copie o link do vídeo desejado. Se o monitor de área de transferência estiver ativo, o link já é capturado sozinho!
3. Escolha **Vídeo Completo** (resolução até 4K/8K) ou **Apenas Áudio** (MP3 em 320 kbps com metadados e capa original).
4. Clique em **INICIAR DOWNLOAD** e veja o progresso no console integrado.
5. Ao concluir, clique em **Abrir Pasta** para acessar o arquivo.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/faelsete/universal-video-downloader/issues) or read [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <sub>Built with ❤️ for developers and creators who appreciate minimalist, powerful tools.</sub>
</div>

