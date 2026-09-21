"""
Universal Video Downloader (UVD) • Terminal Edition
Interface Gráfica Desktop Minimalista - Tema Escuro / Terminal
Controle Completo: Vídeo vs Só Áudio, Resoluções (4K a 360p), Formatos (MP4, MKV, MP3, WAV...),
Bitrates, Legendas, Capa Embutida, Playlists, Auto-detecção e Clipboard Monitor.
"""

import os
import sys
import time
import threading
import subprocess
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

from downloader_engine import DownloaderEngine, DownloadCancelledException
from ui_theme import (
    COLOR_BG_DARK,
    COLOR_PANEL_BG,
    COLOR_PANEL_BORDER,
    COLOR_INPUT_BG,
    COLOR_INPUT_BORDER,
    COLOR_TEXT_WHITE,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_DIM,
    COLOR_BTN_PRIMARY_BG,
    COLOR_BTN_PRIMARY_TEXT,
    COLOR_BTN_PRIMARY_HOVER,
    COLOR_BTN_SEC_BG,
    COLOR_BTN_SEC_BORDER,
    COLOR_BTN_SEC_TEXT,
    COLOR_BTN_SEC_HOVER,
    COLOR_ACCENT_GREEN,
    COLOR_ACCENT_RED,
    COLOR_PROGRESS_BAR,
    COLOR_PROGRESS_TRACK,
    FONT_FAMILY_MONO,
    FONT_FAMILY_UI
)

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")


class UniversalDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuração da Janela Principal
        self.title("Universal Video Downloader • Terminal Edition")
        self.geometry("900x840")
        self.minsize(820, 720)
        self.configure(fg_color=COLOR_BG_DARK)

        # Motor e Estados
        self.engine = DownloaderEngine(log_callback=self._queue_log)
        self.is_downloading = False
        self.last_clipboard_text = ""
        self.current_fetching_url = ""

        # Variáveis de Configuração
        default_downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        self.download_dir_var = tk.StringVar(value=default_downloads)
        
        self.url_var = tk.StringVar()
        self.url_var.trace_add("write", self._on_url_changed)

        # Seleção de Mídia: "video" ou "audio"
        self.media_type_var = tk.StringVar(value="video")

        # Opções de Vídeo
        self.video_res_var = tk.StringVar(value="Melhor Disponível (Até 4K / 8K)")
        self.video_format_var = tk.StringVar(value="MP4 (Universal)")

        # Opções de Áudio
        self.audio_format_var = tk.StringVar(value="MP3 (Padrão Universal)")
        self.audio_bitrate_var = tk.StringVar(value="320 kbps (Máxima Fidelidade)")

        # Opções Extras
        self.embed_thumb_var = tk.BooleanVar(value=True)
        self.subtitles_var = tk.BooleanVar(value=False)
        self.auto_download_var = tk.BooleanVar(value=False)
        self.auto_clipboard_var = tk.BooleanVar(value=False)
        self.download_full_playlist_var = tk.BooleanVar(value=True)

        # Mapeamentos Técnicos
        self.res_map = {
            "Melhor Disponível (Até 4K / 8K)": "best",
            "2160p (4K Ultra HD)": "2160p",
            "1440p (2K QHD)": "1440p",
            "1080p (Full HD)": "1080p",
            "720p (HD)": "720p",
            "480p (SD)": "480p",
            "360p (Econômico)": "360p",
        }
        self.v_format_map = {
            "MP4 (Universal)": "mp4",
            "MKV (Alta Qualidade)": "mkv",
            "WEBM (Padrão Web)": "webm",
            "MOV (QuickTime)": "mov",
        }
        self.a_format_map = {
            "MP3 (Padrão Universal)": "mp3",
            "M4A (AAC Original)": "m4a",
            "WAV (Lossless Sem Perdas)": "wav",
            "FLAC (Lossless Studio)": "flac",
            "OPUS (Web Áudio)": "opus",
        }
        self.a_bitrate_map = {
            "320 kbps (Máxima Fidelidade)": "320",
            "256 kbps (Muito Alta)": "256",
            "192 kbps (Padrão Estúdio)": "192",
            "128 kbps (Econômico)": "128",
        }

        # Constrói a Interface
        self._build_ui()

        # Fila de Log e Clipboard Watcher
        self.log_queue = []
        self._process_log_queue()
        self._start_clipboard_watcher()

        # Mensagem inicial no terminal
        self.append_terminal_log("=" * 66)
        self.append_terminal_log("[SISTEMA] Universal Video Downloader pronto.")
        self.append_terminal_log("[MOTOR] yt-dlp + FFmpeg + Mutagen integrados.")
        self.append_terminal_log("[REDE] Reconhecimento ativo: YouTube, TikTok sem logo, Insta, Facebook...")
        self.append_terminal_log("=" * 66)

    def _build_ui(self):
        main_frame = ctk.CTkFrame(self, fg_color=COLOR_BG_DARK)
        main_frame.pack(fill="both", expand=True, padx=20, pady=16)

        # --- 1. CABEÇALHO ---
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))

        title_label = ctk.CTkLabel(
            header_frame,
            text=">_ UNIVERSAL VIDEO DOWNLOADER",
            font=(FONT_FAMILY_MONO, 20, "bold"),
            text_color=COLOR_TEXT_WHITE
        )
        title_label.pack(side="left")

        self.status_indicator = ctk.CTkLabel(
            header_frame,
            text="● ONLINE",
            font=(FONT_FAMILY_MONO, 12, "bold"),
            text_color=COLOR_ACCENT_GREEN
        )
        self.status_indicator.pack(side="right")

        # --- 2. CARD DE ENTRADA & AUTO-RECONHECIMENTO ---
        input_card = ctk.CTkFrame(
            main_frame,
            fg_color=COLOR_PANEL_BG,
            border_color=COLOR_PANEL_BORDER,
            border_width=1,
            corner_radius=6
        )
        input_card.pack(fill="x", pady=(0, 10))

        badge_row = ctk.CTkFrame(input_card, fg_color="transparent")
        badge_row.pack(fill="x", padx=14, pady=(10, 4))

        lbl_url_title = ctk.CTkLabel(
            badge_row,
            text="LINK DO VÍDEO OU PLAYLIST:",
            font=(FONT_FAMILY_MONO, 11, "bold"),
            text_color=COLOR_TEXT_MUTED
        )
        lbl_url_title.pack(side="left")

        self.platform_badge = ctk.CTkLabel(
            badge_row,
            text="[ AGUARDANDO LINK ]",
            font=(FONT_FAMILY_MONO, 11, "bold"),
            text_color=COLOR_TEXT_WHITE,
            fg_color=COLOR_BTN_SEC_BG,
            corner_radius=4,
            padx=8,
            pady=2
        )
        self.platform_badge.pack(side="right")

        # Linha de entrada e botões
        entry_row = ctk.CTkFrame(input_card, fg_color="transparent")
        entry_row.pack(fill="x", padx=14, pady=(0, 6))

        self.url_entry = ctk.CTkEntry(
            entry_row,
            textvariable=self.url_var,
            placeholder_text="Cole o link aqui (YouTube, TikTok, Instagram, Facebook, X, etc.)",
            font=(FONT_FAMILY_MONO, 12),
            fg_color=COLOR_INPUT_BG,
            border_color=COLOR_INPUT_BORDER,
            border_width=1,
            text_color=COLOR_TEXT_WHITE,
            placeholder_text_color=COLOR_TEXT_DIM,
            height=38,
            corner_radius=4
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        btn_paste = ctk.CTkButton(
            entry_row,
            text="Colar",
            command=self._paste_clipboard,
            font=(FONT_FAMILY_UI, 12, "bold"),
            fg_color=COLOR_BTN_SEC_BG,
            border_color=COLOR_BTN_SEC_BORDER,
            border_width=1,
            text_color=COLOR_BTN_SEC_TEXT,
            hover_color=COLOR_BTN_SEC_HOVER,
            width=75,
            height=38,
            corner_radius=4
        )
        btn_paste.pack(side="left", padx=(0, 6))

        btn_clear = ctk.CTkButton(
            entry_row,
            text="Limpar",
            command=self._clear_url,
            font=(FONT_FAMILY_UI, 12),
            fg_color=COLOR_BTN_SEC_BG,
            border_color=COLOR_BTN_SEC_BORDER,
            border_width=1,
            text_color=COLOR_TEXT_MUTED,
            hover_color=COLOR_BTN_SEC_HOVER,
            width=65,
            height=38,
            corner_radius=4
        )
        btn_clear.pack(side="left")

        # Prévia rápida de metadados
        self.preview_frame = ctk.CTkFrame(input_card, fg_color=COLOR_INPUT_BG, corner_radius=4)
        preview_inner = ctk.CTkFrame(self.preview_frame, fg_color="transparent")
        preview_inner.pack(fill="x", padx=10, pady=5)

        self.lbl_preview_text = ctk.CTkLabel(
            preview_inner,
            text="> Aguardando leitura do vídeo...",
            font=(FONT_FAMILY_MONO, 11),
            text_color=COLOR_TEXT_MUTED,
            anchor="w"
        )
        self.lbl_preview_text.pack(fill="x")

        # Painel para Playlists
        self.playlist_panel = ctk.CTkFrame(input_card, fg_color=COLOR_INPUT_BG, corner_radius=4)
        playlist_inner = ctk.CTkFrame(self.playlist_panel, fg_color="transparent")
        playlist_inner.pack(fill="x", padx=12, pady=6)

        playlist_lbl = ctk.CTkLabel(
            playlist_inner,
            text="[ CONTEÚDO DE PLAYLIST DETECTADO ]",
            font=(FONT_FAMILY_MONO, 11, "bold"),
            text_color=COLOR_TEXT_WHITE
        )
        playlist_lbl.pack(side="left", padx=(0, 15))

        self.chk_playlist = ctk.CTkCheckBox(
            playlist_inner,
            text="Baixar Playlist Completa (todos os vídeos)",
            variable=self.download_full_playlist_var,
            font=(FONT_FAMILY_UI, 11),
            text_color=COLOR_TEXT_WHITE,
            fg_color=COLOR_TEXT_WHITE,
            checkmark_color=COLOR_BG_DARK,
            border_color=COLOR_INPUT_BORDER,
            border_width=1,
            corner_radius=3,
            checkbox_height=18,
            checkbox_width=18
        )
        self.chk_playlist.pack(side="left")

        # Automações (Clipboard + Auto-download)
        options_toggle_row = ctk.CTkFrame(input_card, fg_color="transparent")
        options_toggle_row.pack(fill="x", padx=14, pady=(6, 10))

        self.chk_clipboard = ctk.CTkCheckBox(
            options_toggle_row,
            text="Auto-detectar ao copiar link (Ctrl+C)",
            variable=self.auto_clipboard_var,
            command=self._on_toggle_clipboard_monitor,
            font=(FONT_FAMILY_UI, 11),
            text_color=COLOR_TEXT_MUTED,
            fg_color=COLOR_TEXT_WHITE,
            checkmark_color=COLOR_BG_DARK,
            border_color=COLOR_INPUT_BORDER,
            border_width=1,
            corner_radius=3,
            checkbox_height=18,
            checkbox_width=18
        )
        self.chk_clipboard.pack(side="left", padx=(0, 20))

        self.chk_autodownload = ctk.CTkCheckBox(
            options_toggle_row,
            text="Download automático ao colar",
            variable=self.auto_download_var,
            font=(FONT_FAMILY_UI, 11),
            text_color=COLOR_TEXT_MUTED,
            fg_color=COLOR_TEXT_WHITE,
            checkmark_color=COLOR_BG_DARK,
            border_color=COLOR_INPUT_BORDER,
            border_width=1,
            corner_radius=3,
            checkbox_height=18,
            checkbox_width=18
        )
        self.chk_autodownload.pack(side="left")

        # --- 3. SELEÇÃO DE FORMATO, RESOLUÇÃO & TIPO DE MÍDIA ---
        media_card = ctk.CTkFrame(
            main_frame,
            fg_color=COLOR_PANEL_BG,
            border_color=COLOR_PANEL_BORDER,
            border_width=1,
            corner_radius=6
        )
        media_card.pack(fill="x", pady=(0, 10))

        media_card_inner = ctk.CTkFrame(media_card, fg_color="transparent")
        media_card_inner.pack(fill="x", padx=14, pady=10)

        # Barra de Alternância: Vídeo vs Só Áudio
        mode_row = ctk.CTkFrame(media_card_inner, fg_color="transparent")
        mode_row.pack(fill="x", pady=(0, 10))

        lbl_media_mode = ctk.CTkLabel(
            mode_row,
            text="TIPO DE DOWNLOAD:",
            font=(FONT_FAMILY_MONO, 11, "bold"),
            text_color=COLOR_TEXT_MUTED
        )
        lbl_media_mode.pack(side="left", padx=(0, 15))

        self.btn_mode_video = ctk.CTkButton(
            mode_row,
            text="🎬  VÍDEO COMPLETO",
            command=lambda: self._set_media_type("video"),
            font=(FONT_FAMILY_MONO, 12, "bold"),
            fg_color=COLOR_BTN_PRIMARY_BG,
            text_color=COLOR_BTN_PRIMARY_TEXT,
            hover_color=COLOR_BTN_PRIMARY_HOVER,
            width=170,
            height=34,
            corner_radius=4
        )
        self.btn_mode_video.pack(side="left", padx=(0, 8))

        self.btn_mode_audio = ctk.CTkButton(
            mode_row,
            text="🎵  APENAS ÁUDIO",
            command=lambda: self._set_media_type("audio"),
            font=(FONT_FAMILY_MONO, 12, "bold"),
            fg_color=COLOR_BTN_SEC_BG,
            text_color=COLOR_BTN_SEC_TEXT,
            hover_color=COLOR_BTN_SEC_HOVER,
            border_color=COLOR_BTN_SEC_BORDER,
            border_width=1,
            width=160,
            height=34,
            corner_radius=4
        )
        self.btn_mode_audio.pack(side="left")

        # Container para os Controles Dinâmicos (Vídeo vs Áudio)
        self.controls_container = ctk.CTkFrame(media_card_inner, fg_color="transparent")
        self.controls_container.pack(fill="x", pady=(0, 8))

        # --- PAINEL DE VÍDEO (Resolução + Formato de Vídeo) ---
        self.video_panel = ctk.CTkFrame(self.controls_container, fg_color="transparent")
        
        # Coluna Resolução
        v_left = ctk.CTkFrame(self.video_panel, fg_color="transparent")
        v_left.pack(side="left", fill="x", expand=True, padx=(0, 8))

        lbl_res = ctk.CTkLabel(
            v_left,
            text="RESOLUÇÃO DO VÍDEO:",
            font=(FONT_FAMILY_MONO, 11, "bold"),
            text_color=COLOR_TEXT_MUTED,
            anchor="w"
        )
        lbl_res.pack(fill="x", pady=(0, 4))

        self.opt_video_res = ctk.CTkOptionMenu(
            v_left,
            values=list(self.res_map.keys()),
            variable=self.video_res_var,
            font=(FONT_FAMILY_UI, 12),
            fg_color=COLOR_INPUT_BG,
            button_color=COLOR_BTN_SEC_BG,
            button_hover_color=COLOR_BTN_SEC_HOVER,
            dropdown_fg_color=COLOR_PANEL_BG,
            dropdown_text_color=COLOR_TEXT_WHITE,
            text_color=COLOR_TEXT_WHITE,
            height=36,
            corner_radius=4
        )
        self.opt_video_res.pack(fill="x")

        # Coluna Formato de Vídeo
        v_right = ctk.CTkFrame(self.video_panel, fg_color="transparent")
        v_right.pack(side="left", fill="x", expand=True, padx=(8, 0))

        lbl_v_format = ctk.CTkLabel(
            v_right,
            text="FORMATO DO ARQUIVO (CONTAINER):",
            font=(FONT_FAMILY_MONO, 11, "bold"),
            text_color=COLOR_TEXT_MUTED,
            anchor="w"
        )
        lbl_v_format.pack(fill="x", pady=(0, 4))

        self.opt_video_fmt = ctk.CTkOptionMenu(
            v_right,
            values=list(self.v_format_map.keys()),
            variable=self.video_format_var,
            font=(FONT_FAMILY_UI, 12),
            fg_color=COLOR_INPUT_BG,
            button_color=COLOR_BTN_SEC_BG,
            button_hover_color=COLOR_BTN_SEC_HOVER,
            dropdown_fg_color=COLOR_PANEL_BG,
            dropdown_text_color=COLOR_TEXT_WHITE,
            text_color=COLOR_TEXT_WHITE,
            height=36,
            corner_radius=4
        )
        self.opt_video_fmt.pack(fill="x")

        # --- PAINEL DE SÓ ÁUDIO (Formato + Bitrate) ---
        self.audio_panel = ctk.CTkFrame(self.controls_container, fg_color="transparent")

        # Coluna Formato de Áudio
        a_left = ctk.CTkFrame(self.audio_panel, fg_color="transparent")
        a_left.pack(side="left", fill="x", expand=True, padx=(0, 8))

        lbl_a_fmt = ctk.CTkLabel(
            a_left,
            text="FORMATO DO ÁUDIO:",
            font=(FONT_FAMILY_MONO, 11, "bold"),
            text_color=COLOR_TEXT_MUTED,
            anchor="w"
        )
        lbl_a_fmt.pack(fill="x", pady=(0, 4))

        self.opt_audio_fmt = ctk.CTkOptionMenu(
            a_left,
            values=list(self.a_format_map.keys()),
            variable=self.audio_format_var,
            font=(FONT_FAMILY_UI, 12),
            fg_color=COLOR_INPUT_BG,
            button_color=COLOR_BTN_SEC_BG,
            button_hover_color=COLOR_BTN_SEC_HOVER,
            dropdown_fg_color=COLOR_PANEL_BG,
            dropdown_text_color=COLOR_TEXT_WHITE,
            text_color=COLOR_TEXT_WHITE,
            height=36,
            corner_radius=4
        )
        self.opt_audio_fmt.pack(fill="x")

        # Coluna Bitrate / Qualidade
        a_right = ctk.CTkFrame(self.audio_panel, fg_color="transparent")
        a_right.pack(side="left", fill="x", expand=True, padx=(8, 0))

        lbl_bitrate = ctk.CTkLabel(
            a_right,
            text="QUALIDADE / TAXA DE BITS (BITRATE):",
            font=(FONT_FAMILY_MONO, 11, "bold"),
            text_color=COLOR_TEXT_MUTED,
            anchor="w"
        )
        lbl_bitrate.pack(fill="x", pady=(0, 4))

        self.opt_audio_bitrate = ctk.CTkOptionMenu(
            a_right,
            values=list(self.a_bitrate_map.keys()),
            variable=self.audio_bitrate_var,
            font=(FONT_FAMILY_UI, 12),
            fg_color=COLOR_INPUT_BG,
            button_color=COLOR_BTN_SEC_BG,
            button_hover_color=COLOR_BTN_SEC_HOVER,
            dropdown_fg_color=COLOR_PANEL_BG,
            dropdown_text_color=COLOR_TEXT_WHITE,
            text_color=COLOR_TEXT_WHITE,
            height=36,
            corner_radius=4
        )
        self.opt_audio_bitrate.pack(fill="x")

        # Exibe o painel inicial (Vídeo)
        self.video_panel.pack(fill="x")

        # Opções Extras (Capa + Legendas)
        extra_opts_row = ctk.CTkFrame(media_card_inner, fg_color="transparent")
        extra_opts_row.pack(fill="x", pady=(6, 2))

        self.chk_embed_thumb = ctk.CTkCheckBox(
            extra_opts_row,
            text="Embutir capa/thumbnail original no arquivo",
            variable=self.embed_thumb_var,
            font=(FONT_FAMILY_UI, 11),
            text_color=COLOR_TEXT_MUTED,
            fg_color=COLOR_TEXT_WHITE,
            checkmark_color=COLOR_BG_DARK,
            border_color=COLOR_INPUT_BORDER,
            border_width=1,
            corner_radius=3,
            checkbox_height=18,
            checkbox_width=18
        )
        self.chk_embed_thumb.pack(side="left", padx=(0, 20))

        self.chk_subs = ctk.CTkCheckBox(
            extra_opts_row,
            text="Baixar e embutir legendas (se disponíveis)",
            variable=self.subtitles_var,
            font=(FONT_FAMILY_UI, 11),
            text_color=COLOR_TEXT_MUTED,
            fg_color=COLOR_TEXT_WHITE,
            checkmark_color=COLOR_BG_DARK,
            border_color=COLOR_INPUT_BORDER,
            border_width=1,
            corner_radius=3,
            checkbox_height=18,
            checkbox_width=18
        )
        self.chk_subs.pack(side="left")

        # --- 4. PASTA DE DESTINO ---
        dest_card = ctk.CTkFrame(
            main_frame,
            fg_color=COLOR_PANEL_BG,
            border_color=COLOR_PANEL_BORDER,
            border_width=1,
            corner_radius=6
        )
        dest_card.pack(fill="x", pady=(0, 10))

        dest_inner = ctk.CTkFrame(dest_card, fg_color="transparent")
        dest_inner.pack(fill="x", padx=14, pady=8)

        lbl_dest = ctk.CTkLabel(
            dest_inner,
            text="SALVAR EM:",
            font=(FONT_FAMILY_MONO, 11, "bold"),
            text_color=COLOR_TEXT_MUTED,
            anchor="w"
        )
        lbl_dest.pack(side="left", padx=(0, 10))

        self.dest_entry = ctk.CTkEntry(
            dest_inner,
            textvariable=self.download_dir_var,
            font=(FONT_FAMILY_MONO, 11),
            fg_color=COLOR_INPUT_BG,
            border_color=COLOR_INPUT_BORDER,
            border_width=1,
            text_color=COLOR_TEXT_WHITE,
            height=34,
            corner_radius=4
        )
        self.dest_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        btn_browse = ctk.CTkButton(
            dest_inner,
            text="Alterar",
            command=self._choose_directory,
            font=(FONT_FAMILY_UI, 11),
            fg_color=COLOR_BTN_SEC_BG,
            border_color=COLOR_BTN_SEC_BORDER,
            border_width=1,
            text_color=COLOR_BTN_SEC_TEXT,
            hover_color=COLOR_BTN_SEC_HOVER,
            width=65,
            height=34,
            corner_radius=4
        )
        btn_browse.pack(side="left", padx=(0, 6))

        btn_open_folder = ctk.CTkButton(
            dest_inner,
            text="Abrir Pasta",
            command=self._open_download_folder,
            font=(FONT_FAMILY_UI, 11),
            fg_color=COLOR_BTN_SEC_BG,
            border_color=COLOR_BTN_SEC_BORDER,
            border_width=1,
            text_color=COLOR_BTN_SEC_TEXT,
            hover_color=COLOR_BTN_SEC_HOVER,
            width=85,
            height=34,
            corner_radius=4
        )
        btn_open_folder.pack(side="left")

        # --- 5. AÇÃO & BARRA DE PROGRESSO ---
        action_card = ctk.CTkFrame(
            main_frame,
            fg_color=COLOR_PANEL_BG,
            border_color=COLOR_PANEL_BORDER,
            border_width=1,
            corner_radius=6
        )
        action_card.pack(fill="x", pady=(0, 10))

        action_inner = ctk.CTkFrame(action_card, fg_color="transparent")
        action_inner.pack(fill="x", padx=14, pady=10)

        self.btn_download = ctk.CTkButton(
            action_inner,
            text="⬇   INICIAR DOWNLOAD",
            command=self._on_download_click,
            font=(FONT_FAMILY_MONO, 14, "bold"),
            fg_color=COLOR_BTN_PRIMARY_BG,
            text_color=COLOR_BTN_PRIMARY_TEXT,
            hover_color=COLOR_BTN_PRIMARY_HOVER,
            height=44,
            corner_radius=4
        )
        self.btn_download.pack(fill="x", pady=(0, 8))

        self.progress_bar = ctk.CTkProgressBar(
            action_inner,
            height=8,
            fg_color=COLOR_PROGRESS_TRACK,
            progress_color=COLOR_PROGRESS_BAR,
            corner_radius=2
        )
        self.progress_bar.pack(fill="x", pady=(0, 6))
        self.progress_bar.set(0)

        progress_info_row = ctk.CTkFrame(action_inner, fg_color="transparent")
        progress_info_row.pack(fill="x")

        self.lbl_progress_status = ctk.CTkLabel(
            progress_info_row,
            text="Pronto para baixar.",
            font=(FONT_FAMILY_MONO, 11),
            text_color=COLOR_TEXT_MUTED,
            anchor="w"
        )
        self.lbl_progress_status.pack(side="left", fill="x", expand=True)

        self.lbl_progress_metrics = ctk.CTkLabel(
            progress_info_row,
            text="0% • -- MB/s • ETA: --:--",
            font=(FONT_FAMILY_MONO, 11),
            text_color=COLOR_TEXT_WHITE,
            anchor="e"
        )
        self.lbl_progress_metrics.pack(side="right")

        # --- 6. TERMINAL DE LOGS ---
        terminal_header = ctk.CTkFrame(main_frame, fg_color="transparent")
        terminal_header.pack(fill="x", pady=(2, 4))

        lbl_term = ctk.CTkLabel(
            terminal_header,
            text=">_ CONSOLE TERMINAL:",
            font=(FONT_FAMILY_MONO, 11, "bold"),
            text_color=COLOR_TEXT_MUTED
        )
        lbl_term.pack(side="left")

        btn_clear_term = ctk.CTkButton(
            terminal_header,
            text="Limpar Log",
            command=self._clear_terminal,
            font=(FONT_FAMILY_MONO, 10),
            fg_color="transparent",
            text_color=COLOR_TEXT_MUTED,
            hover_color=COLOR_BTN_SEC_BG,
            height=20,
            width=70
        )
        btn_clear_term.pack(side="right")

        self.terminal_box = ctk.CTkTextbox(
            main_frame,
            fg_color=COLOR_INPUT_BG,
            text_color="#e6edf3",
            font=(FONT_FAMILY_MONO, 11),
            border_color=COLOR_PANEL_BORDER,
            border_width=1,
            corner_radius=4,
            wrap="word"
        )
        self.terminal_box.pack(fill="both", expand=True)

    # --- CONTROLE DE MÍDIA (VÍDEO vs ÁUDIO) ---
    def _set_media_type(self, media_type: str):
        self.media_type_var.set(media_type)
        if media_type == "video":
            self.btn_mode_video.configure(
                fg_color=COLOR_BTN_PRIMARY_BG,
                text_color=COLOR_BTN_PRIMARY_TEXT,
                border_width=0
            )
            self.btn_mode_audio.configure(
                fg_color=COLOR_BTN_SEC_BG,
                text_color=COLOR_BTN_SEC_TEXT,
                border_width=1
            )
            self.audio_panel.pack_forget()
            self.video_panel.pack(fill="x")
            self.append_terminal_log("[MODO] Selecionado: VÍDEO COMPLETO (com áudio e imagem).")
        else:
            self.btn_mode_audio.configure(
                fg_color=COLOR_BTN_PRIMARY_BG,
                text_color=COLOR_BTN_PRIMARY_TEXT,
                border_width=0
            )
            self.btn_mode_video.configure(
                fg_color=COLOR_BTN_SEC_BG,
                text_color=COLOR_BTN_SEC_TEXT,
                border_width=1
            )
            self.video_panel.pack_forget()
            self.audio_panel.pack(fill="x")
            self.append_terminal_log("[MODO] Selecionado: APENAS ÁUDIO (extração MP3/M4A/WAV).")

    # --- LOGS & TERMINAL ---
    def _queue_log(self, message: str):
        now = datetime.now().strftime("%H:%M:%S")
        self.log_queue.append(f"[{now}] {message}")

    def _process_log_queue(self):
        while self.log_queue:
            msg = self.log_queue.pop(0)
            self.terminal_box.insert("end", msg + "\n")
            self.terminal_box.see("end")
        self.after(80, self._process_log_queue)

    def append_terminal_log(self, message: str):
        self._queue_log(message)

    def _clear_terminal(self):
        self.terminal_box.delete("1.0", "end")
        self.append_terminal_log("[TERMINAL] Histórico limpo.")

    # --- ENTRADA & CLIPBOARD ---
    def _paste_clipboard(self):
        try:
            content = self.clipboard_get().strip()
            if content:
                self.url_var.set(content)
                self.append_terminal_log(f"[COLADO] {content[:60]}...")
        except Exception:
            pass

    def _clear_url(self):
        self.url_var.set("")
        self.platform_badge.configure(text="[ AGUARDANDO LINK ]", text_color=COLOR_TEXT_WHITE)
        self.playlist_panel.pack_forget()
        self.preview_frame.pack_forget()
        self.progress_bar.set(0)
        self.lbl_progress_status.configure(text="Pronto para baixar.")
        self.lbl_progress_metrics.configure(text="0% • -- MB/s • ETA: --:--")

    def _on_url_changed(self, *args):
        url = self.url_var.get().strip()
        if not url:
            self.platform_badge.configure(text="[ AGUARDANDO LINK ]", text_color=COLOR_TEXT_WHITE)
            self.playlist_panel.pack_forget()
            self.preview_frame.pack_forget()
            return

        info = DownloaderEngine.identify_platform(url)
        self.platform_badge.configure(text=info['badge'], text_color=COLOR_TEXT_WHITE)

        if info.get('is_playlist_candidate'):
            self.playlist_panel.pack(fill="x", padx=14, pady=(0, 8))
        else:
            self.playlist_panel.pack_forget()

        # Inicia busca assíncrona de metadados para prévia
        if url.startswith(("http://", "https://")) and url != self.current_fetching_url:
            self.current_fetching_url = url
            self.preview_frame.pack(fill="x", padx=14, pady=(0, 6))
            self.lbl_preview_text.configure(text="> Consultando metadados do vídeo...")
            threading.Thread(target=self._fetch_metadata_worker, args=(url,), daemon=True).start()

        # Disparo automático se configurado
        if self.auto_download_var.get() and url.startswith(("http://", "https://")) and not self.is_downloading:
            self.after(500, self._trigger_auto_download)

    def _fetch_metadata_worker(self, url: str):
        meta = self.engine.fetch_quick_info(url)
        if meta and self.url_var.get().strip() == url:
            details = meta.get('details', '')
            self.after(0, lambda: self.lbl_preview_text.configure(text=f"▶ {details}"))
            self.after(0, lambda: self.append_terminal_log(f"[INFO] {details}"))

    def _trigger_auto_download(self):
        if not self.is_downloading and self.url_var.get().strip().startswith(("http://", "https://")):
            self.append_terminal_log("[AUTO-DOWNLOAD] Iniciando download automático...")
            self._start_download()

    def _start_clipboard_watcher(self):
        def watcher():
            while True:
                if self.auto_clipboard_var.get() and not self.is_downloading:
                    try:
                        content = self.clipboard_get().strip()
                        if (
                            content.startswith(("http://", "https://"))
                            and content != self.last_clipboard_text
                            and ("youtube" in content or "youtu.be" in content or "tiktok" in content
                                 or "instagram" in content or "facebook" in content or "fb.watch" in content
                                 or "twitter" in content or "x.com" in content or "reddit" in content)
                        ):
                            self.last_clipboard_text = content
                            self.after(0, lambda c=content: self._handle_copied_url(c))
                    except Exception:
                        pass
                time.sleep(1.2)

        threading.Thread(target=watcher, daemon=True).start()

    def _handle_copied_url(self, url: str):
        if self.url_var.get().strip() != url:
            self.url_var.set(url)
            self.append_terminal_log(f"[CLIPBOARD] Link capturado automaticamente: {url[:50]}...")

    def _on_toggle_clipboard_monitor(self):
        if self.auto_clipboard_var.get():
            self.append_terminal_log("[MONITOR] Captura automática do Ctrl+C ATIVADA.")
        else:
            self.append_terminal_log("[MONITOR] Captura automática do Ctrl+C DESATIVADA.")

    # --- PASTAS ---
    def _choose_directory(self):
        folder = filedialog.askdirectory(initialdir=self.download_dir_var.get())
        if folder:
            self.download_dir_var.set(folder)
            self.append_terminal_log(f"[DESTINO] Pasta alterada para: {folder}")

    def _open_download_folder(self):
        folder = self.download_dir_var.get()
        if os.path.exists(folder):
            try:
                os.startfile(folder)
                self.append_terminal_log(f"[EXPLORER] Pasta aberta: {folder}")
            except Exception as e:
                self.append_terminal_log(f"[ERRO] Falha ao abrir pasta: {e}")
        else:
            messagebox.showwarning("Pasta não encontrada", "A pasta selecionada ainda não existe.")

    # --- PROCESSO DE DOWNLOAD ---
    def _on_download_click(self):
        if self.is_downloading:
            self.engine.cancel()
            self.btn_download.configure(text="Cancelando...", state="disabled")
            self.append_terminal_log("[SISTEMA] Cancelando download ativo...")
        else:
            self._start_download()

    def _start_download(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showinfo("Aviso", "Por favor, insira ou cole a URL do vídeo que deseja baixar.")
            return

        if not url.startswith(("http://", "https://")):
            messagebox.showerror("URL Inválida", "A URL deve começar com http:// ou https://")
            return

        output_dir = self.download_dir_var.get()
        media_type = self.media_type_var.get()

        res_code = self.res_map.get(self.video_res_var.get(), "best")
        v_format = self.v_format_map.get(self.video_format_var.get(), "mp4")
        a_format = self.a_format_map.get(self.audio_format_var.get(), "mp3")
        a_bitrate = self.a_bitrate_map.get(self.audio_bitrate_var.get(), "320")

        embed_thumb = self.embed_thumb_var.get()
        subtitles = self.subtitles_var.get()
        download_playlist = self.download_full_playlist_var.get() if "PLAYLIST" in self.platform_badge.cget("text") else False

        self.is_downloading = True
        self.btn_download.configure(
            text="⏹   CANCELAR DOWNLOAD",
            fg_color=COLOR_ACCENT_RED,
            text_color=COLOR_TEXT_WHITE,
            hover_color="#b52a27",
            state="normal"
        )
        self.status_indicator.configure(text="● BAIXANDO", text_color="#d29922")
        self.progress_bar.set(0)
        self.lbl_progress_status.configure(text="Conectando aos servidores...")
        self.lbl_progress_metrics.configure(text="0% • Conectando...")

        t = threading.Thread(
            target=self._download_worker,
            args=(url, output_dir, media_type, res_code, v_format, a_format, a_bitrate, embed_thumb, subtitles, download_playlist),
            daemon=True
        )
        t.start()

    def _download_worker(
        self,
        url: str,
        output_dir: str,
        media_type: str,
        res_code: str,
        v_format: str,
        a_format: str,
        a_bitrate: str,
        embed_thumb: bool,
        subtitles: bool,
        download_playlist: bool
    ):
        try:
            self.engine.download(
                url=url,
                output_dir=output_dir,
                media_type=media_type,
                resolution=res_code,
                video_format=v_format,
                audio_format=a_format,
                audio_bitrate=a_bitrate,
                embed_thumbnail=embed_thumb,
                download_subtitles=subtitles,
                download_playlist=download_playlist,
                progress_callback=self._on_progress_update
            )
            self.after(0, self._on_download_success)
        except DownloadCancelledException:
            self.after(0, self._on_download_cancelled)
        except Exception as e:
            self.after(0, lambda err=str(e): self._on_download_error(err))

    def _on_progress_update(self, data: dict):
        status = data.get('status')
        percent = data.get('percent', 0.0)
        speed = data.get('speed', '-- MB/s')
        eta = data.get('eta', '--:--')
        filename = data.get('filename', '')

        self.after(0, lambda: self._update_ui_progress(status, percent, speed, eta, filename))

    def _update_ui_progress(self, status: str, percent: float, speed: str, eta: str, filename: str):
        self.progress_bar.set(percent / 100.0)
        display_name = filename if len(filename) <= 45 else filename[:42] + "..."

        if status == 'downloading':
            self.lbl_progress_status.configure(text=f"Baixando: {display_name}")
            self.lbl_progress_metrics.configure(text=f"{percent:.1f}% • {speed} • ETA: {eta}")
        elif status == 'processing':
            self.lbl_progress_status.configure(text=f"Finalizando e convertendo: {display_name}")
            self.lbl_progress_metrics.configure(text="100% • Processando...")
        elif status == 'finished':
            self.lbl_progress_status.configure(text="Download concluído com sucesso!")
            self.lbl_progress_metrics.configure(text="100% • Concluído")

    def _reset_buttons(self):
        self.is_downloading = False
        self.btn_download.configure(
            text="⬇   INICIAR DOWNLOAD",
            fg_color=COLOR_BTN_PRIMARY_BG,
            text_color=COLOR_BTN_PRIMARY_TEXT,
            hover_color=COLOR_BTN_PRIMARY_HOVER,
            state="normal"
        )
        self.status_indicator.configure(text="● ONLINE", text_color=COLOR_ACCENT_GREEN)

    def _on_download_success(self):
        self._reset_buttons()
        self.progress_bar.set(1.0)
        self.lbl_progress_status.configure(text="Concluído com sucesso!")
        self.lbl_progress_metrics.configure(text="100% • Sucesso")
        self.append_terminal_log("[SUCESSO] Operação finalizada. Arquivo pronto para reprodução.")

    def _on_download_cancelled(self):
        self._reset_buttons()
        self.progress_bar.set(0)
        self.lbl_progress_status.configure(text="Download cancelado pelo usuário.")
        self.lbl_progress_metrics.configure(text="Cancelado")
        self.append_terminal_log("[AVISO] Download cancelado.")

    def _on_download_error(self, err: str):
        self._reset_buttons()
        self.lbl_progress_status.configure(text="Falha no download.")
        self.lbl_progress_metrics.configure(text="Erro")
        self.status_indicator.configure(text="● ERRO", text_color=COLOR_ACCENT_RED)
        self.append_terminal_log(f"[ERRO CRÍTICO] {err}")


def main():
    app = UniversalDownloaderApp()
    app.mainloop()


if __name__ == "__main__":
    main()
