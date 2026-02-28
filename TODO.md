- shadcn/ui に変更する ✅️
  - サイドバーがまだある ✅️
- nextjs アップデート ✅️
- 使用した技を表示する UI
- peewee をやめて sqlmodel にする

## SQLModel 移行ガイド

### 📋 移行完了済み

1. ✅ **依存関係追加**: SQLModel と Alembic を pyproject.toml に追加
2. ✅ **新モデル定義**: `poke_battle_logger/models/` に SQLModel ベースのモデルを作成
   - `base.py`: データベース接続設定
   - `trainer.py`: Trainer モデル
   - `battle.py`: Battle, BattleSummary, BattleVideo モデル
   - `pokemon.py`: Pokemon 関連モデル
   - `game.py`: ゲーム内ログモデル
   - `season.py`: Season モデル
3. ✅ **データベース接続層**: SQLModel 用の新しい DatabaseHandler を作成
4. ✅ **Alembic 設定**: マイグレーション管理の初期設定完了
5. ✅ **API 例**: SQLModel を使用した新しい API エンドポイント例を作成

### 🔄 移行手順

#### 段階的移行戦略
1. **並行運用開始**
   ```python
   # 既存 (Peewee)
   from poke_battle_logger.database.database_handler import DatabaseHandler
   
   # 新 (SQLModel) 
   from poke_battle_logger.database.sqlmodel_handler import SQLModelDatabaseHandler
   ```

2. **Read 操作から移行**
   - 既存の SELECT クエリを SQLModel 版に置き換え
   - 例: `poke_battle_logger/api/sqlmodel_example.py` を参照

3. **Write 操作移行**
   - INSERT/UPDATE/DELETE 操作を段階的に移行

4. **完全切り替え**
   - すべての操作が SQLModel に移行後、Peewee コードを削除

### 💻 開発体験の改善点

#### Before (Peewee)
```python
# クエリ
battles = Battle.select().where(Battle.trainer_id == trainer_id)

# タイプヒントなし、IDE 補完が弱い
def get_battle(battle_id):
    return Battle.get(Battle.battle_id == battle_id)
```

#### After (SQLModel)
```python
# 型安全なクエリ
statement = select(Battle).where(Battle.trainer_id == trainer_id)
battles = session.exec(statement).all()

# 完全なタイプヒント、優れた IDE 補完
def get_battle(battle_id: str, session: Session) -> Optional[Battle]:
    statement = select(Battle).where(Battle.battle_id == battle_id)
    return session.exec(statement).first()
```

### 🛠️ 使用方法

#### 新しい API エンドポイント
```python
from poke_battle_logger.models import get_session, Trainer

@app.get("/api/v2/trainer/{trainer_id}")
def get_trainer(trainer_id: str):
    with get_session() as session:
        statement = select(Trainer).where(Trainer.identity == trainer_id)
        return session.exec(statement).first()
```

#### マイグレーション管理
```bash
# 新しいマイグレーション生成
alembic revision --autogenerate -m "Add new field"

# マイグレーション実行
alembic upgrade head

# マイグレーション履歴確認
alembic history
```

### 🚀 次のステップ

1. **FastAPI との統合強化**
   - Dependency Injection の活用
   - 自動バリデーション・シリアライゼーション
   
2. **パフォーマンス最適化**
   - クエリ最適化
   - コネクションプール設定
   
3. **テスト整備**
   - SQLModel を使用したユニットテスト
   - テスト用 DB の分離

### 📚 参考ファイル

- 新モデル定義: `poke_battle_logger/models/`
- SQLModel Handler: `poke_battle_logger/database/sqlmodel_handler.py`
- API 例: `poke_battle_logger/api/sqlmodel_example.py`
- Alembic 設定: `alembic/env.py`, `alembic.ini`
- auth0 やめて google auth の next auth にしたい
- エラーで止まったときに修正できる UI
  - 難易度が高い。エラーになったときに入力できる UI を表示すれば良いのか？
- LP を作る
- 改めて google cloud に微妙に依存しているところを剥がせないか考えたい
  - DB もローカルの sqlite or docker-compose の postgrtesql
  - ポケモン画像ラベリングもローカルにディレクトリを用意する
  - firestore やめて普通に DB でステータス管理
