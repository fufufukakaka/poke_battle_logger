import os

from google.cloud import storage


class GCSHandler:
    def __init__(self) -> None:
        self.bucket_name = "poke_battle_logger_templates"
        self.client = storage.Client()
        self.bucket = self.client.get_bucket(self.bucket_name)

    def download_template_images(self, target_local_directory: str) -> None:
        gcs_directories = [
            "general_templates",
            "japanese_general_templates",
            "pokemon_name_window_templates",
            "pokemon_templates"
        ]

        for gcs_directory in gcs_directories:
            local_path = os.path.join(target_local_directory, gcs_directory)
            os.makedirs(local_path, exist_ok=True)

            # get file list in GCS
            blobs = self.client.list_blobs(self.bucket_name, prefix=gcs_directory)

            # download each files(if not exists)
            for blob in blobs:
                file_name = os.path.basename(blob.name)
                local_file_path = os.path.join(local_path, file_name)
                if not os.path.exists(local_file_path) or os.path.getsize(local_file_path) != blob.size:
                    blob.download_to_filename(local_file_path)
