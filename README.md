# py-art-repos-to-confluence

Update Confluence page with actual list of public remote repos from Artifactory

## Parameters

Every parameter will be interactively asked.
Or you can put any of them in ENV:

```bash
export CONFLUENCE_URL=https://confluence.my.org
export CONFLUENCE_USER=User
export CONFLUENCE_PASSWORD=Password               #hided in input
export CONFLUENCE_PAGE_ID=999999999
export ARTIFACTORY_URL=https://artifactory.my.com
export BLACKLIST_FILE=blacklist.txt         #default
export TEMPLATE_FILE=./page_template.txt    #default
```

## Run once

```bash
git clone git@github.com:laoleesch/py-art-repos-to-confluence.git
cd py-art-repos-to-confluence
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
./run.py
```
