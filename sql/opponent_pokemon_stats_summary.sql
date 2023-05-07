with target_trainer as (
    select id
    from trainer
    where identity = '{trainer_id}'
),
target_trainer_battles as (
    select battle_id
    from battle
    where trainer_id in (
            select id
            from target_trainer
        )
),
target_battle_pokemon_team as (
    select *
    from battlepokemonteam
    where battle_id in (
            select battle_id
            from target_trainer_battles
        )
),
target_battle_summary as (
    select *
    from battlesummary
    where battle_id in (
            select battle_id
            from target_trainer_battles
        )
),
battle_count as (
    select count(1) as counts
    from target_battle_summary
),
in_team_count as (
    select pokemon_name,
        count(1) as counts
    from target_battle_pokemon_team
    where team = 'opponent'
    group by pokemon_name
),
first_in_battle_count as (
    select opponent_pokemon_1 as pokemon_name,
        count(1) as counts
    from target_battle_summary
    group by opponent_pokemon_1
),
second_in_battle_count as (
    select opponent_pokemon_2 as pokemon_name,
        count(1) as counts
    from target_battle_summary
    group by opponent_pokemon_2
),
third_in_battle_count as (
    select opponent_pokemon_3 as pokemon_name,
        count(1) as counts
    from target_battle_summary
    group by opponent_pokemon_3
),
unions_in_battle_count as (
    select *
    from first_in_battle_count
    union all
    select *
    from second_in_battle_count
    union all
    select *
    from third_in_battle_count
),
in_battle_count as (
    select pokemon_name,
        sum(counts) as counts
    from unions_in_battle_count
    group by pokemon_name
),
first_in_battle_lose_count as (
    select opponent_pokemon_1 as pokemon_name,
        count(1) as counts
    from target_battle_summary
    where win_or_lose = 'lose'
    group by opponent_pokemon_1
),
second_in_battle_lose_count as (
    select opponent_pokemon_2 as pokemon_name,
        count(1) as counts
    from target_battle_summary
    where win_or_lose = 'lose'
    group by opponent_pokemon_2
),
third_in_battle_lose_count as (
    select opponent_pokemon_3 as pokemon_name,
        count(1) as counts
    from target_battle_summary
    where win_or_lose = 'lose'
    group by opponent_pokemon_3
),
unions_in_battle_lose_count as (
    select *
    from first_in_battle_lose_count
    union all
    select *
    from second_in_battle_lose_count
    union all
    select *
    from third_in_battle_lose_count
),
in_battle_lose_count as (
    select pokemon_name,
        sum(counts) as counts
    from unions_in_battle_lose_count
    group by pokemon_name
),
head_battle_count as (
    select opponent_pokemon_1 as pokemon_name,
        count(1) as counts
    from target_battle_summary
    group by opponent_pokemon_1
),
joins as (
    select in_team_count.pokemon_name,
        coalesce(head_battle_count.counts, 0) as head_battle_count,
        coalesce(in_battle_lose_count.counts, 0) as in_battle_lose_count,
        coalesce(in_battle_count.counts, 0) as in_battle_count,
        coalesce(in_team_count.counts, 0) as in_team_count,
        (
            select counts
            from battle_count
        ) as battle_count
    from in_team_count
        left join in_battle_lose_count on in_battle_lose_count.pokemon_name = in_team_count.pokemon_name
        left join in_battle_count on in_battle_count.pokemon_name = in_team_count.pokemon_name
        left join head_battle_count on in_team_count.pokemon_name = head_battle_count.pokemon_name
)
select pokemon_name,
    coalesce(
        in_team_count * 1.0 / NULLIF(battle_count, 0),
        0.0
    ) as in_team_rate,
    coalesce(
        in_battle_count * 1.0 / NULLIF(in_team_count, 0),
        0.0
    ) as in_battle_rate,
    coalesce(
        in_battle_lose_count * 1.0 / NULLIF(in_battle_count, 0),
        0.0
    ) as in_battle_lose_rate,
    coalesce(
        head_battle_count * 1.0 / NULLIF(in_battle_count, 0),
        0.0
    ) as head_battle_rate,
    in_team_count,
    in_battle_count,
    in_battle_lose_count,
    head_battle_count
from joins
