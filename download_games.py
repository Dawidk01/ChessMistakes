import requests
import datetime
import sys
import os

# Retrieve the API key from environment variables
lichess_api_key = os.getenv('LICHESS_API')

if lichess_api_key is None:
    raise ValueError("Environment variable 'LICHESS_API' is not set")


#API_KEY = "lip_xiFsUFY21yQl3SEFwXAR"
USERNAME = "Dawidk01"
YEAR = 2024
PERF_TYPE = "rapid"

print("Starting script...")

start_date = int(datetime.datetime(YEAR, 7, 1).timestamp() * 1000)
end_date = int(datetime.datetime(YEAR, 7, 31).timestamp() * 1000)

headers = {
    "Authorization": f"Bearer {lichess_api_key}",
    "Accept": "application/x-ndjson"
}

params = {
    "since": start_date,
    "until": end_date,
    "perfType": PERF_TYPE,
    "analysed": True,
    "evals": True,
    "opening": True,
    "moves": True,
    "clocks": True,
}

print(
    f"Requesting games for {USERNAME} from {datetime.datetime.fromtimestamp(start_date / 1000)} to {datetime.datetime.fromtimestamp(end_date / 1000)}")


def get_game_pgn(game_id, params):
    game_url = f"https://lichess.org/game/export/{game_id}?literate=1"
    game_response = requests.get(game_url, headers=headers, params=params)
    if game_response.status_code == 200:
        return game_response.text
    else:
        print(f"Failed to fetch PGN for game {game_id}. Status code: {game_response.status_code}")
        return None


try:
    response = requests.get(f"https://lichess.org/api/games/user/{USERNAME}", headers=headers, params=params,
                            stream=True)
    print(f"API response status code: {response.status_code}")


    games_processed = 0
    games_with_annotations = 0
    games_without_annotations = 0

    for line in response.iter_lines():
        if line:
            games_processed += 1
            game = requests.compat.json.loads(line.decode('utf-8'))
            game_id = game['id']
            pgn = get_game_pgn(game_id, params)

            if pgn:
                if 'Inaccuracy' in pgn or 'Mistake' in pgn or 'Blunder' in pgn:
                    games_with_annotations += 1
                    print(f"\nPGN for game {game_id} (with annotations):")
                    print(pgn)
                else:
                    games_without_annotations += 1
                    print(f"\nPGN for game {game_id} (without annotations):")
                    print(pgn)
                print("\n" + "=" * 50 + "\n")

    print(f"Total games processed: {games_processed}")
    print(f"Games with annotations: {games_with_annotations}")
    print(f"Games without annotations: {games_without_annotations}")

except Exception as e:
    print(f"An error occurred: {e}", file=sys.stderr)

print("Script finished.")