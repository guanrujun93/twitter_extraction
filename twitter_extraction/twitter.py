import socket
import sys
import requests
import requests_oauthlib
import json

ACCESS_TOKEN = '911896803754221568-LrHNQj2RkACJO4QSNX71UZ2fI6AJqWR'
ACCESS_SECRET = 'kyirWQoNxlB77ahbnOXnINajLuwF1QRW2ioeteJJRjqOs'
CONSUMER_KEY = '8pq1fogCzq7eGTmfN6LrBvq83'
CONSUMER_SECRET = 'ZRxdvAkCb66C8vAisdfHxsaf8qxrZmcnFKIfpxPpWQ6tOw5plO'
my_auth = requests_oauthlib.OAuth1(CONSUMER_KEY, CONSUMER_SECRET,ACCESS_TOKEN, ACCESS_SECRET)


def send_tweets_to_spark(http_resp, tcp_connection):
    for line in http_resp.iter_lines():
        try:
            full_tweet = json.loads(line)
            tweet_text = str(full_tweet['text'].encode("utf-8")) # pyspark can't accept stream, add '\n'
            print("Tweet Text: " + tweet_text)
            print ("------------------------------------------")
            tcp_connection.send(bytes(tweet_text+'\n','utf-8'))
        except:
            e = sys.exc_info()[0]
            print("Error: %s" % e)


def get_tweets():
    url = 'https://stream.twitter.com/1.1/statuses/filter.json'
    query_data = [('language', 'en'), ('locations', '-180,-90,180,90'),('track','python')]
  
    query_url = url + '?' + '&'.join([str(t[0]) + '=' + str(t[1]) for t in query_data])
    response = requests.get(query_url, auth=my_auth, stream=True)
    print(query_url, response)
    return response


TCP_IP = "localhost"
TCP_PORT = 9009
conn = None
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
print("Waiting for TCP connection...")
conn, addr = s.accept()
print("Connected... Starting getting tweets.")
resp = get_tweets()
send_tweets_to_spark(resp,conn)