with ranked_battle_log as (
	select
		battle_id,
		turn,
		frame_number,
		LEAD(frame_number) over (partition by battle_id order by turn) as next_frame_number,
		your_pokemon_name,
		opponent_pokemon_name
	from
		inbattlepokemonlog
)
select
	COALESCE(rbl.turn, 0) as turn,
	ml.frame_number,
	ml.message,
	rbl.your_pokemon_name,
	rbl.opponent_pokemon_name
from
	messagelog ml
	left join ranked_battle_log rbl on ml.battle_id = rbl.battle_id
		and ml.frame_number >= rbl.frame_number
		AND(ml.frame_number < rbl.next_frame_number
		or rbl.next_frame_number is null)
where
	ml.battle_id = '{battle_id}'
order by
	ml.frame_number
