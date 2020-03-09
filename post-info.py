#!/usr/bin/python3
from atlassian import Confluence
import os
from getpass import getpass
import requests
import urllib3
from collections import defaultdict
# import jinja2


class VirtRepo:
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.repos = list()
    
    def append(self, url):
        if url not in self.repos:
            self.repos.append(url)

urllib3.disable_warnings() # disable ssl varnings :)

wiki_url = os.getenv('WIKI_URL') #export WIKI_URL=https://wiki.x5.ru
if wiki_url is None:
    wiki_url = input("Wiki url: ")
wiki_username = os.getenv('WIKI_USER')
if wiki_username is None:
    wiki_username = input("Wiki username: ")
wiki_password = os.getenv('WIKI_PASSWORD')
if wiki_password is None:
    wiki_password = getpass("Wiki password: ")
wiki_page_id = os.getenv('WIKI_PAGE_ID')
if wiki_page_id is None:
    wiki_page_id = input("Wiki page id: ")
art_url = os.getenv('ART_URL')
if art_url is None:
    art_url = input("Artifactory url: ")

confluence = Confluence(
    url=wiki_url,
    username=wiki_username,
    password=wiki_password,
    verify_ssl=False) # TODO ssl verify

wiki_page = confluence.get_page_by_id(page_id=wiki_page_id, expand='body.editor')
curr_content = wiki_page['body']['editor']['value']

resp = requests.get(art_url + '/api/repositories', verify=False) # TODO ssl verify
resp.raise_for_status()
repositories = resp.json()

virt_repos = defaultdict(list)
for rep in repositories:
    if rep['type'] == 'VIRTUAL':
        vrepo = VirtRepo(name=rep['key'], url=rep['url'])
        resp = requests.get(art_url + '/api/repositories/' + rep['key'], verify=False) # TODO ssl verify
        resp.raise_for_status()
        for irep in resp.json()['repositories']:
            resp = requests.get(art_url + '/api/repositories/' + irep, verify=False) # TODO ssl verify
            resp.raise_for_status()
            if resp.json()['rclass'] == 'remote':
                vrepo.append(resp.json()['url'])
        virt_repos[rep['packageType']].append(vrepo)
    # elif rep['type'] == 'REMOTE':
# print(virt_repos)

