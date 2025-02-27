from sentence_transformers import SentenceTransformer, util
import time
# 1. Load a small, fast model for creating embeddings
# model_name = "sentence-transformers/all-MiniLM-L6-v2"


class PathPredictor:
    def __init__(self, model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):


        self.model = SentenceTransformer(model_name)


    def predict(self,user_input:str,path_descriptions:dict,threshold: float = 0.5):

        # 3. Pre-embed the path descriptions (so you only do this once)
        paths = list(path_descriptions.keys())  # ["A", "B", "C"]
        descriptions = list(path_descriptions.values())


        path_embeddings = self.model.encode(descriptions, convert_to_tensor=True)

        # 1. Embed the user input
        user_embedding = self.model.encode(user_input, convert_to_tensor=True)

        # 2. Compute similarities between user input and each path
        #    cos_sim returns a 1 x N tensor with similarity to each path
        similarity_scores = util.cos_sim(user_embedding, path_embeddings)[0]

        # 3. Find the highest similarity and its index
        best_score, best_idx = similarity_scores.max(dim=0)

        # 4. Convert to a float value
        best_score_val = best_score.item()

        if best_score_val >= threshold:
            chosen_path = paths[best_idx]
            return chosen_path,best_score_val
        else:
            return "none",best_score_val

