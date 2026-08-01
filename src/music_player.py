import vlc
from yt_dlp import YoutubeDL


class MusicPlayer:
    def __init__(self):
        # Инициализируем VLC без видеовыхода
        self.instance = vlc.Instance('--no-video', '--quiet')
        self.player = self.instance.media_player_new()
        self.is_playing_flag = False

        self.ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'sponsorblock_remove': 'sponsor,intro,outro,selfpromo,music_offtopic',
        }

    def play_from_query(self, query: str, source: str = "ytsearch") -> str:
        """
        Ищет трек на YouTube или SoundCloud и запускает потоковое воспроизведение.
        :param query: Название трека или исполнителя
        :param source: 'ytsearch' для YouTube/YouTube Music или 'scsearch' для SoundCloud
        :return: Название найденного трека или None при ошибке
        """
        search_query = f"{source}:{query}"

        with YoutubeDL(self.ydl_opts) as ydl:
            try:
                info = ydl.extract_info(search_query, download=False)
                if 'entries' in info and len(info['entries']) > 0:
                    video_data = info['entries'][0]
                else:
                    video_data = info

                stream_url = video_data['url']
                title = video_data.get('title', 'music track')

                # Останавливаем предыдущий трек, если он играл
                self.stop()

                # Запускаем новый поток
                media = self.instance.media_new(stream_url)
                self.player.set_media(media)
                self.player.play()
                self.is_playing_flag = True

                return title
            except Exception as e:
                print(f"[Music Error]: Failed to extract stream or play audio: {e}")
                return None

    def stop(self):
        """Останавливает воспроизведение музыки."""
        if self.player:
            self.player.stop()
            self.is_playing_flag = False

    def is_playing(self) -> bool:
        """Возвращает True, если сейчас активно воспроизводится трек."""
        if not self.player:
            return False
        state = self.player.get_state()
        return self.is_playing_flag and (state == vlc.State.Playing)