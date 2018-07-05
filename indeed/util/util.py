import datetime


def total_time_in_second(start_time):
	current_time = datetime.datetime.utcnow()
	total_time = current_time-start_time
	total_time = total_time.total_seconds()
	print(type(total_time))
	return total_time