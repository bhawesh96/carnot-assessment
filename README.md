# carnot-assessment

Flask based API server hosted on an EC2 instance. Configured Nginx and Gunicorn for serving the app.
Raw data from CSV file is parsed and the data is sorted on STS column. After this, it is loaded in the Redis cluster.
Keys are device IDs and the values are the device information in JSON format.

Hosted at http://54.163.216.242:8080

#### Run tester.py for interactive menu

#### API structure: 
- GET '/'

- GET '/get_all_data'\
 ``
 {
 	status,
 	data: {
 		<id>: [{id, lat, long, ts, sts}, {id, lat, long, ts, sts}]
 	}
 }
``
- GET '/get_info/<string:id>'\
 ``
 {
 	status,
 	data: {
 		id,
 		lat,
 		long,
 		ts,
 		sts
 	}
 }
``
- GET '/get_location/<string:id>'\
``
{
	status,
	data: {
		start: [lat, long],
		end: [lat, long]
	}
}
``
- GET '/get_time_based/<string:id>/<string:start_time>/<string:end_time>'\
``
{
	status,
	data: {
		lat,
		long,
		ts
	}
}
``
- GET '/load_data'\
``
{
	status
}
``
