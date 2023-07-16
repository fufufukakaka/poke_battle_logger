with ranked_battle_log as (
	select
		battle_id,
		turn,
		frame_number,
		LEAD(frame_number) over (partition by battle_id order by turn) as next_frame_number
	from
		inbattlepokemonlog
),
messagelog2 as (
select
	ml.battle_id,
	rbl.turn,
	ml.frame_number,
	ml.message
from
	messagelog ml
	left join ranked_battle_log rbl on ml.battle_id = rbl.battle_id
		and ml.frame_number >= rbl.frame_number
		AND(ml.frame_number < rbl.next_frame_number
		or rbl.next_frame_number is null)
),
fainted_pokemon as (
select
	m.battle_id,
	m.turn,
	case when m.message like 'The opposing % fainted!' then
		'Opponent Pokemon Fainted'
	when m.message like '% fainted!' then
		'Your Pokemon Fainted'
	end as fainted_pokemon_type
from
	messagelog2 m
where
	m.message like '% fainted!'
),
battles as (
select
	i.battle_id,
	i.turn,
	i.your_pokemon_name,
	i.opponent_pokemon_name,
	f.fainted_pokemon_type
from
	inbattlepokemonlog i
	join fainted_pokemon f on i.turn = f.turn
		and i.battle_id = f.battle_id
)
select
	b.battle_id,
	b.turn,
	b.your_pokemon_name,
	b.opponent_pokemon_name,
	case when b.fainted_pokemon_type = 'Your Pokemon Fainted' then
		'Opponent Pokemon Win'
	when b.fainted_pokemon_type = 'Opponent Pokemon Fainted' then
		'Your Pokemon Win'
	else
		'Unknown'
	end as fainted_pokemon_side
from
	battles b
where
	b.battle_id = '{battle_id}'
