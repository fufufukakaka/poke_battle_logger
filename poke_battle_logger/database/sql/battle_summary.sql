select
    battle_id,
    win_or_lose,
    next_rank,
    your_team,
    opponent_team,
    your_pokemon_1,
    your_pokemon_2,
    your_pokemon_3,
    opponent_pokemon_1,
    opponent_pokemon_2,
    opponent_pokemon_3
from
    battlesummary
where
    battle_id = '{battle_id}'
