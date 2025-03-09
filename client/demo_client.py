import asyncio
import os
import json
import websockets
from websockets.exceptions import ConnectionClosedError, InvalidURI
import time


path_descriptions = {
    "A": "When the lead asks for the finance support",
    "B": "When the lead asks for the technical support",
    "C": "When the lead asks for the customer support"
}


async def communicate_with_websocket():
    """
    Establishes a WebSocket connection, sends JSON messages for each user input,
    and processes the server's response, continuing until user presses Enter.
    """
    # Retrieve the API key from environment variables (or use default if not set)
    PATH_API_KEY = os.getenv("PATH_API_KEY") or "sk-A6878SHFDJLFDNDZuFDSJL8sZxJLFS790SDFJLzDz-Mc8790SDFLLZ44hJLSFD897894qg-FSJF89AA"

    # Define the WebSocket URI
    uri = f"wss://path-prediction.virtualscale.xyz/v1/stream?api_key={PATH_API_KEY}"

    try:
        # Establish the WebSocket connection
        async with websockets.connect(uri) as websocket:
            print(f"Connected to {uri}")

            # Continuously prompt for user input until empty
            while True:
                user_input = input("User says: ")

                # If the user presses Enter with no text, exit
                if not user_input:
                    print("No input provided. Closing connection...")
                    break

                # Prepare the message to send
                message = {
                    "input": user_input,
                    "path_descriptions": path_descriptions
                }
                message_json = json.dumps(message)

                start_time = time.time()
                # Send the JSON message
                await websocket.send(message_json)
                print("Sent!")

                # Wait for the server's response
                response = await websocket.recv()
                end_time = time.time()
                print(f"Time taken: {end_time - start_time}")
                response_data = json.loads(response)

                print(f"Raw response received: {response_data}")

    except ConnectionClosedError as e:
        print(f"Connection was closed unexpectedly: {e}")
    except InvalidURI as e:
        print(f"The WebSocket URI is invalid: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def main():
    """
    The main entry point for the script.
    """
    try:
        asyncio.run(communicate_with_websocket())
    except Exception as e:
        print(f"Failed to communicate with WebSocket: {e}")

if __name__ == "__main__":
    main()
