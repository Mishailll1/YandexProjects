import os
from steam_web_api import Steam
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("STEAM_API_KEY")
steam = Steam(API_KEY)

def get_info(appid: int):
    try:
        response = steam.apps.get_app_details(appid)
        if not response or str(appid) not in response:
            print("Такая игра не найдена.")
            return None

        game_info = response[str(appid)]['data']
        name = game_info.get('name', 'Unknown')
        thumbnail = game_info.get('header_image')

        return {
            'name': name,
            'thumbnail': thumbnail
        }
    except Exception as error:
        print(error)
        return None

def get_hours(steamid: str, appid: int):
    try:
        response = steam.users.get_owned_games(steamid)
        if not response or "games" not in response:
            print('Возможно, профиль закрыт.')
            return 0.0

        games = response['games']
        for game in games:
            if game.get('appid') == appid:
                minutes = game.get('playtime_forever', 0)
                return round(minutes / 60, 1)

        return 0.0
    except Exception as error:
        print(error)
        return 0.0

def get_achievements(steamid: int, appid: int):
    try:
        response = steam.apps.get_user_achievements(steamid, appid)
        if not response or 'achievements' not in response['playerstats']:
            print('Ошибочка.')
            return {
                'curr_ach': 0,
                'total_ach': 0
            }

        achieved = 0
        total = len(response['playerstats']['achievements'])
        for ach in response['playerstats']['achievements']:
            if ach['achieved'] == 1:
                achieved += 1
        return {
            'curr_ach': achieved,
            'total_ach': total
        }
    except Exception as error:
        print(error)
        return None