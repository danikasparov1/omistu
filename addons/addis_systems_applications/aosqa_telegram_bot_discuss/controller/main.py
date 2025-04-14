import threading
import requests
from markupsafe import Markup
from bs4 import BeautifulSoup
from odoo.addons.mail.controllers.thread import ThreadController
from odoo import http
from odoo.addons.mail.models.discuss.mail_guest import add_guest_to_context
from odoo.tools import config
from odoo.http import request
import logging
import json


_logger = logging.getLogger(__name__)

class GitlabPushController(http.Controller):

    @http.route('/gitlab_message/post', type='json', auth="public", methods=['POST'])
    def gitlab_push(self):
        payload = json.loads(request.httprequest.data)
        if payload.get('object_kind') != "push":
            return {'status': 'success', 'message': 'Payload processed but not posted to channel because object kind is '+payload.get('object_kind')}

        # Extract details from the payload
        user_name = payload.get('user_name', '')
        commit_message = payload.get('commits', [{}])[0].get('message', 'No message')
        commit_url = payload.get('commits', [{}])[0].get('url', '')
        project_name = payload.get('project', {}).get('name', 'Unknown Project')
        project_url = payload.get('project', {}).get('web_url', '')
        
        # Prepare the message content
        message = Markup("""
            <b>GitLab Push Notification</b><br/>
            - <b>User:</b> {user_name}<br/>
            - <b>Project:</b> {project_name}<br/>
            - <b>Commit Message:</b> {commit_message}<br/>
            - <b>Commit URL:</b> <a href='{commit_url}'>Link</a><br/>
            - <b>Project URL:</b> <a href='{project_url}'>Link</a><br/>
            New Commit Detected :)
        """).format(
            user_name=user_name,
            project_name=project_name,
            commit_message=commit_message,
            commit_url=commit_url,
            project_url=project_url,
        )


        
        # Post the message to the Odoo Discussion Channel
        # Get the channel by its ID (replace CHANNEL_ID with  your actual channel ID)
        
        channel = request.env['discuss.channel'].sudo().search([('name','=','general')],limit=1)
        if channel.exists():
            # Send the message to the channel
            channel.message_post(body=message, message_type='comment', subtype_xmlid="mail.mt_comment")
        try:
            subtask_id=request.env["project.task"].sudo().search([("code","=",commit_message.split()[0])])
            partner = request.env["res.partner"].sudo().search([("gitlab_username",'=',payload.get('user_username', 'xlm'))],limit="1")
            vals={
                "sub_task_id" : subtask_id.id,
                "gitlab_event_type":"push",
                "gitlab_event_id":commit_url,
                "commit_message":commit_message,
                "gitlab_event_data":payload,
                "gitlab_project":project_name,
                "partner":partner.id
            }
            request.env["project.task.gitlab"].sudo().create(vals)
        except Exception as e:
            _logger.error(f"Error creating GitLab event record: {str(e)}")
            return {'status': 'success', 'message': 'Payload processed but not created in odoo Gitlab db'}
        _logger.info("Gitlab Payload Processed successfully")
        tg_channel=request.env['telegram.channel.discuss'].sudo().search([('odoo_disccuss','=',channel.id)],limit=1)
        CHAT_ID = tg_channel.telegram_channel.channel_id
        threading.Thread(target=send_message_in_thread, args=(CHAT_ID, "message from gitlab odoo\n"+commit_message+"\n"), daemon=True).start()
        return {'status': 'success', 'message': 'Payload processed and posted to channel'}


def send_message_in_thread(CHAT_ID, MESSAGE):
    """
    Sends a message to Telegram in a separate thread to avoid blocking Odoo.
    """
    try:
        bot_token = config['bot_token']
        telegram_bot_token = config['bot_token']
        url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": Markup(MESSAGE),
            "parse_mode": "MarkdownV2",  # Use 'HTML' if preferred
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            _logger.info("Message sent to Telegram Channel.")
        else:
            _logger.error(f"Failed to send message to Telegram: {response.content}")
    except Exception as e:
        _logger.error(f"Error while sending message to Telegram: {str(e)}")


class CustomThreadController(ThreadController):
    @staticmethod
    def strip_html_tags(html):
        """
        Strips HTML tags from the given text using BeautifulSoup.
        """
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text()
    
    


       
    
    @http.route("/mail/message/post", methods=["POST"], type="json", auth="public")
    @add_guest_to_context
    def mail_message_post(self, thread_model, thread_id, post_data, context=None):
        if thread_model == 'discuss.channel':
            tg_channel=request.env['telegram.channel.discuss'].sudo().search([('odoo_disccuss','=',thread_id)],limit=1)
            CHAT_ID = tg_channel.telegram_channel.channel_id
            user_name = request.env.user.name
            message_body = post_data.get('body', 'posted something ...')
            telegram_message = f"*{user_name}* sent a message:\n\n`{self.strip_html_tags(message_body)}`"
            if telegram_message:
                threading.Thread(target=send_message_in_thread, args=(CHAT_ID, telegram_message), daemon=True).start()
        return super(CustomThreadController, self).mail_message_post(thread_model, thread_id, post_data, context)
