# PokeBattleLogger

ポケモンSV のランクマッチ(マスターボール以上) の youtube 配信から、対戦データを抽出します。

## Setup

Pyton 3.10 +

```
poetry install
```

## Batch

GCP cloud vision を用いるので、credential を事前に配置する必要があります。

```
export GOOGLE_APPLICATION_CREDENTIALS=.credentials/{your_credential}.json
VIDEO_ID={your_pokemon_sv_rank_match_stream_id} make extract-data
```

抽出したデータは sqlite に保存されます。

## Visualize App

🚧 Under Construction 🚧

```
make run-dashboard
```
