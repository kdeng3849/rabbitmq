import json
import pika

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def listen(request):
    data = json.loads(request.body.decode('utf-8'))
    keys = data['keys']
    # msg = ""
    response = {}

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='hw4',
                            exchange_type='direct')

    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    for key in keys:
        channel.queue_bind(
            exchange='hw4', queue=queue_name, routing_key=key)


    def callback(ch, method, properties, body):
        print(" [x] %r:%r" % (method.routing_key, body))
        response['msg'] = body.decode('utf-8')
        # channel.stop_consuming()
        return response and channel.stop_consuming()
        # return msg


    channel.basic_consume(
        queue=queue_name, on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

    # if msg:
        # channel.stop_consuming()
    return JsonResponse(response)


@csrf_exempt
def speak(request):
    data = json.loads(request.body.decode('utf-8'))
    key = data['key']
    msg = data['msg']

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='hw4', exchange_type='direct')

    channel.basic_publish(
        exchange='hw4', routing_key=key, body=msg)
    print(" [x] Sent %r:%r" % (key, msg))

    connection.close()
    return JsonResponse({"status": "OK"})
