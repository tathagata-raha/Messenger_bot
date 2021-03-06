from .fb_requests import *
from .random_message import *
from .send_message import *
from .handle_nlp import *
from .handle_common import *

def send_message(db, recipient_id, text, message_rec, new_user):
    # sends user the text message provided via input response parameter
    """Send a response to Facebook"""
    if message_rec.get("quick_reply"):
        payload = handle_quickreply(db, recipient_id, message_rec["quick_reply"]["payload"])
    else:
        intent = handle_nlp(db, recipient_id, message_rec)
        if intent == "":
            intent = message_rec["text"]
        if intent == "Greeting":
            print("greeting2")
            payload = handle_greeting(recipient_id,new_user)
            db.flow_convo.update_one({"user": recipient_id}, {'$set' : {"tag":"greeting", "state": "null"}})
        elif intent == "Bye":
            payload = handle_bye(recipient_id)
            db.flow_convo.update_one({"user": recipient_id}, {'$set' : {"tag":"bye", "state": "null"}})
        elif intent == "Talk to someone":
            payload = talk_to_someone(recipient_id, db)
            db.flow_convo.update_one({"user": recipient_id}, {'$set' : {"tag" : "attachment"}})
            db.flow_convo.insert_one({"user":recipient_id,"tag":"talk to someone"})
        elif intent == "Book an appointment":
            payload = book_appointment("", recipient_id, db)
            db.flow_convo.insert_one({"user":recipient_id,"tag":"book_appointment"})
        elif intent == "color":
            payload = {
                "recipient": {"id": recipient_id},
                "messaging_type": "RESPONSE",
                "message": {"text": "Pick a color:", "quick_replies": replies["color"]},
            }
        elif intent == "url":
            payload = {
                "recipient": {"id": recipient_id},
                "messaging_type": "RESPONSE",
                "message": {"text": "Sorry, I don't support url sharing right now. I can give you urls if you want."},
            }
        elif intent == "Get a joke":
            payload = jokes_util(recipient_id,db)
            db.flow_convo.update_one({"user": recipient_id}, {'$set' : {"tag" : "attachment"}})
        elif intent == "Get a quote":
            payload = get_quotes(recipient_id)
            db.flow_convo.update_one({"user": recipient_id}, {'$set' : {"tag" : "attachment"}})
        elif intent == "Get music":
            payload = get_music(recipient_id)
            db.flow_convo.update_one({"user": recipient_id}, {'$set' : {"tag" : "attachment"}})
        elif intent == "Get yoga":
            payload = getYoga_displayed(recipient_id)
            db.flow_convo.update_one({"user": recipient_id}, {'$set' : {"tag" : "attachment"}})
        elif intent == "Get stories":
            payload = get_motiv_images(recipient_id)
            db.flow_convo.update_one({"user": recipient_id}, {'$set' : {"tag" : "attachment"}})
        elif intent == "Get memes":
            payload = get_meme(recipient_id)
            db.flow_convo.update_one({"user": recipient_id}, {'$set' : {"tag" : "attachment"}})
        elif intent == "Happy":
            payload = handle_happy(recipient_id)
            db.flow_convo.update_one({"user": recipient_id}, {'$set' : {"tag" : "Happy", "state": "Happy"}})
        elif intent == "Sad":
            payload = handle_sad(recipient_id)
            db.flow_convo.update_one({"user": recipient_id}, {'$set' : {"tag" : "Sad", "state": "Sad"}})
        elif intent == "Suicidal":
            payload = handle_suicidal(recipient_id)
            db.flow_convo.update_one({"user": recipient_id}, {'$set' : {"tag" : "Suicidal", "state": "Suicidal"}})
        elif intent == "handle_suicide2":
            payload = handle_suicide2(recipient_id)
        elif intent == "Sorry":
            payload = handle_sorry(recipient_id)
            db.flow_convo.update_one({"user": recipient_id}, {'$set' : {"tag" : "Sorry"}})
        elif intent == "Nice":
            payload = handle_nice(recipient_id)
        elif intent == "Hurt":
            payload = handle_hurt(recipient_id)
        elif intent == "Bot info":
            payload = bot_info(recipient_id)
        elif intent == "Sad negative":
            payload = handle_sad_negative(recipient_id)
            db.flow_convo.update_one({"user": recipient_id}, {'$set' : {"tag" : "Sad negative"}})
        elif intent == "Confused last question":
            payload = confused_last_question(recipient_id)
            db.flow_convo.update_one({"user": recipient_id}, {'$set' : {"tag" : "Confused last question"}})
        elif intent == "Didn't get":
            payload = didnt_get(recipient_id)
        else:
            payload = {
                "message": {"text": text},
                "recipient": {"id": recipient_id},
                "notification_type": "regular",
            }
    send_request(payload)

def handle_normal_message(db,recipient_id,message, new_user):
    # Facebook Messenger ID for user so we know where to send response back to
    if (message["message"].get("attachments")):
        payload = {
            "message": {"text": "Attachment not supported"},
            "recipient": {"id": recipient_id},
            "notification_type": "regular",
        }
        send_request(payload)
    if message["message"].get("text"):
        response_sent_text = get_message()
        send_message(
            db, recipient_id, response_sent_text, message["message"], new_user 
        )