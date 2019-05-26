#!/usr/bin/env python

import json
import requests
from bs4 import BeautifulSoup

with open('base.xml', 'r') as base:
    feed = BeautifulSoup(base.read(), 'xml')

channel = feed.find('channel')

archive_page = '/archive'

while True:

    request = requests.get('https://www.thisamericanlife.org' + archive_page)
    archive = BeautifulSoup(request.content, 'html.parser')

    for episode_page in archive.select('header > a.goto-episode'):

        full_url = 'https://www.thisamericanlife.org' + episode_page['href']
        request = requests.get(full_url)
        episode = BeautifulSoup(request.content, 'html.parser')
        player_data = episode.select('script#playlist-data')[0]
        player_data = json.loads(player_data.get_text())

        title = feed.new_tag('title')
        title.string = player_data['title']

        link = feed.new_tag('link')
        link.string = full_url

        meta_pub_time = episode.select(
            'meta [property=\'article:published_time\']')[0]

        pub_date = feed.new_tag('pubDate')
        pub_date.string = meta_pub_time['content']

        summary = episode.select('meta [name=\'description\']')
        description = feed.new_tag('description')
        description.string = summary[0]['content']

        enclosure = feed.new_tag('enclosure')
        enclosure['url'] = player_data['audio']
        enclosure['type'] = 'audio/mpeg'

        item = feed.new_tag('item')
        item.append(title)
        item.append(link)
        item.append(enclosure)
        item.append(description)
        item.append(pub_date)

        channel.append(item)

    pager = archive.select('a.pager')

    if pager:
        archive_page = pager[0]['href']
    else:
        break

with open('feed.xml', 'w') as out:
    out.write(feed.prettify())
