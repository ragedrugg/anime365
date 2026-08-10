"""Справочные словари: русскоязычные подписи для значений полей API anime365."""

ANIME_TYPES: dict[str, str] = {
    "tv": "ТВ сериал",
    "movie": "Фильм",
    "ova": "OVA",
    "ona": "ONA",
    "special": "Спешл",
    "music": "Музыкальное видео",
}

EPISODE_TYPES: dict[str, str] = {
    "tv": "ТВ эпизод",
    "preview": "Превью",
    "special": "Спешл",
    "ova": "OVA",
    "ona": "ONA",
}

TRANSLATION_TYPES: dict[str, str] = {
    "subRu": "Русские субтитры",
    "subEn": "Английские субтитры",
    "voiceRu": "Русская озвучка",
    "voiceEn": "Английская озвучка",
    "raw": "RAW (без перевода)",
}

QUALITY_TYPES: dict[str, str] = {
    "tv": "ТВ качество",
    "bd": "Blu-ray качество",
    "dvd": "DVD качество",
}

LANGUAGE_TYPES: dict[str, str] = {
    "ru": "Русский",
    "en": "Английский",
    "ja": "Японский",
}

CONTENT_TYPES: dict[str, str] = {
    "sub": "Субтитры",
    "voice": "Озвучка",
    "raw": "RAW",
}

FEED_TYPES: dict[str, str] = {
    "recent": "Последние переводы онгоингов",
    "id": "Все переводы по ID (в начале самые старые)",
    "all": "Все переводы включая неактивные",
}

ACTIVE_STATUS: dict[int, str] = {
    0: "Неактивно",
    1: "Активно",
}

PREMIUM_STATUS: dict[bool, str] = {
    False: "Обычный пользователь",
    True: "Премиум пользователь",
}
