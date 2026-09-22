"""
Motor de Download Universal (Downloader Engine)
Powered by yt-dlp, FFmpeg & Mutagen
Suporta YouTube, Instagram, TikTok (sem marca d'água), Facebook, Twitter/X e +1800 sites.
Controle total: Vídeo vs Só Áudio, Resoluções (4K a 360p), Formatos (MP4, MKV, MP3, WAV, etc.),
Bitrate de áudio, Legendas, Capas embutidas e Playlists.
"""

import os
import re
import sys
import shutil
import threading
import urllib.parse
from typing import Callable, Optional, Dict, Any, List
import yt_dlp


class DownloadCancelledException(Exception):
    pass


class DownloaderEngine:
    def __init__(self, log_callback: Optional[Callable[[str], None]] = None):
        self.log_callback = log_callback or (lambda msg: None)
        self.is_cancelled = False

    def log(self, message: str):
        self.log_callback(message)

    @staticmethod
    def clean_url(url: str) -> str:
        """Remove parâmetros de rastreamento desnecessários mantendo o identificador limpo."""
        url = url.strip()
        if not url:
            return ""
        
        try:
            parsed = urllib.parse.urlparse(url)
            # YouTube
            if "youtube.com" in parsed.netloc or "youtu.be" in parsed.netloc:
                qs = urllib.parse.parse_qs(parsed.query)
                clean_qs = {}
                if "v" in qs:
                    clean_qs["v"] = qs["v"]
                if "list" in qs:
                    clean_qs["list"] = qs["list"]
                new_query = urllib.parse.urlencode(clean_qs, doseq=True)
                return urllib.parse.urlunparse((
                    parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, ""
                ))
            # Instagram
            elif "instagram.com" in parsed.netloc:
                return urllib.parse.urlunparse((
                    parsed.scheme, parsed.netloc, parsed.path, "", "", ""
                ))
            # TikTok
            elif "tiktok.com" in parsed.netloc:
                return urllib.parse.urlunparse((
                    parsed.scheme, parsed.netloc, parsed.path, "", "", ""
                ))
            # Facebook
            elif "facebook.com" in parsed.netloc or "fb.watch" in parsed.netloc:
                return url.split("?")[0] if "reel" in url or "watch" in url else url
        except Exception:
            pass
        return url

    @staticmethod
    def identify_platform(url: str) -> Dict[str, Any]:
        """Identifica a plataforma e retorna código, nome e tag minimalista estilo terminal."""
        url_lower = url.lower().strip()
        if not url_lower or not url_lower.startswith(("http://", "https://")):
            return {
                "code": "none",
                "name": "Aguardando link...",
                "badge": "[ AGUARDANDO LINK ]",
                "is_playlist_candidate": False
            }

        is_playlist = "list=" in url_lower or "/playlist" in url_lower

        if "youtube.com" in url_lower or "youtu.be" in url_lower:
            if "shorts" in url_lower:
                return {
                    "code": "youtube_shorts",
                    "name": "YouTube Shorts",
                    "badge": "[ YOUTUBE | SHORTS ]",
                    "is_playlist_candidate": False
                }
            if is_playlist:
                return {
                    "code": "youtube_playlist",
                    "name": "YouTube Playlist",
                    "badge": "[ YOUTUBE | PLAYLIST ]",
                    "is_playlist_candidate": True
                }
            return {
                "code": "youtube",
                "name": "YouTube",
                "badge": "[ YOUTUBE | VIDEO ]",
                "is_playlist_candidate": is_playlist
            }
        elif "instagram.com" in url_lower:
            return {
                "code": "instagram",
                "name": "Instagram",
                "badge": "[ INSTAGRAM | REELS/POST (SEM LOGO) ]",
                "is_playlist_candidate": False
            }
        elif "tiktok.com" in url_lower:
            return {
                "code": "tiktok",
                "name": "TikTok",
                "badge": "[ TIKTOK | SEM MARCA D'AGUA ]",
                "is_playlist_candidate": False
            }
        elif "facebook.com" in url_lower or "fb.watch" in url_lower or "fb.com" in url_lower:
            return {
                "code": "facebook",
                "name": "Facebook",
                "badge": "[ FACEBOOK | REELS/VIDEO ]",
                "is_playlist_candidate": False
            }
        elif "twitter.com" in url_lower or "x.com" in url_lower:
            return {
                "code": "twitter",
                "name": "Twitter / X",
                "badge": "[ TWITTER / X ]",
                "is_playlist_candidate": False
            }
        elif "reddit.com" in url_lower:
            return {
                "code": "reddit",
                "name": "Reddit",
                "badge": "[ REDDIT ]",
                "is_playlist_candidate": False
            }
        elif "twitch.tv" in url_lower:
            return {
                "code": "twitch",
                "name": "Twitch",
                "badge": "[ TWITCH | CLIPS/VOD ]",
                "is_playlist_candidate": False
            }
        elif "kwai.com" in url_lower or "kuaishou.com" in url_lower:
            return {
                "code": "kwai",
                "name": "Kwai",
                "badge": "[ KWAI | SEM MARCA ]",
                "is_playlist_candidate": False
            }
        elif "vimeo.com" in url_lower:
            return {
                "code": "vimeo",
                "name": "Vimeo",
                "badge": "[ VIMEO ]",
                "is_playlist_candidate": False
            }
        elif "pinterest.com" in url_lower or "pin.it" in url_lower:
            return {
                "code": "pinterest",
                "name": "Pinterest",
                "badge": "[ PINTEREST ]",
                "is_playlist_candidate": False
            }
        else:
            return {
                "code": "universal",
                "name": "Universal",
                "badge": "[ PLATAFORMA UNIVERSAL (1800+ SITES) ]",
                "is_playlist_candidate": is_playlist
            }

    def _apply_cookie_settings(self, ydl_opts: Dict[str, Any], browser_cookies: str = "auto", platform_code: str = "") -> None:
        """Configura cookies para contornar proteções anti-bot do YouTube e outras plataformas."""
        # TikTok bloqueia requisições quando cookies de navegador ou WAF tokens expirados são enviados (HTTP 403 Forbidden).
        # O extrator nativo do yt-dlp resolve os desafios JS do TikTok perfeitamente sem cookies.
        if platform_code == "tiktok":
            return

        b_clean = (browser_cookies or "").strip().lower()

        # Se desativado explicitamente, não aplica nada
        if b_clean in ["none", "desativado", "desabilitado"]:
            return

        # 1. Se foi passado um caminho de arquivo direto existente
        if browser_cookies and os.path.isfile(browser_cookies) and os.path.getsize(browser_cookies) > 0:
            ydl_opts['cookiefile'] = browser_cookies
            self.log(f"[AUTH] Arquivo de cookies carregado: {os.path.basename(browser_cookies)}")
            return

        # 2. Verifica se existe arquivo cookies.txt no projeto ou locais padrão
        project_dir = os.path.dirname(os.path.abspath(__file__))
        cookie_candidates = [
            os.path.join(project_dir, "cookies.txt"),
            os.path.join(os.path.expanduser("~"), ".config", "yt-dlp", "cookies.txt"),
            os.path.join(os.path.expanduser("~"), "Downloads", "cookies.txt"),
        ]

        for cookie_path in cookie_candidates:
            if os.path.isfile(cookie_path) and os.path.getsize(cookie_path) > 0:
                ydl_opts['cookiefile'] = cookie_path
                self.log(f"[AUTH AUTO] Cookies ativos via arquivo: {os.path.basename(cookie_path)}")
                return

        # 3. Modo AUTO: detecta e ativa automaticamente o navegador do usuário
        if b_clean in ["auto", "automático", "automatico", ""]:
            # Prioridade 1: Google Chrome (mais comum e suporte a cookies do YouTube)
            chrome_app = "/Applications/Google Chrome.app"
            chrome_dir = os.path.expanduser("~/Library/Application Support/Google/Chrome")
            if os.path.exists(chrome_app) or os.path.exists(chrome_dir):
                ydl_opts['cookiesfrombrowser'] = ('chrome', 'Default', None, None)
                self.log("[AUTH AUTO] Autenticação automática ativa via Google Chrome.")
                return

            # Prioridade 2: Brave
            brave_dir = os.path.expanduser("~/Library/Application Support/BraveSoftware/Brave-Browser")
            if os.path.exists(brave_dir) or os.path.exists("/Applications/Brave Browser.app"):
                ydl_opts['cookiesfrombrowser'] = ('brave', 'Default', None, None)
                self.log("[AUTH AUTO] Autenticação automática ativa via Brave.")
                return

            # Prioridade 3: Safari
            if os.path.exists("/Applications/Safari.app"):
                ydl_opts['cookiesfrombrowser'] = ('safari', None, None, None)
                self.log("[AUTH AUTO] Autenticação automática ativa via Safari.")
                return

            # Prioridade 4: Firefox
            firefox_dir = os.path.expanduser("~/Library/Application Support/Firefox")
            if os.path.exists(firefox_dir) or os.path.exists("/Applications/Firefox.app"):
                ydl_opts['cookiesfrombrowser'] = ('firefox', None, None, None)
                self.log("[AUTH AUTO] Autenticação automática ativa via Firefox.")
                return

        # 4. Se o usuário selecionou um navegador específico manualmente
        if "chrome" in b_clean:
            ydl_opts['cookiesfrombrowser'] = ('chrome', 'Default', None, None)
            self.log("[AUTH] Autenticação ativa via Google Chrome.")
        elif "safari" in b_clean:
            ydl_opts['cookiesfrombrowser'] = ('safari', None, None, None)
            self.log("[AUTH] Autenticação ativa via Safari.")
        elif "firefox" in b_clean:
            ydl_opts['cookiesfrombrowser'] = ('firefox', None, None, None)
            self.log("[AUTH] Autenticação ativa via Firefox.")
        elif "brave" in b_clean:
            ydl_opts['cookiesfrombrowser'] = ('brave', 'Default', None, None)
            self.log("[AUTH] Autenticação ativa via Brave.")
        elif "edge" in b_clean:
            ydl_opts['cookiesfrombrowser'] = ('edge', 'Default', None, None)
            self.log("[AUTH] Autenticação ativa via Microsoft Edge.")


    def fetch_quick_info(self, url: str, browser_cookies: str = "auto") -> Optional[Dict[str, Any]]:
        """Extração rápida de informações essenciais em background sem travar."""
        try:
            clean = self.clean_url(url)
            platform_info = self.identify_platform(clean)
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
                'extract_flat': 'in_playlist',
                'remote_components': {'ejs:github'},
            }
            if platform_info['code'] == 'tiktok':
                ydl_opts['extractor_args'] = {
                    'tiktok': {
                        'app_version': ['20.2.1'],
                    }
                }
            self._apply_cookie_settings(ydl_opts, browser_cookies, platform_code=platform_info['code'])
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(clean, download=False)
                if not info:
                    return None

                # Salva em cache cookies.txt para acelerar os próximos acessos
                if 'cookiesfrombrowser' in ydl_opts and hasattr(ydl, 'cookiejar') and len(ydl.cookiejar) > 0:
                    try:
                        project_dir = os.path.dirname(os.path.abspath(__file__))
                        ydl.cookiejar.save(os.path.join(project_dir, "cookies.txt"), ignore_discard=True, ignore_expires=True)
                    except Exception:
                        pass

                entries = info.get('entries')
                if entries is not None:
                    count = len(list(entries))
                    return {
                        'is_playlist': True,
                        'title': info.get('title', 'Playlist'),
                        'uploader': info.get('uploader') or info.get('channel') or '',
                        'count': count,
                        'details': f"Playlist com {count} vídeos"
                    }
                else:
                    duration_sec = info.get('duration')
                    dur_str = ""
                    if duration_sec:
                        m, s = divmod(int(duration_sec), 60)
                        h, m = divmod(m, 60)
                        dur_str = f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

                    # Detecta resolução máxima disponível
                    max_height = info.get('height') or 0
                    formats = info.get('formats', [])
                    for f in formats:
                        h = f.get('height') or 0
                        if h > max_height:
                            max_height = h

                    res_str = f"{max_height}p" if max_height > 0 else "HD"

                    title = info.get('title', 'Vídeo')
                    uploader = info.get('uploader') or info.get('channel') or 'Desconhecido'

                    return {
                        'is_playlist': False,
                        'title': title,
                        'uploader': uploader,
                        'duration': dur_str,
                        'max_resolution': res_str,
                        'details': f"{title} [{uploader}] {dur_str} (Máx: {res_str})".strip()
                    }
        except Exception:
            return None

    def cancel(self):
        """Cancela o download ativo."""
        self.is_cancelled = True
        self.log("[SISTEMA] Sinal de cancelamento emitido.")

    def download(
        self,
        url: str,
        output_dir: str,
        media_type: str = "video",            # "video" ou "audio"
        resolution: str = "best",             # "best", "2160p", "1440p", "1080p", "720p", "480p", "360p"
        video_format: str = "mp4",           # "mp4", "mkv", "webm", "mov"
        audio_format: str = "mp3",           # "mp3", "m4a", "wav", "flac", "opus"
        audio_bitrate: str = "320",          # "320", "256", "192", "128"
        embed_thumbnail: bool = True,
        download_subtitles: bool = False,
        download_playlist: bool = False,
        browser_cookies: str = "auto",
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> str:
        """
        Executa o download de acordo com os parâmetros configurados pelo usuário.
        """
        self.is_cancelled = False
        clean_url = self.clean_url(url)
        os.makedirs(output_dir, exist_ok=True)

        platform_info = self.identify_platform(clean_url)
        self.log(f"[INÍCIO] URL: {clean_url}")
        self.log(f"[DETECTADO] {platform_info['badge']}")

        # Template de saída
        if download_playlist:
            outtmpl = os.path.join(output_dir, "%(playlist_title,playlist)s", "%(playlist_index)02d - %(title)s.%(ext)s")
        else:
            outtmpl = os.path.join(output_dir, "%(title)s.%(ext)s")

        ydl_opts: Dict[str, Any] = {
            'outtmpl': outtmpl,
            'noplaylist': not download_playlist,
            'quiet': False,
            'no_warnings': False,
            'windowsfilenames': True,
            'retries': 5,
            'fragment_retries': 5,
            'concurrent_fragment_downloads': 4,
            'remote_components': {'ejs:github'},
            'postprocessors': [],
        }

        # Configuração específica para TikTok sem marca d'água
        if platform_info['code'] == 'tiktok':
            ydl_opts['extractor_args'] = {
                'tiktok': {
                    'app_version': ['20.2.1'],
                }
            }

        # --- SELEÇÃO: SÓ ÁUDIO vs VÍDEO COMPLETO ---
        if media_type == "audio":
            self.log(f"[FORMATO] Extração de ÁUDIO: {audio_format.upper()} ({audio_bitrate} kbps)")
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'].append({
                'key': 'FFmpegExtractAudio',
                'preferredcodec': audio_format.lower(),
                'preferredquality': audio_bitrate,
            })
        else:
            # Modo VÍDEO COMPLETO
            # Seleção de resolução
            if resolution == "best":
                format_str = 'bestvideo+bestaudio/best'
                res_desc = "Melhor Resolução Disponível (até 4K/8K)"
            else:
                height_num = int(re.sub(r'\D', '', resolution))
                format_str = f"bestvideo[height<={height_num}]+bestaudio/best[height<={height_num}]/best"
                res_desc = f"{height_num}p"

            ydl_opts['format'] = format_str
            ydl_opts['merge_output_format'] = video_format.lower()
            self.log(f"[FORMATO] VÍDEO: Resolução {res_desc} | Formato {video_format.upper()}")

        # Adiciona metadados FFmpeg padrão
        ydl_opts['postprocessors'].append({
            'key': 'FFmpegMetadata',
            'add_metadata': True,
        })

        # Embutir Capa / Thumbnail (se marcado)
        if embed_thumbnail:
            ydl_opts['writethumbnail'] = True
            ydl_opts['postprocessors'].append({
                'key': 'EmbedThumbnail',
                'already_have_thumbnail': False,
            })
            self.log("[CONFIG] Embutir miniatura/capa original ativado.")

        # Baixar legendas (se marcado)
        if download_subtitles:
            ydl_opts['writesubtitles'] = True
            ydl_opts['writeautomaticsub'] = True
            ydl_opts['subtitleslangs'] = ['pt', 'pt-BR', 'en']
            ydl_opts['postprocessors'].append({
                'key': 'FFmpegEmbedSubtitle',
            })
            self.log("[CONFIG] Download e embutimento de legendas (pt, en) ativado.")

        # Hook de progresso
        def ydl_hook(d):
            if self.is_cancelled:
                raise DownloadCancelledException("Download interrompido pelo usuário.")
            
            status = d.get('status')
            if status == 'downloading':
                downloaded = d.get('downloaded_bytes', 0)
                total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                
                percent = 0.0
                if total > 0:
                    percent = (downloaded / total) * 100
                elif '_percent_str' in d:
                    try:
                        clean_pct = re.sub(r'[^\d.]', '', d['_percent_str'])
                        percent = float(clean_pct)
                    except Exception:
                        percent = 0.0

                speed_str = d.get('_speed_str', '-- MB/s').strip()
                eta_str = d.get('_eta_str', '--:--').strip()
                filename = os.path.basename(d.get('filename', 'arquivo'))

                if progress_callback:
                    progress_callback({
                        'status': 'downloading',
                        'percent': percent,
                        'speed': speed_str,
                        'eta': eta_str,
                        'downloaded': downloaded,
                        'total': total,
                        'filename': filename,
                    })

            elif status == 'finished':
                filename = os.path.basename(d.get('filename', 'arquivo'))
                self.log(f"[PROCESSANDO] Finalizando e convertendo arquivo: {filename}")
                if progress_callback:
                    progress_callback({
                        'status': 'processing',
                        'percent': 100.0,
                        'speed': '0 MB/s',
                        'eta': '00:00',
                        'filename': filename,
                    })

        # Aplica autenticação / cookies para evitar bloqueios anti-bot (exceto TikTok que rejeita cookies)
        self._apply_cookie_settings(ydl_opts, browser_cookies, platform_code=platform_info['code'])

        ydl_opts['progress_hooks'] = [ydl_hook]

        # Logger simplificado
        class YdlLogger:
            def __init__(self, parent):
                self.parent = parent
            def debug(self, msg):
                if any(k in msg for k in ['[download]', '[Merger]', '[ExtractAudio]', '[Metadata]', '[Thumbnails]']):
                    self.parent.log(f"> {msg}")
            def info(self, msg):
                self.parent.log(f"> {msg}")
            def warning(self, msg):
                self.parent.log(f"[AVISO] {msg}")
            def error(self, msg):
                self.parent.log(f"[ERRO] {msg}")

        ydl_opts['logger'] = YdlLogger(self)

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.log("[MOTOR] Conectando aos servidores...")
                retcode = ydl.download([clean_url])
                if retcode != 0:
                    raise RuntimeError(f"O processo retornou código de status: {retcode}")

                # Salva em cache cookies.txt para acelerar os próximos downloads
                if 'cookiesfrombrowser' in ydl_opts and hasattr(ydl, 'cookiejar') and len(ydl.cookiejar) > 0:
                    try:
                        project_dir = os.path.dirname(os.path.abspath(__file__))
                        cache_path = os.path.join(project_dir, "cookies.txt")
                        ydl.cookiejar.save(cache_path, ignore_discard=True, ignore_expires=True)
                        self.log(f"[AUTH AUTO] Sessão salva em cookies.txt ({len(ydl.cookiejar)} cookies sincronizados).")
                    except Exception:
                        pass
            
            self.log(f"[SUCESSO] Download concluído com sucesso!")
            self.log(f"[ARQUIVO] Salvo na pasta: {output_dir}")
            if progress_callback:
                progress_callback({
                    'status': 'finished',
                    'percent': 100.0,
                    'speed': 'Concluído',
                    'eta': '00:00',
                    'filename': 'Download finalizado!',
                })
            return output_dir
        except DownloadCancelledException:
            self.log("[CANCELADO] Download cancelado pelo usuário.")
            if progress_callback:
                progress_callback({
                    'status': 'cancelled',
                    'percent': 0.0,
                    'speed': 'Cancelado',
                    'eta': '--:--',
                    'filename': 'Cancelado',
                })
            raise
        except Exception as e:
            err_msg = str(e)
            # Auto-recuperação TikTok: se deu erro 403, tenta novamente garantindo que nenhum cookie seja enviado
            if platform_info['code'] == 'tiktok' and ("403" in err_msg or "Forbidden" in err_msg):
                self.log("[AUTO-RECUPERAÇÃO TIKTOK] Erro 403 detectado. Removendo cookies e reconectando...")
                ydl_opts.pop('cookiefile', None)
                ydl_opts.pop('cookiesfrombrowser', None)
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl_retry:
                        retcode = ydl_retry.download([clean_url])
                        if retcode == 0:
                            self.log("[SUCESSO] Download do TikTok concluído via auto-recuperação!")
                            self.log(f"[ARQUIVO] Salvo na pasta: {output_dir}")
                            if progress_callback:
                                progress_callback({
                                    'status': 'finished',
                                    'percent': 100.0,
                                    'speed': 'Concluído',
                                    'eta': '00:00',
                                    'filename': 'Download finalizado!',
                                })
                            return output_dir
                except Exception as retry_err:
                    err_msg = str(retry_err)

            # Auto-recuperação automática: se bloqueou por anti-bot e ainda não usou Chrome, tenta automaticamente
            if ("Sign in to confirm you" in err_msg or "confirm you're not a bot" in err_msg) and not ydl_opts.get('cookiesfrombrowser'):
                self.log("[AUTO-RECUPERAÇÃO] Bloqueio anti-bot detectado. Ativando autenticação automática...")
                ydl_opts['cookiesfrombrowser'] = ('chrome', 'Default', None, None)
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl_retry:
                        self.log("[MOTOR] Reconectando aos servidores com autenticação automática...")
                        retcode = ydl_retry.download([clean_url])
                        if retcode == 0:
                            self.log("[SUCESSO] Download concluído via auto-recuperação!")
                            self.log(f"[ARQUIVO] Salvo na pasta: {output_dir}")
                            try:
                                project_dir = os.path.dirname(os.path.abspath(__file__))
                                ydl_retry.cookiejar.save(os.path.join(project_dir, "cookies.txt"), ignore_discard=True, ignore_expires=True)
                                self.log(f"[AUTH AUTO] Sessão salva em cookies.txt ({len(ydl_retry.cookiejar)} cookies).")
                            except Exception:
                                pass
                            if progress_callback:
                                progress_callback({
                                    'status': 'finished',
                                    'percent': 100.0,
                                    'speed': 'Concluído',
                                    'eta': '00:00',
                                    'filename': 'Download finalizado!',
                                })
                            return output_dir
                except Exception as retry_err:
                    err_msg = str(retry_err)

            if "Sign in to confirm you" in err_msg or "confirm you're not a bot" in err_msg:
                self.log("[BLOQUEIO YOUTUBE] O YouTube exigiu confirmação de login/anti-bot.")
                self.log("[SOLUÇÃO AUTOMÁTICA] Se o sistema pedir confirmação de Chaves do Chrome, permita para autenticar automaticamente.")
            self.log(f"[FALHA] Erro durante o download: {err_msg}")
            if progress_callback:
                progress_callback({
                    'status': 'error',
                    'percent': 0.0,
                    'speed': 'Erro',
                    'eta': '--:--',
                    'filename': f"Erro: {err_msg}",
                })
            raise
