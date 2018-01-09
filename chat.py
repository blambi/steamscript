#!/usr/bin/env python3
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests

CHAT_PAGE = "https://www.gamingonlinux.com/tools/rust_chat/"
TIMEOUT = timedelta(minutes=5)

class Chat:
    def __init__(self):
        self.last_fetched = None
        self.log = []
        self.fetch()

    def __convert_to_utc__(self, timestamp_string):
        local_format = "%Y-%m-%d %H:%M:%S"
        dt = datetime.strptime(timestamp_string, local_format)
        delta = timedelta(hours=-8) # Ugly hack for now
        dt -= delta
        return (dt.strftime(local_format), dt)

    def fetch(self):
        """Returns list of messages on site
        Returns something like:

        [
          (timestamp, nick, message)
          ...
        ]
        """
        resp = requests.get(CHAT_PAGE)

        if resp.status_code != 200:
            raise ValueError("Got status {} expected 200".format(resp.status_code))

        soup = BeautifulSoup(resp.content, 'html.parser')
        log = []

        for row in soup.find_all('tr')[1:]: # skip header
            log_row = []
            for column in row:
                log_row.append(column.text.strip())

            log_row[0] = self.__convert_to_utc__(log_row[0])
            log.append(log_row)

        log.reverse()
        self.log = log
        self.last_fetched = datetime.now()
        return log

    def poll(self):
        """Only fetch if timeout is reached othervise give old"""
        if self.last_fetched + TIMEOUT <= datetime.now():
            return self.fetch()
        else:
            return self.log


if __name__ == "__main__":
    from time import sleep
    print("Chat cat!")
    chat = Chat()

    while True:
        for row in chat.poll():
            print("{} <{}> {}".format(row[0][0], row[1], row[2]))
        sleep(5*60)
