from kafka import KafkaConsumer, KafkaProducer
class Producer():
	def stop(self):
		self.stop_event.set()

	def run(self):
		producer = KafkaProducer(bootstrap_servers='localhost:9092')

		while not self.stop_event.is_set():
			producer.send('scrapy_url_store', b"how_are_you")
			producer.send('scrapy_url_store', b"are_you_there")

		producer.close()