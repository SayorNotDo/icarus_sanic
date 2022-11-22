from confluent_kafka import Producer


def deliver_report(err, msg):
    if err is not None:
        print("message delivery failed: {}".format(err))
    else:
        print("message delivered to {} [{}]".format(msg.topic(), msg.partition()))


if __name__ == '__main__':
    p = Producer({"bootstrap.servers": '127.0.0.1:9092'})
    p.poll(0)
    p.produce("test", "test_log".encode("utf-8"), callback=deliver_report)

    # wait for any outstanding messages to be delivered and delivery report
    # callbacks to be triggered
    p.flush()
