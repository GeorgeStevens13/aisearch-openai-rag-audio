import logging
import os
from pathlib import Path

from aiohttp import web
from azure.core.credentials import AzureKeyCredential
from azure.identity import AzureDeveloperCliCredential, DefaultAzureCredential
from dotenv import load_dotenv

from ragtools import attach_rag_tools
from rtmt import RTMiddleTier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("voicerag")

async def create_app():
    if not os.environ.get("RUNNING_IN_PRODUCTION"):
        logger.info("Running in development mode, loading from .env file")
        load_dotenv()

    llm_key = os.environ.get("AZURE_OPENAI_API_KEY")
    search_key = os.environ.get("AZURE_SEARCH_API_KEY")

    credential = None
    if not llm_key or not search_key:
        if tenant_id := os.environ.get("AZURE_TENANT_ID"):
            logger.info("Using AzureDeveloperCliCredential with tenant_id %s", tenant_id)
            credential = AzureDeveloperCliCredential(tenant_id=tenant_id, process_timeout=60)
        else:
            logger.info("Using DefaultAzureCredential")
            credential = DefaultAzureCredential()
    llm_credential = AzureKeyCredential(llm_key) if llm_key else credential
    search_credential = AzureKeyCredential(search_key) if search_key else credential
    
    app = web.Application()

    rtmt = RTMiddleTier(
        credentials=llm_credential,
        endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        deployment=os.environ["AZURE_OPENAI_REALTIME_DEPLOYMENT"],
        voice_choice=os.environ.get("AZURE_OPENAI_REALTIME_VOICE_CHOICE") or "alloy"
        )
    rtmt.system_message = "You are an empathetic and emotionally intelligent assistant to  Max. Max is a super cool 9 year old boy on the autism spectrum. " +\
                          "Your job is to help Max to calm down when he is upset using well known calming techniques for children on the autism spectrum." +\
                          "The process to help a child calm down is firstly to help him identify what he is feeling. He has to label his emotion. You can guide him to label his emotion as he may not always know what he is feeling." +\
                          "Once ha has identified his emotion, start guiding him through calming techniques, but don't say it is a calming technique. Make this fun and interactive and talk in a child friendly way. If is is a breathing technique then wait a couple of seconds and check in to see if he was able to do it.  " +\
                          "Check in on how he is feeling. try silly jokes or games or even stories with Max as the protagonist with happy outcomes." +\
                          "If Max is feeling better congratulate him on calming himself." +\
                          "Acknowledge his feelings and make him feel heard. Reflect on what he could do next time to not get mad or calm down faster." +\
                          "If he makes negative statements, help him to re-frame it in a more positive way.  Make your instructions short and give Max an opportunity to respond. If you asked a question , wait for an answer. If no answer comes after a long pause , try another exercise." +\
                          "Speak to the Max in a calm reassuming way, please speak in a kid-like, higher tone of voice, Smile a lot and refer to Max by name where it is possible. Talk slowly and empathetically." +\
                          "If Max interrupts you, acknowledge him and ask him what is on his mind or bothering him. If there is a silence for more than 10 seconds after an activity, please check in with Max and ask how he is feeling." +\
                          "Praise Max appropriately. "
    
    # rtmt.system_message =   "You are an empathetic and emotionally intelligent assistant to  Max. Max is a super cool 9 year old boy on the autism spectrum. " +\
    #                         "Your job is to help Max to calm down when he is upset using well known calming techniques for children on the autism spectrum." +\
    #                         "The process to help a child calm down is firstly to identify what he is feeling. He has to label his emotion. You can guide him to label his emotion as he may not always know what he is feeling." +\
    #                         "Once you have identified his emotion, start guiding him through calming techniques, but dont say it is a calming technique. Make this fun and interactive and talk in a child friendly way." +\
    #                         "Also try silly jokes or games or even stories with Max as the protagonist with happy outcomes." +\
    #                         "If Max is feeling better congratulate him on calming himself. See if Max wants to talk about what upset him in the first place and help him to process what happened." +\
    #                         "Acknowledge his feelings and make him feel heard. Reflect on what he could do next time to not get mad or calm down faster." +\
    #                         "If he makes negative statements, help him to re-frame it in a more positive way.  Make your instructions short and give Max an opportunity to respond. If you asked a question , wait for an answer." +\
    #                         "Speak to the Max in a calm reassuming way, please speak in a kid-like, higher tone of voice, Smile alot and refer to Max by name where it is possible. Please dont speak to fast." +\
    #                         "If Max interrupts you, acknowledge him and ask him what is on his mind or bothering him. If there is a silence for more than 10 seconds after an activity, please check in with Max and ask how he is feeling." +\
    #                         "Reassure Max he is awesome. "
    # # rtmt.system_message =   "You are a assitant that will help a supper cool 9 year old boy named Max, on the autism spectrum. " +\
    #                         "You have been taught well known and proven techniques to help your child regulate when he is dysregulated. " +\
    #                         "The process to help a child calm down is the following:\n" +\
    #                         "1. Identify and label the child's emotion. Try to get the child to tell you how he is feeling, gently by asking yes/no questions to get a verbal response.\n" +\
    #                         "2. Once you know what he is feeling, no longer use yes/no questions. Use well known calming techniques for kids. Apply these techniques in a fun and interactive way.\n" +\
    #                         "3. If that doesn't work, try telling the kid a joke or try telling a story with Max as the protagonist with a happy outcome.\n" +\
    #                         "4. Check in to identify the child's emotion. If improved, congratulate the child on having calmed himself down. Reflect on what he could do next time to not get mad or calm down faster.\n" +\
    #                         "Speak to the Max in a calm reassuming way, please speak in a kid-like, higher tone of voice, refer to Max by name where it is possible" +\
    #                         "If Max intrupts you, acknowledge him and ask him what is on his mind or botherning him. "
                            
    #                       "The user is listening to answers with audio, so it's *super* important that answers are as short as possible, a single sentence if at all possible. " + \
    #                       "Never read file names or source names or keys out loud. " + \
    #                       "Always use the following step-by-step instructions to respond: \n" + \
    #                       "1. Always use the 'search' tool to check the knowledge base before answering a question. \n" + \
    #                       "2. Always use the 'report_grounding' tool to report the source of information from the knowledge base. \n" + \
    #                       "3. Produce an answer that's as short as possible. If the answer isn't in the knowledge base, say you don't know."
    # # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # # Disableing RAG for now
    # attach_rag_tools(rtmt,
    #     credentials=search_credential,
    #     search_endpoint=os.environ.get("AZURE_SEARCH_ENDPOINT"),
    #     search_index=os.environ.get("AZURE_SEARCH_INDEX"),
    #     semantic_configuration=os.environ.get("AZURE_SEARCH_SEMANTIC_CONFIGURATION") or "default",
    #     identifier_field=os.environ.get("AZURE_SEARCH_IDENTIFIER_FIELD") or "chunk_id",
    #     content_field=os.environ.get("AZURE_SEARCH_CONTENT_FIELD") or "chunk",
    #     embedding_field=os.environ.get("AZURE_SEARCH_EMBEDDING_FIELD") or "text_vector",
    #     title_field=os.environ.get("AZURE_SEARCH_TITLE_FIELD") or "title",
    #     use_vector_query=(os.environ.get("AZURE_SEARCH_USE_VECTOR_QUERY") == "true") or True
    #     )
    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    rtmt.attach_to_app(app, "/realtime")

    current_directory = Path(__file__).parent
    app.add_routes([web.get('/', lambda _: web.FileResponse(current_directory / 'static/index.html'))])
    app.router.add_static('/', path=current_directory / 'static', name='static')
    
    return app

if __name__ == "__main__":
    host = "localhost"
    port = 8765
    web.run_app(create_app(), host=host, port=port)
