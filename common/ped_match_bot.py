import __builtin__
import inspect
import datetime
import time
import json
import os
import traceback
from string import Template
from slackclient import SlackClient
from celery.exceptions import MaxRetriesExceededError


class PedMatchBot(object):

    @staticmethod
    def send_message(attachments):
        SlackClient(__builtin__.slack_token).api_call(
            "chat.postMessage",
            token= (__builtin__.slack_token),
            channel=(__builtin__.environment_config[__builtin__.environment]['slack_channel_id']),

            username=__builtin__.environment_config[__builtin__.environment]['bot_name'],
            icon_emoji=__builtin__.environment_config[__builtin__.environment]['icon_emoji'],
            attachments = attachments
        )

    @staticmethod
    def upload_to_slack(message, id):
        task_id = str(id)
        upload_object = SlackClient(__builtin__.slack_token).api_call(
            "files.upload",
            as_user = "true",
            filename= task_id[:5]+ "_error_message",
            filetype="javascript",
            content= message,
        )
        return upload_object

    @staticmethod
    def return_slack_message_and_retry(queue_name, message, error_message, stack, task, logger, dlx_queue):
        requeue_countdown = (__builtin__.environment_config[__builtin__.environment]['requeue_countdown'])
        details = task.request
        message_output = json.dumps(message, indent=4, sort_keys=True)
        ts = time.time()
        pattern = '%Y-%m-%d %H:%M:%S'
        time_stamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        int_timestamp = int(time.mktime(time.strptime(time_stamp, pattern)))

        upload_json = PedMatchBot.upload_to_slack(message_output, details.id)
        json_url = upload_json["file"]["edit_link"]

        upload_stack = PedMatchBot.upload_to_slack(PedMatchBot.generate_traceback_message(stack), details.id)
        stack_url = upload_stack["file"]["edit_link"]


        filein = open(os.path.abspath("config/ped_match_bot_message.txt"))
        src = Template(filein.read())
        d = {'error_message': error_message, 'requeue_countdown': requeue_countdown, 'task_id': details.id,
             'stack_url': stack_url, 'json_url': json_url, 'queue_name': queue_name,
             'task_retries': details.retries,
             'task_hostname': details.hostname, 'time_stamp': int_timestamp
             }

        attachments = src.substitute(d)
        attachments = json.loads(attachments, strict=False)

        retry_attachments = [
            {
                "fallback": error_message,
                "color": "#ff0000",
                "pretext": error_message + "; \n Maximum retries reached, moving to to: " + queue_name + "_dlx.",
                "title": "Loggly Reference",
                "title_link": "https://match.loggly.com/search#terms=" + str(details.id),
                "text": "<" + str(stack_url) + "|Traceback Download> and <" + str(json_url) + "|JSON Download>",
                "fields": [
                    {
                        "title": "Project",
                        "value": "IR Ecosystem",
                        "short": "true"
                    },
                    {
                        "title": "Queue Name",
                        "value": queue_name,
                        "short": "true"
                    },
                    {
                        "title": "Task ID",
                        "value": str(details.id),
                        "short": "true"
                    },
                    {
                        "title": "Estimated Time of Arrival",
                        "value": str(details.eta),
                        "short": "true"
                    }
                ],

                "footer": "Host: " + str(details.hostname),
                "ts": int_timestamp
            }
        ]

        try:
            logger.error(str(details.task) + " has failed, details: " + str(details))
            PedMatchBot().send_message(attachments= attachments)
        except Exception as e:
            logger.error("Ped Match Bot Failure.: " + e.message)
        try:
            task.retry(args=[message], countdown=requeue_countdown)
        except MaxRetriesExceededError:
            logger.error("MAXIMUM RETRIES reached for %s moving task to %s details: %s" % (details.task, dlx_queue, details))
            PedMatchBot().send_message(retry_attachments)
            try:
                task.apply_async(args=[message], queue=dlx_queue)
            except Exception as e:
                logger.error("Unable to post to dead letter queue: %s" % e.message)

    @staticmethod
    def generate_traceback_message(stack):
        calling_function = inspect.stack()[1][3]
        error_traceback = traceback.format_exc()
        class_called = str(stack[1][0].f_locals["self"].__class__)
        ts = time.time()
        time_stamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        message_details = (
            "The class, %s and method %s were called at %s \n %s" %(class_called, calling_function, time_stamp,
                                                                          error_traceback)

        )
        return message_details

