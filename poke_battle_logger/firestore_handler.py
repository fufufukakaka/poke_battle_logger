from google.cloud import firestore


class FirestoreHandler:
    def __init__(self) -> None:
        self.client = firestore.Client()

    def get_document(self, collection: str, document: str) -> dict:
        doc_ref = self.client.collection(collection).document(document)
        return doc_ref.get().to_dict()

    def update_document(self, collection: str, document: str, data: dict) -> None:
        doc_ref = self.client.collection(collection).document(document)
        doc_ref.update(data)

    def update_log_document(self, video_id: str, new_message: str) -> None:
        """ poke_battle_logger_processing_log を蓄積するための関数

        Args:
            video_id (str): video_id
            new_message (str): new procesing log message
        """
        current_data: dict[str, list[str]] = self.get_document("poke_battle_logger_processing_log", video_id)
        current_data["messages"] = current_data["messages"] + [new_message]
        self.update_document("poke_battle_logger_processing_log", video_id, current_data)
