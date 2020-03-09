#!/usr/bin/python3
from atlassian import Confluence
import os
from getpass import getpass
import requests
import urllib3
from collections import defaultdict
from jinja2 import Environment, FileSystemLoader

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
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
# curr_content = wiki_page['body']['editor']['value']

resp = requests.get(art_url + '/api/repositories', verify=False) # TODO ssl verify
resp.raise_for_status()
repositories = resp.json()

# get all virt and remote repos
virt_repos = dict()
remote_repos = dict()
for rep in repositories:
    if rep['type'] == 'VIRTUAL':
        virt_repos[rep['key']] = rep
    elif rep['type'] == 'REMOTE':
        remote_repos[rep['key']] = rep

# from all virt repos pop remote repos
all_repos = dict(dict(list()))
for vname, vrep in virt_repos.items():
    resp = requests.get(art_url + '/api/repositories/' + vname, verify=False) # TODO ssl verify
    resp.raise_for_status()
    remotes = list()
    for irep in resp.json()['repositories']:
        if irep in remote_repos.keys():
            remotes.append(remote_repos[irep]['url'])
            del remote_repos[irep]
    all_repos.setdefault(vrep['packageType'], {})[vrep['url']] = remotes

# get all remained remote repos
for _, rrep in remote_repos.items():
    all_repos.setdefault(rrep['packageType'], {})[art_url + '/' + rrep['key']] = [rrep['url']]

# generate page from template

jinja2_env = Environment(loader=FileSystemLoader(BASE_DIR), trim_blocks=True)
new_content = jinja2_env.get_template('page_template.html').render(all_repos=all_repos)

# post page on wiki
confluence.update_page(wiki_page_id,wiki_page['title'],new_content)

print('Done')
