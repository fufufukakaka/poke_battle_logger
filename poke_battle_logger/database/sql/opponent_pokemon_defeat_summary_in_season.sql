with season_start_end as (
	select start_datetime,
		end_datetime
	from season
	where season = {season}
),
target_trainer as (
	select id
	from trainer
	where identity = '{trainer_id}'
),
target_battles as (
	select battle_id
	from battle
	where trainer_id in (
			select id
			from target_trainer
		)
),
target_battle_summary as (
	select battle_id
	from battlesummary
	where battle_id in (
			select battle_id
			from target_battles
		)
		and created_at between(
			select start_datetime
			from season_start_end
		)
		and(
			select end_datetime
			from season_start_end
		)
),
target_log as (
	select *
	from faintedlog
	where battle_id in (
			select battle_id
			from target_battles
		)
)
select
	your_pokemon_name,
	opponent_pokemon_name,
	count(1) as defeat_count
from
	target_log
where fainted_pokemon_side = 'Opponent Pokemon Win'
group by your_pokemon_name, opponent_pokemon_name
