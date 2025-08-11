from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


class FixedBattleMessage(BaseModel):
    internal_thinking_process: str = Field(
        ...,
        description="ポケモン対戦中に表示されるメッセージを修正する際のAIの内部思考過程を説明するテキスト。できるだけ簡潔に。",
    )
    fixed_battle_message: str = Field(
        ...,
        description="ポケモン対戦中に表示されるメッセージを修正した結果のテキスト",
    )


class OpenAIHandler:
    def __init__(self) -> None:
        self.model_name = "gpt-4.1-mini"

    def fix_battle_message(
        self,
        original_message: str,
        pre_battle_your_teams: list[str],
        pre_battle_opponent_teams: list[str],
        your_current_pokemon_name: str,
        opponent_current_pokemon_name: str,
    ) -> FixedBattleMessage:
        """ポケモン対戦中に表示されるメッセージを修正する"""
        model = ChatOpenAI(
            model=self.model_name,
        ).with_structured_output(FixedBattleMessage)

        prompt = ChatPromptTemplate.from_template(
            """
            ## あなたの役割
            あなたはポケモン対戦のメッセージを修正するAIです。
            以下の情報をもとに、ポケモン対戦中に表示されるメッセージを修正してください。

            ## 入力情報
            元のメッセージ: {original_message}
            あなたのチーム: {pre_battle_your_teams}
            相手のチーム: {pre_battle_opponent_teams}
            あなたの現在のポケモン: {your_current_pokemon_name}
            相手の現在のポケモン: {opponent_current_pokemon_name}

            ## 修正例（これらはあくまでも修正例です！)
            ### Case1
            これは opposing とあるので相手のポケモンが倒れた様子です。ポケモン名はキラフロルです。
            空白が入っているので修正します。

            元のメッセージ: "The opposing キラ フロ ル fainted!"
            修正後のメッセージ: "The opposing キラフロル fainted!"

            ポケモン名と思われるものについて空白が入っている場合、その空白は取り除きましょう。

            ### Case2
            これは自分のポケモンが技を使用している様子です。ポケモン名がZEEEと読み取られています。
            このままでは修正が難しいので、自分のチーム情報及び現在のポケモン情報をもとに修正します。

            元のメッセージ: "ZEEE used Encorel"
            あなたのチーム: ['コライドン', 'バドレックス(黒馬)', 'キラフロル', 'ラグラージ', 'オーロンゲ', 'ヘイラッシャ']
            あなたの現在のポケモン: "バドレックス"
            修正後のメッセージ: "バドレックス used Encore"

            ### Case3
            これはトレーナーがポケモンを繰り出している様子です。トレーナ名はモニ ミニ ジ、ポケモン名はコライドンです。

            元のメッセージ: "モニ ミニ ジ sent out コラ イド ン !"
            修正後のメッセージ: "モニミニジ sent out コライドン!"

            ## 出力形式
            あなたは以下の形式で出力を行います。
            - internal_thinking_process: ポケモン対戦中に表示されるメッセージを修正する際のAIの内部思考過程を説明するテキスト
            - fixed_battle_message: ポケモン対戦中に表示されるメッセージを修正した結果のテキスト。できるだけ原型を保ちながら、空白や誤ったポケモン名を修正してください。
            """,
        )

        chain = prompt | model

        result = chain.invoke({
            "original_message": original_message,
            "pre_battle_your_teams": pre_battle_your_teams,
            "pre_battle_opponent_teams": pre_battle_opponent_teams,
            "your_current_pokemon_name": your_current_pokemon_name,
            "opponent_current_pokemon_name": opponent_current_pokemon_name,
        })
        typed_result = FixedBattleMessage.model_validate(result)
        return typed_result
