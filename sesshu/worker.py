import os
import sys
import json
import yaml
import boto3
import logging

from sesshu import plugin
from sesshu import config
from sesshu import constant
from sesshu import message


def run(configuration):
    ''' Long-polls messages from the queue and dispatches them. '''
    config.validate(configuration)

    log = logging.getLogger(configuration['logging']['name'])
    sqs = boto3.client('sqs')
    sns = boto3.client('sns')

    # Poll until the heat death of the universe.
    log.info(
        'Starting long-poll loop for messages from {}'.format(
            configuration['bus']['input']['queue']
        )
    )

    while True:
        queue = sqs.receive_message(
            QueueUrl=configuration['bus']['input']['queue'],
            WaitTimeSeconds=configuration['workers']['polling']['interval']
        )

        try:
            messages = queue['Messages']
        except KeyError:
            log.info('No messages in queue, re-polling')
            continue

        # Iterate over polled messages, validate objects, and dispatch to the
        # relevant module.
        log.info('Got {} messages from the queue'.format(len(messages)))
        for i in xrange(0, len(messages)):
            mid = messages[i]['MessageId']
            handle = messages[i]['ReceiptHandle']

            # 'Body' is JSON, which contains 'Message' which is also JSON.
            log.info('[{}] Processing message body'.format(mid))
            try:
                body = json.loads(messages[i]['Body'])
                work = json.loads(body['Message'])
                message.validate_request(work)
            except (ValueError, AttributeError) as e:
                log.warn(
                    '[{}] deleting malformed message: {}'.format(mid, e)
                )
                continue

            # Provide some tracking / status for the logs.
            log.info(
                '[{}] Plugin {} requested for target {}'.format(
                    mid, work['plugin'], work['target']
                )
            )

            # Ensure the requested plugin exists and is enabled.
            if work['plugin'] not in configuration['plugin']:
                log.warn(
                    '[{}] {} is not a configured plugin'.format(
                        mid, work['plugin']
                    )
                )
                continue

            # Attempt to load the plugin.
            try:
                runner = getattr(plugin, work['plugin'])
            except AttributeError as x:
                log.error(
                    '[{}] Plugin {} failed: {}'.format(mid, work['plugin'], x)
                )
                continue

            # Validate and execute the plugin.
            try:
                runner.validate(work['target'])
                result = runner.fetch(work['target'])
            except AttributeError as x:
                log.error(
                    '[{}] Target is not compatible with plugin: {}'.format(
                        mid, x
                    )
                )
                continue

            # Serialize and submit result.
            if result is not None:
                log.info('[{}] Got results! Pushing reply.'.format(mid))
                sns.publish(
                    TopicArn=configuration['bus']['output']['topic'],
                    Message=json.dumps(
                        message.response(
                            work['target'], work['plugin'], result
                        )
                    )
                )

            # Delete.
            log.info('[{}] Message processed successfully'.format(mid))
            sqs.delete_message(
                QueueUrl=configuration['bus']['input']['queue'],
                ReceiptHandle=handle
            )
