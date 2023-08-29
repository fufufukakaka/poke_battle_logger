from typing import cast

from google.cloud import firestore  # type: ignore


class FirestoreHandler:
    def __init__(self) -> None:
        self.client = firestore.Client()

    def get_document(self, collection: str, document: str) -> dict[str, list[str]]:
        doc_ref = self.client.collection(collection).document(document)
        _res = cast(dict[str, list[str]], doc_ref.get().to_dict())
        return _res

    def update_document(self, collection: str, document: str, data: dict) -> None:
        doc_ref = self.client.collection(collection).document(document)
        doc_ref.update(data)

    def update_log_document(self, video_id: str, new_message: str) -> None:
        """poke_battle_logger_processing_log を蓄積するための関数

        Args:
            video_id (str): video_id
            new_message (str): new procesing log message
        """
        current_data: dict[str, list[str]] = self.get_document(
            "poke_battle_logger_processing_log", video_id
        )
        if current_data is None or new_message == "INFO: Read Video...":
            # Read Video の場合はログをリセットして記録し直す
            current_data = {"messages": []}
            # もし document が存在しない場合は、新しく document を作成する
            self.client.collection("poke_battle_logger_processing_log").document(
                video_id
            ).set(current_data)
            return

        current_data["messages"] = current_data["messages"] + [new_message]
        self.update_document(
            "poke_battle_logger_processing_log", video_id, current_data
        )

    def get_battle_video_detail_status_log(self, video_id: str) -> list[str]:
        """poke_battle_logger_processing_log から video_id に対応する status log を取得する関数

        Args:
            video_id (str): video_id

        Returns:
            list[str]: status log
        """
        return self.get_document("poke_battle_logger_processing_log", video_id)[
            "messages"
        ]
