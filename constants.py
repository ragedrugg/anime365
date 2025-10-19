"""
Константы для типов данных API anime365
"""

# Типы аниме (type)
ANIME_TYPES = {
    "tv": "ТВ сериал",
    "movie": "Фильм", 
    "ova": "OVA",
    "ona": "ONA",
    "special": "Спешл",
    "music": "Музыкальное видео"
}

# Типы эпизодов (episodeType)
EPISODE_TYPES = {
    "tv": "ТВ эпизод",
    "preview": "Превью",
    "special": "Спешл",
    "ova": "OVA",
    "ona": "ONA"
}

# Типы переводов (type)
TRANSLATION_TYPES = {
    "subRu": "Русские субтитры",
    "subEn": "Английские субтитры", 
    "voiceRu": "Русская озвучка",
    "voiceEn": "Английская озвучка",
    "raw": "RAW (без перевода)"
}

# Типы качества (qualityType)
QUALITY_TYPES = {
    "tv": "ТВ качество",
    "bd": "Blu-ray качество",
    "dvd": "DVD качество"
}

# Типы языков (typeLang)
LANGUAGE_TYPES = {
    "ru": "Русский",
    "en": "Английский",
    "ja": "Японский"
}

# Типы контента (typeKind)
CONTENT_TYPES = {
    "sub": "Субтитры",
    "voice": "Озвучка", 
    "raw": "RAW"
}

# Типы лент для переводов (feed)
FEED_TYPES = {
    "recent": "Последние переводы онгоингов",
    "id": "Все переводы по ID (в начале самые старые)",
    "all": "Все переводы включая неактивные"
}

# Статусы активности
ACTIVE_STATUS = {
    0: "Неактивно",
    1: "Активно"
}

# Статусы премиума
PREMIUM_STATUS = {
    False: "Обычный пользователь",
    True: "Премиум пользователь"
}
