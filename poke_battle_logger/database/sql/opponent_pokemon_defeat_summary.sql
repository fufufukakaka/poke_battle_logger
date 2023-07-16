with target_trainer as (
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
