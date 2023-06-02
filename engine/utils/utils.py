"""
Daksha
Copyright (C) 2021 myKaarma.
opensource@mykaarma.com
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.
You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

from github import Github
import yaml
import base64
from daksha.settings import STORAGE_PATH, GIT_USER, GIT_PASS, REPO_ORG, REPO_USER
from engine.logs import *


def git_login():
    if len(GIT_USER) == 0 or len(GIT_PASS) == 0:
        logger.info("Username OR password not given, mode is : public repository")
        github = Github()
        return get_org_instance(github, REPO_USER, REPO_ORG)
    else:
        github = Github(GIT_USER, GIT_PASS)
        return get_org_instance(github, REPO_USER, REPO_ORG)


def get_file_content(repo_name, branch_name, file_path):
    org = git_login()
    logger.info("Fetching the content from %s of %s branch %s ", file_path, repo_name, branch_name)
    repo = org.get_repo(repo_name)
    file_content = repo.get_contents(file_path, branch_name)
    return file_content


# Download the file from github
def download_file_content(file_content, test_uuid):
    content = base64.b64decode(file_content.content)
    ymlcontent = yaml.full_load(content)
    logger.info(ymlcontent)
    file_path = f"{STORAGE_PATH}/{test_uuid}/"

    try:
        with open(file_path + file_content.name, "w") as file:
            yaml.dump(ymlcontent, file)
            file.close()
        logger.info(file_content.name)
        logger.info("File %s downloaded", file_content.path)
    except IOError as exc:
        logger.error('Error creating file : %s', exc)


# read yaml file
def read_yaml(repo, branch, file_path, test_uuid):
    try:
        file_content = get_file_content(repo, branch, file_path)
        download_file_content(file_content, test_uuid)
        file_name = f"{STORAGE_PATH}/{test_uuid}/{file_content.name}"
        with open(file_name, 'r') as stream:
            yaml_content = yaml.full_load(stream)
            logger.info("Find your text file at location %s" % file_name)
            return yaml_content
    except Exception:
        logger.error("File %s is not present in %s branch of %s" % (file_path, branch, repo))
        return None


def read_local_yaml(file_path):
    with open(file_path, 'r') as stream:
        yaml_content = yaml.full_load(stream)
        return yaml_content


def get_org_instance(github, repo_user, repo_org):
    if len(repo_user) != 0 and len(repo_org) != 0:
        logger.error("Please provide either REPO_USER or REPO_ORG")
        raise Exception("Please provide either REPO_USER or REPO_ORG, terminating engine...")
    if len(repo_user) == 0 and len(repo_org) == 0:
        logger.error("Both REPO_USER or REPO_ORG are empty, please provide one")
        raise Exception("Both REPO_USER or REPO_ORG are empty, please provide one, terminating engine...")
    if len(repo_org) != 0:
        logger.info("REPO_ORG is present in config, accessing via : get_organization")
        org = github.get_organization(repo_org)
    else:
        logger.info("REPO_USER is present in config, accessing via : get_user")
        org = github.get_user(repo_user)
    return org


def get_yml_files_in_folder_local(folder_path):
    files = []
    for file in os.listdir(folder_path):
        if file.endswith(".yaml") or file.endswith(".yml"):
            file_path = os.path.join(folder_path, file)
            files.append(file_path)
    return files


def get_yml_files_in_folder_git(repo_name: str, branch_name: str, folder_path: str):
    org = git_login()
    logger.info("Fetching yml files from %s of %s branch %s ", folder_path, repo_name, branch_name)
    repo = org.get_repo(repo_name)
    contents = repo.get_contents(folder_path, branch_name)
    files = []
    for content in contents:
        if content.path.endswith(".yml"):
            files.append(content.path)
    return files
