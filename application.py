import os
import logging
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from fastapi import FastAPI, WebSocket, Request, Form, Response,HTTPException, Header

from dotenv import load_dotenv

import io
import wave
from fastapi.responses import JSONResponse
import asyncio
from time import time 
import json

from fastapi.websockets import WebSocketState,WebSocketDisconnect

from src.services.path_prediction import PathPredictor



load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s: [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Create the FastAPI instance with the configuration options
app_config = {
    'docs_url': None,  # Disable docs (Swagger UI)
    'redoc_url': None  # Disable redoc
}
application = FastAPI(
    title="Virtual Scale EOU API",
    version="1.0",
    **app_config
)

# CORS settings
origins = ["*"]  # Allows all origins; specify your frontend's domain for more security
application.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


EOU_API_KEY = os.getenv("EOU_API_KEY")

PORT = int(os.environ.get('PORT', 8080))

def authenticate(token: str):
    return token == EOU_API_KEY


path_prediction_model = PathPredictor()

@application.websocket("/v1/stream")
async def websocket_endpoint(websocket: WebSocket):
    
    #get the api key from the query params
    api_key = websocket.query_params.get("api_key")

    #verify the widget key, if not, it will try the public key, if not it will try the privatekey, if not , it will close the connection
    _is_valid = authenticate(token=api_key)

    #check if entity_id is valid
    if not _is_valid:
        await websocket.close(code=1008)
        raise HTTPException(status_code=403, detail="Invalid API key")
    

    try:
        
        #accept the connection
        await websocket.accept()

        while websocket.application_state == WebSocketState.CONNECTED and websocket.client_state == WebSocketState.CONNECTED:
            #await for data
            data = await websocket.receive_text()
            json_data = json.loads(data)
            user_input = (json_data.get("input",None))
            path_descriptions = (json_data.get("path_descriptions",None))

            if user_input is None or path_descriptions is None:
                await  websocket.send_text(json.dumps({"error": "Invalid input"}))
                continue


            before = time()

            selected_path,score = path_prediction_model.predict(user_input=user_input,path_descriptions=path_descriptions,threshold=0.3)

            after = time()
            calculation_time = after - before

            message = json.dumps({
                "path": selected_path,
                "score": round(score,3),
                "calculation_time": calculation_time
            })

            await websocket.send_text(message)


    except WebSocketDisconnect:
        print(f"WebSocket disconnected")
    except Exception as e:
        logging.error(f"Error in WebSocket connection: {e}", exc_info=True)
    finally:
        print(f"WebSocket connection closed")

        try:

            if websocket.application_state == WebSocketState.CONNECTED and websocket.client_state == WebSocketState.CONNECTED:
                #when websocket is open we close it
                await websocket.close()
            elif websocket.application_state == WebSocketState.DISCONNECTED:
                #when websocket is already closed
                pass
            else:
                #unkwown state of websocket
                logging.warning(f"websocket is in an invalid state: {str(websocket.client_state)}")

        except RuntimeError as e:
            if str(e) == 'Cannot call "send" once a close message has been sent.':
                pass
            else:
                logging.warning(f"Error when closing websocket {str(e)}")
                pass


@application.get("/")
def ELB_HealthChecker(request: Request, response: Response):
    try:
        client_ip = request.client.host
        attacker_ip = request.headers.get("x-forwarded-for",client_ip)
        attacker_user_agent = request.headers.get("user-agent","Unknown")
        message = {
            "detail":"Not Found",
            "detected_ip":attacker_ip,
            "detected_agent":attacker_user_agent,
            "Intruder message":"IP And user agent have been reported to admin"
        }
        return message
    except:
        logging.error("ERROR")
        raise HTTPException(status_code=500,detail="ERROR")
    
# @application.post("/v1/transcribe")
# async def transcribe_full_audio(
#     request: Request,
#     language: str = None,
#     model: str = None,
#     diarize: bool = False,
#     authorization: str = Header(None)
# ):
#     # Extract token from Authorization header
#     token = authorization.split()[-1] if authorization else None

#     if not token or not authenticate(token):
#         raise HTTPException(status_code=401, detail="Unauthorized")

#     # Get language from query parameters, defaulting to 'en'
#     language = language or 'en'
#     if language not in ['en', 'es']:
#         raise HTTPException(status_code=400, detail="Unsupported language")

#     try:
#         # Read raw binary data from the request body
#         contents = await request.body()

#         with io.BytesIO(contents) as buf, wave.open(buf, 'rb') as wav:
#             if wav.getnchannels() != 1 or wav.getsampwidth() != 2 or wav.getframerate() != 16000:
#                 return JSONResponse(status_code=400, content={"error": "Audio must be 16kHz mono PCM"})
            
#             audio_data = wav.readframes(wav.getnframes())

#         transcription = VoskBatchTranscription(language, diarize,size=model)

        
#         result = await transcription.transcribe(audio_data)

#         return JSONResponse(content=result)

#     except Exception as e:
#         logging.error(f"Error in transcribe_full_audio: {str(e)}", exc_info=True)
#         return JSONResponse(status_code=500, content={"error": "Internal server error"})

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(application, host="0.0.0.0", port=80,workers=1)