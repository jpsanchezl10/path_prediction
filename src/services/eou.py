from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
import string
import os
import json
from huggingface_hub import hf_hub_download
import logging

class EOUPredictor:
    def __init__(self, model_dir="src/models/eou_tuned_model-en", hf_repo="virtualscale/eou-prediction-en"):
        """
        Initializes the EOUPredictor.

        Args:
            model_dir (str): Path to the local model directory.
            hf_repo (str): Hugging Face repository name for the model.
        """
        self.hf_repo = hf_repo

        # Check if the local model directory exists
        if os.path.isdir(model_dir):
            load_dir = model_dir
            phrases_path = os.path.join(model_dir, "phrases.json")
            logging.info(f"Loading model from local directory: {load_dir}")
        else:
            load_dir = hf_repo
            try:
                # Download phrases.json from Hugging Face repository
                phrases_path = hf_hub_download(repo_id=hf_repo, filename="phrases.json")
                logging.info(f"Loading model from Hugging Face repository: {load_dir}")
            except Exception as e:
                logging.info(f"Error downloading phrases.json from Hugging Face: {e}")
                phrases_path = None

        # Load tokenizer and model
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(load_dir)
            self.model = AutoModelForSequenceClassification.from_pretrained(load_dir)
        except Exception as e:
            raise ValueError(f"Error loading model or tokenizer from {load_dir}: {e}")

        # Define punctuation to remove (excluding apostrophes)
        self.puncs = string.punctuation.replace("'", "")

        # Load trained phrases if phrases_path is available
        if phrases_path and os.path.isfile(phrases_path):
            try:
                with open(phrases_path, "r", encoding="utf-8") as f:
                    phrases = json.load(f)
                self.complete_phrases = phrases.get('complete_phrases', [])
                self.incomplete_phrases = phrases.get('incomplete_phrases', [])
                logging.info("Successfully loaded phrases.json.")
            except Exception as e:
                logging.info(f"Error loading phrases.json: {e}")
                self.complete_phrases = []
                self.incomplete_phrases = []
        else:
            logging.info("phrases.json not found. Initializing empty phrase lists.")
            self.complete_phrases = []
            self.incomplete_phrases = []

    def _normalize_text(self, text):
        """
        Normalizes the input text by removing specified punctuation and converting to lowercase.

        Args:
            text (str): The text to normalize.

        Returns:
            str: The normalized text.
        """
        text = text.translate(str.maketrans("", "", self.puncs))
        return " ".join(text.lower().split())

    def _format_conversation(self, messages):
        """
        Formats a list of messages into a single string suitable for model input.

        Args:
            messages (list): List of message dictionaries with 'role' and 'content'.

        Returns:
            str: The formatted conversation string.
        """
        formatted_texts = []
        for msg in messages:
            if isinstance(msg.get("content"), str):
                content = self._normalize_text(msg["content"])
                if content:
                    role = msg.get("role", "user")
                    if role == "user":
                        formatted_texts.append(f"User: {content}")
                    else:
                        formatted_texts.append(f"Assistant: {content}")
        return " ".join(formatted_texts)

    async def predict_eou(self, messages):
        """
        Predicts the probability that the conversation has ended.

        Args:
            messages (list): List of message dictionaries with 'role' and 'content'.

        Returns:
            float: Probability between 0.0 and 1.0 indicating the likelihood of conversation ending.
        """
        # Format the conversation text
        text = self._format_conversation(messages)
        if not text:
            # print("No valid text to predict.")
            logging.warning("No valid text to predict.")
            return 0.0  # Default to 0.0 if there's no text

        # Tokenize the input text
        inputs = self.tokenizer(text, return_tensors="pt", add_special_tokens=True)

        # Perform inference without tracking gradients
        with torch.no_grad():
            try:
                outputs = self.model(**inputs)
                logits = outputs.logits
                probs = torch.softmax(logits, dim=-1)
                complete_prob = probs[0][1].item()  # Probability of label '1' (complete)
                # print(f"Prediction probability: {complete_prob}")
            except Exception as e:
                logging.error(f"Error during model inference: {e}")
                return 0.0  # Default to 0.0 in case of error

        return complete_prob  # Value between 0.0 and 1.0
