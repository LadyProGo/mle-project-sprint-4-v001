# импортируем библиотеку для отправки HTTP-запросов
import requests

# задаём адрес сервиса рекомендаций
BASE_URL = "http://127.0.0.1:8000"

# проверяем пользователя без персональных рекомендаций
user_without_personal = 1373207

response = requests.get(f"{BASE_URL}/recommendations/{user_without_personal}")

print("Сценарий 1: пользователь без персональных рекомендаций")
print("Статус:", response.status_code)
print("Количество рекомендаций:", len(response.json()["recommendations"]))
print("Первые рекомендации:", response.json()["recommendations"][:5])

# проверяем пользователя с персональными рекомендациями без онлайн-истории
user_without_online_history = 2109

response = requests.get(f"{BASE_URL}/recommendations/{user_without_online_history}")

print("\nСценарий 2: пользователь с персональными рекомендациями без онлайн-истории")
print("Статус:", response.status_code)
print("Количество рекомендаций:", len(response.json()["recommendations"]))
print("Первые рекомендации:", response.json()["recommendations"][:5])

# проверяем пользователя с персональными рекомендациями и онлайн-историей
user_with_online_history = 1372197
history_track = 92079766

requests.post(f"{BASE_URL}/history/{user_with_online_history}/{history_track}")

response = requests.get(f"{BASE_URL}/recommendations/{user_with_online_history}")

print("\nСценарий 3: пользователь с персональными рекомендациями и онлайн-историей")
print("Статус:", response.status_code)
print("Количество рекомендаций:", len(response.json()["recommendations"]))
print("Первые рекомендации:", response.json()["recommendations"][:5])
