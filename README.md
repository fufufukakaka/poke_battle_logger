# PokeBattleLogger

ポケモンSV のランクマッチ(マスターボール以上) の youtube 配信から、対戦データを抽出します。

## Notification

- 動画のサイズは 720p: 1280 x 720 (HD) のみに対応しています。
- 必ず「続ける」or「対戦チームを変える」で順位を表示する必要があります。表示されていない場合、正常に動作しません。
- また、バトルスタジアムから抜ける場合は動画を切って頂く必要があります。
- 何らかの理由で順位が変動しなかった試合についてはデータ抽出を行いません。

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
