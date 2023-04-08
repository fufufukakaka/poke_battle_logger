import glob

import cloudpickle
import cv2
import faiss
import imgsim
import numpy as np
from tqdm.auto import tqdm


def main() -> None:
    vtr = imgsim.Vectorizer()
    vectors = {}
    pokemon_images = glob.glob("template_images/labeled_pokemon_templates/*.png")
    for path in tqdm(pokemon_images):
        img = cv2.imread(path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img2 = np.zeros_like(img)
        img2[:, :, 0] = gray
        img2[:, :, 1] = gray
        img2[:, :, 2] = gray
        vec0 = vtr.vectorize(img2)

        vectors[path.split("/")[-1].split(".")[0]] = vec0

    vec0 = list(vectors.values())[0]
    vector_array = np.array(list(vectors.values()))
    vector_array = np.reshape(vector_array, (len(vector_array), vec0.shape[0]))

    faiss_index = faiss.IndexFlatL2(vec0.shape[0])
    faiss_index.add(vector_array)
    vector_index = list(vectors.keys())

    faiss.write_index(faiss_index, "model/pokemon_image_faiss/pokemon_faiss_index")
    cloudpickle.dump(
        vector_index,
        open("model/pokemon_image_faiss/pokemon_faiss_index_vector_index", "wb"),
    )


if __name__ == "__main__":
    main()
