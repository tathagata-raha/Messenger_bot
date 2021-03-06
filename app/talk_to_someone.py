from .data import *
from .fb_requests import *
from .send_message import *

code_of_conduct = "You can now chat live with your partner! Here's a list of instructions you can use to control your chat experiece\n1. /report - To report your partner and explain your issue to the admins\n2. /end - To end the conversation and return to the bot\n\nA few things to keep in mind:\n*Do not share sensitive info like address, locations, phone numbers, email-ids\n*Attachment sending is disabled for security purposes to avoid sharing of personal images etc.\n*Avoid using offensive speech as it may lead to blocking by admins\nHope you have an amazing chat experience!"


def sorry_text(db, minute_delta):
    for i in db.pool.find({}):
        if datetime.datetime.now() - i["timestamp"] > minute_delta:
            db.pool.remove({"id": i["id"]})
            print("yayy1")
            payload = {
                "recipient": {"id": i["id"]},
                "message": {
                    "text": "Sorry! We couldn't find anyone at this moment. Try again after some time."
                },
            }
            send_request(payload)


def talk_to_someone(recipient_id, db):
    userind = random.randint(0, len(anonymous_usernames) - 1)
    user_name = "Anonymous " + anonymous_usernames[userind]
    pool = db.pool.find({})
    print(user_name)
    if pool.count() == 0:
        print("Adding to pool")
        temp_pool = {
            "id": recipient_id,
            "timestamp": datetime.datetime.now(),
            "username": user_name,
            "image_url": persona_urls[userind],
        }
        db.pool.insert_one(temp_pool)

        payload = {
            "message": {
                "text": "Please wait for 1 min for us to pair you with someone else"
            },
            "recipient": {"id": recipient_id},
            "notification_type": "regular",
        }
        return payload
    else:
        print("Someone is there in pool")
        pool_id = pool[0]["id"]
        user1_blocked = db.blocked_users.distinct("blocked", {"user": recipient_id})
        user2_blocked = db.blocked_users.distinct("blocked", {"user": pool_id})
        if recipient_id in list(user2_blocked) or pool_id in list(user1_blocked):
            db.pool.remove({"id": pool_id})
            payload = {
                "recipient": {"id": pool_id},
                "message": {
                    "text": "Sorry! We couldn't find anyone at this moment. Try again after some time."
                },
            }
            send_request(payload)
            payload = {
                "recipient": {"id": recipient_id},
                "message": {
                    "text": "Sorry! We couldn't find anyone at this moment. Try again after some time."
                },
            }
            return payload
        else:
            partner_id = pool_id
            partner_username = pool[0]["username"]
            partner_pic = pool[0]["image_url"]
            if partner_id != recipient_id:
                # pool[:] = []
                db.pool.remove({"id": partner_id})
                persona_id_self = send_persona_request(
                    {"name": user_name, "profile_picture_url": persona_urls[userind]}
                )
                payload_partner = {
                    "message": {
                        "text": "Congrats! You have been paired with "
                        + str(user_name)
                        + ". Please take some time to go through our Code of Conduct and control instructions."
                    },
                    "recipient": {"id": partner_id},
                    "notification_type": "regular",
                    "persona_id": persona_id_self,
                }
                send_request(payload_partner)
                payload_next = {
                    "message": {"text": code_of_conduct},
                    "recipient": {"id": partner_id},
                    "notification_type": "regular",
                }
                send_request(payload_next)
                persona_id = send_persona_request(
                    {"name": partner_username, "profile_picture_url": partner_pic}
                )
                payload = {
                    "message": {
                        "text": "Congrats! You have been paired with "
                        + str(partner_username)
                        + ". Please take some time to go through our Code of Conduct and control instructions."
                    },
                    "recipient": {"id": recipient_id},
                    "notification_type": "regular",
                    "persona_id": persona_id,
                }
                print(persona_id_self, persona_id)
                db.user_status.update_one(
                    {"user": recipient_id}, {"$set": {"status": 10}}
                )
                send_request(payload)
                db.user_status.update_one(
                    {"user": partner_id}, {"$set": {"status": 10}}
                )
                db.paired_peeps.insert_one(
                    {
                        "fp": recipient_id,
                        "sp": partner_id,
                        "persona_id_sp": persona_id,
                        "persona_id_fp": persona_id_self,
                        "timestamp_fp": datetime.datetime.now(),
                        "timestamp_sp": datetime.datetime.now(),
                    }
                )
                payload_next = {
                    "message": {"text": code_of_conduct},
                    "recipient": {"id": recipient_id},
                    "notification_type": "regular",
                }
                return payload_next
            else:
                payload = {
                    "message": {
                        "text": "Please wait for 1 min for us to pair you with someone else"
                    },
                    "recipient": {"id": recipient_id},
                    "notification_type": "regular",
                }
                return payload
