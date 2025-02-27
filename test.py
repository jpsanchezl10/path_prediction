
from src.services.path_prediction import PathPredictor
import time

model = PathPredictor()



# 2. Define your path descriptions (for each path, create a short text describing it)
path_descriptions = {
    "A": "The user wants the first option, or something that sounds like Option A.",
    "B": "The user wants the second option, or something that sounds like Option B.",
    "C": "The user wants the third option, or something that sounds like Option C."
}

# ------------------------------ Testing -------------------------------
while True:
    user_input = input("User says: ")
    if not user_input:
        break
    start_time = time.time()

    selected_path = model.predict(user_input=user_input,path_descriptions=path_descriptions)

    end_time = time.time()
    print(f"Computed similarities in {end_time - start_time} seconds.")
    print(f"Chosen path: {selected_path}")
