import paho.mqtt.client as mqtt


def publish_message(broker, topic, message):
    client = mqtt.Client()
    client.connect(broker, 1883)
    rc = client.publish(topic, message)
    print(f'Message {message} sent to broker:{broker} on topic:{topic}')
    client.disconnect()


publish_message('localhost', 'test_hw', 'Hello from Python Example!')
