# импортируем библиотеку для работы с табличными данными
import pandas as pd

# импортируем FastAPI для создания микросервиса
from fastapi import FastAPI

# создаём приложение FastAPI
app = FastAPI()

# загружаем итоговые офлайн-рекомендации
recommendations = pd.read_parquet("recommendations.parquet")

# загружаем похожие треки для формирования онлайн-рекомендаций
similar = pd.read_parquet("similar.parquet")

# загружаем популярные треки для пользователей без персональных рекомендаций
top_popular = pd.read_parquet("top_popular.parquet")

# создаём хранилище онлайн-истории пользователей
online_history = {}

# создаём базовый эндпоинт для проверки работы сервиса
@app.get("/")
def root():
    return {"status": "ok"}

# создаём эндпоинт для добавления трека в онлайн-историю пользователя
@app.post("/history/{user_id}/{track_id}")
def add_online_history(user_id: int, track_id: int):
    # создаём историю пользователя, если её ещё нет
    if user_id not in online_history:
        online_history[user_id] = []

    # добавляем трек в онлайн-историю пользователя
    online_history[user_id].append(track_id)

    # возвращаем обновлённую историю пользователя
    return {
        "user_id": user_id,
        "history": online_history[user_id]
    }

# создаём функцию для получения онлайн-рекомендаций по истории пользователя
def get_online_recommendations(user_id: int, limit: int = 20):
    # получаем онлайн-историю указанного пользователя
    history_tracks = online_history.get(user_id, [])

    # если онлайн-истории нет, возвращаем пустой список
    if not history_tracks:
        return []

    # выбираем похожие треки для истории пользователя
    online_recommendations = similar[
        similar["track_id"].isin(history_tracks)
    ].sort_values(["track_id", "rank"])

    # убираем уже прослушанные треки и дубликаты
    online_recommendations = online_recommendations[
        ~online_recommendations["similar_track_id"].isin(history_tracks)
    ].drop_duplicates("similar_track_id")

    # возвращаем ограниченное число онлайн-рекомендаций
    return online_recommendations["similar_track_id"].head(limit).tolist()

# создаём функцию для смешивания онлайн- и офлайн-рекомендаций
def mix_recommendations(offline_recommendations, online_recommendations, limit=100):
    # создаём итоговый список рекомендаций
    mixed_recommendations = []

    # поочерёдно добавляем онлайн- и офлайн-рекомендации
    max_length = max(
        len(offline_recommendations),
        len(online_recommendations)
    )

    for index in range(max_length):
        if index < len(online_recommendations):
            track_id = online_recommendations[index]

            if track_id not in mixed_recommendations:
                mixed_recommendations.append(track_id)

        if index < len(offline_recommendations):
            track_id = offline_recommendations[index]

            if track_id not in mixed_recommendations:
                mixed_recommendations.append(track_id)

        if len(mixed_recommendations) >= limit:
            break

    # возвращаем итоговую выдачу заданной длины
    return mixed_recommendations[:limit]


# создаём эндпоинт для получения рекомендаций пользователя
@app.get("/recommendations/{user_id}")
def get_recommendations(user_id: int):
    # выбираем офлайн-рекомендации для указанного пользователя
    user_recommendations = recommendations[
        recommendations["user_id"] == user_id
    ]

    # если персональных рекомендаций нет, используем популярные треки
    if user_recommendations.empty:
        fallback_recommendations = (
            top_popular
            .sort_values("rank")
            ["track_id"]
            .head(100)
            .tolist()
        )

        return {
            "user_id": user_id,
            "recommendations": fallback_recommendations
        }

    # получаем список персональных офлайн-рекомендаций
    offline_recommendations = (
        user_recommendations
        .sort_values("rank")
        ["track_id"]
        .tolist()
    )

    # получаем онлайн-рекомендации по истории пользователя
    online_recommendations = get_online_recommendations(user_id)

    # смешиваем онлайн- и офлайн-рекомендации
    final_recommendations = mix_recommendations(
        offline_recommendations,
        online_recommendations,
        limit=100
    )

    # возвращаем итоговые рекомендации
    return {
        "user_id": user_id,
        "recommendations": final_recommendations
    }