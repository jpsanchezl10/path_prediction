from sentence_transformers import SentenceTransformer, util
import time
from transformers import pipeline
# 1. Load a small, fast model for creating embeddings
# model_name = "sentence-transformers/all-MiniLM-L6-v2


# Load the zero-shot classification pipeline with a model that has LLM-like reasoning capabilities.
#models:
# model = "BAAI/bge-reranker-v2-m3"

class PathPredictor:
    def __init__(self, model_name="FacebookAI/roberta-large-mnli"):


        self.classifier = pipeline("zero-shot-classification", model=model_name)

    def classify_response(self,candidates, user_answer, threshold=0.5):
        """
        Classify the user's answer using a zero-shot classification model.
        
        Parameters:
            candidates (dict): A dictionary where keys are candidate labels (e.g., "A") and values are candidate descriptions.
            user_answer (str): The answer provided by the user.
            threshold (float): The minimum confidence score required to assign a candidate.
        
        Returns:
            The key corresponding to the candidate that best matches the user's answer, or None if no match exceeds the threshold.
        """
        candidate_labels = list(candidates.values())
        
        # Classify the user answer against the candidate descriptions.
        result = self.classifier(user_answer, candidate_labels)
        
        # Debug output: display the top candidate label and its score.
        top_label = result['labels'][0]
        top_score = result['scores'][0]

        # print(f"User Answer: '{user_answer}'")
        # print(f"Top label: {top_label} with score: {top_score:.4f}")
        
        # If the highest score is above our threshold, return the corresponding candidate key.
        if top_score >= threshold:
            for key, description in candidates.items():
                if description == top_label:
                    return key, top_score
        # Otherwise, return None and the top score.
        return None, top_score