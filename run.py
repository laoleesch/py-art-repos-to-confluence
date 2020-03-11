from atlassian import Confluence
import os
from getpass import getpass
import requests
import urllib3
from collections import defaultdict
from jinja2 import Environment, FileSystemLoader
import logging

logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', level='INFO')
logging.info('Started')

urllib3.disable_warnings() # disable ssl varnings :)

confluence_url = os.getenv('CONFLUENCE_URL')
if confluence_url is None:
    confluence_url = input("Confluence url: ")
confluence_username = os.getenv('CONFLUENCE_USER')
if confluence_username is None:
    confluence_username = input("Confluence username: ")
confluence_password = os.getenv('CONFLUENCE_PASSWORD')
if confluence_password is None:
    confluence_password = getpass("Confluence password: ")
confluence_page_id = os.getenv('CONFLUENCE_PAGE_ID')
if confluence_page_id is None:
    confluence_page_id = input("Confluence page id: ")
art_url = os.getenv('ARTIFACTORY_URL')
if art_url is None:
    art_url = input("Artifactory url: ")
template_file = os.getenv('TEMPLATE_FILE')
if template_file is None:
    template_file = os.path.expanduser(input("Template full file path (ENTER to skip): "))
blacklist_file = os.getenv('BLACKLIST_FILE')
if blacklist_file is None:
    blacklist_file = input("Blacklist full file path (ENTER to skip): ")

confluence = Confluence(
    url=confluence_url,
    username=confluence_username,
    password=confluence_password,
    verify_ssl=False) # TODO ssl verify

confluence_page = confluence.get_page_by_id(page_id=confluence_page_id, expand='storage')

resp = requests.get(art_url + '/api/repositories', verify=False) # TODO ssl verify
resp.raise_for_status()
repositories = resp.json()

blacklist = list()
if blacklist_file not in [None, '']: 
    with open(blacklist_file) as f:
        blacklist = [line.rstrip() for line in f]

# get all virt and remote repos
virt_repos = dict()
remote_repos = dict()
for rep in repositories:
    if rep['type'] == 'VIRTUAL':
        if rep['key'] not in blacklist:
            virt_repos[rep['key']] = rep
    elif rep['type'] == 'REMOTE':
        if rep['key'] not in blacklist:
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
if template_file in [None, '']: 
    template_file = 'page_template.html'
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(template_file))
jinja2_env = Environment(loader=FileSystemLoader(BASE_DIR), trim_blocks=True)
new_content = jinja2_env.get_template(os.path.basename(template_file)).render(all_repos=all_repos)

# post page on Confluence
confluence.update_page(confluence_page_id,confluence_page['title'],new_content)

logging.info('Finished')
