import glob

from google.cloud import storage


class GCSHandler:
    def __init__(self) -> None:
        self.bucket_name = "poke_battle_logger_templates"
        self.client = storage.Client()
        self.bucket = self.client.get_bucket(self.bucket_name)

    def upload_unknown_pokemon_templates_to_gcs(self):
        """
        
        """
        for path in glob.glob("template_images/unknown_pokemon_templates/*"):
            blob = self.bucket.blob(path)
            blob.upload_from_filename(path)
