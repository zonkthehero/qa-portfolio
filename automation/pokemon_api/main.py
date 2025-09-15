import requests
import time

BASE_URL = 'https://api.pokemonbattle.ru/v2/'
TOKEN = 'some_text'  ## сюда вставить токен тренера


def get_my_pokemon():
    url = BASE_URL + 'pokemons'
    params = {
        'trainer_id': 42889,
        'status': 1
    }
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.get(url, headers=headers, params=params)
    response_data = response.json()

    if response_data.get('status') == 'success':
        if 'data' in response_data and response_data['data']:
            return response_data['data']
        else:
            print("У вас нет живых покемонов.")
            return []
    else:
        print(f"Ошибка получения списка покемонов: {response_data.get('message', 'нет сообщения об ошибке')}")
        return []


def create_pokemon():
    url = BASE_URL + 'pokemons'
    headers = {
        'Content-Type': 'application/json',
        "trainer_token": TOKEN,
    }
    data = {
        'name': 'generate',
        'photo_id': -1
    }

    response = requests.post(url, headers=headers, json=data)
    response_data = response.json()

    if response_data.get("message") == "Покемон создан":
        return response_data["id"]
    elif response_data.get("message").startswith("Максимум"):
        print("Ошибка: превышен лимит живых покемонов")
        return "LIMIT_EXCEEDED"
    elif response_data.get("message").startswith("Мы не узнали"):
        print("Ошибка: неизвестный токен тренера")
        return None
    else:
        print("Неизвестная ошибка:", response_data.get("message"))
        return None


def catch_pokemon(pokemon_id):
    url = BASE_URL + 'trainers/add_pokeball'
    headers = {
        'Content-Type': 'application/json',
        'trainer_token': TOKEN,
    }
    data = {
        "pokemon_id": pokemon_id
    }

    response = requests.post(url, headers=headers, json=data)
    response_data = response.json()
    print("Результат попытки поймать покемона:", response_data)

    if "пойман" in response_data.get("message", "").lower():
        return True
    else:
        print("Не удалось поймать покемона:", response_data.get("message"))
        return False


def find_opponent():
    url = BASE_URL + 'pokemons'
    params = {
        'status': 1,
        'in_pokeball': 1
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers, params=params)
    response_data = response.json()

    if response_data.get('status') == 'success' and response_data.get('data'):
        opponents = [p for p in response_data['data'] if str(p['trainer_id']) != '42889'] ## исключаем покемонов, относящихся к нашему trainer id
        if opponents:
            return opponents[0]['id']
    return None


def start_battle(pokemon_id, opponent_id):
    url = BASE_URL + 'battle'
    headers = {
        'trainer_token': TOKEN,
        'Content-Type': 'application/json'
    }
    data = {
    "attacking_pokemon": pokemon_id,
    "defending_pokemon": opponent_id
    }

    response = requests.post(url, headers=headers, json=data)
    response_data = response.json()

    if response_data.get('status') == 'error' and 'лимит боёв исчерпан' in response_data.get('message', '').lower():
        print("Дневной лимит боёв достигнут")
        return "LIMIT_EXCEEDED"

    if response_data.get('message') == 'Битва проведена' and response_data.get('result'):
        return response_data["result"]

    print("Ошибка в проведении битвы:", response_data.get('message'))
    return None


def main():
    while True:
        # 1. Проверяем, есть ли живой покемон
        print('Ищу своего живого покемона')
        pokemon_list = get_my_pokemon()
        time.sleep(1)

        if pokemon_list:
            first_pokemon = pokemon_list[0]
            if first_pokemon.get('in_pokeball') == 1:
                pokemon_id = first_pokemon['id']
                print('ID живого покемона в покеболе:', pokemon_id)
                time.sleep(1)
            else:
                print('Найден покемон, но он не в покеболе. Нужно поймать.')
                time.sleep(1)
                pokemon_id = first_pokemon['id']
                caught = catch_pokemon(pokemon_id)
                if not caught:
                    print("Не удалось поймать покемона")
                    break
        else:
            # Если нет живых — создаём нового
            print('Создаю покемона')
            creation_result = create_pokemon()
            time.sleep(1)
            if creation_result == "LIMIT_EXCEEDED":
                print("Достигнут лимит живых покемонов")
                break
            elif creation_result:
                pokemon_id = creation_result
                caught = catch_pokemon(pokemon_id)
                if not caught:
                    print("Не удалось поймать покемона")
                    break
            else:
                print("Ошибка создания покемона")
                break
        
        # 2. Находим соперника для битвы
        print('Ищу соперника')
        opponent_id = find_opponent()
        time.sleep(1)
        print("Подходящий соперник:", opponent_id)
        time.sleep(1)
        if not opponent_id:
            print("Нет доступных соперников")
            break

        # 3. Запускаем битву
        print('Начинаю битву')
        time.sleep(1)
        battle_result = start_battle(pokemon_id, opponent_id)
        print("Результат боя:", battle_result)
        time.sleep(1)

        # 4. Анализируем результат и решаем, продолжать или нет
        if battle_result == 'Твой покемон победил':
            print("Победа! Ищем следующего соперника...")
            continue
        elif battle_result == 'LIMIT_EXCEEDED':
            print("Превышен дневной лимит боёв")
            break
        else:
            print("Поражение, твой покемон в нокауте")
            continue


if __name__ == "__main__":
    main()
