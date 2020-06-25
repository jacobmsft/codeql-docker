from os import environ, mkdir, name as os_name
from subprocess import check_output, CalledProcessError
from sys import exit
import logging
from re import search
from datetime import datetime, MINYEAR
from zipfile import ZipFile
from shutil import rmtree
from github import Github, GitObject, GitRelease, Repository, Tag, GithubException

CODEQL_HOME = environ['CODEQL_HOME']
logger = logging.getLogger()
#logger.setLevel(logging.INFO)
CODEQL_GITHUB_URL = 'https://github.com/github/codeql-cli-binaries'
CODEQL_QUERIES_URL = 'https://github.com/github/codeql'
CODEQL_GO_QUERIES_URL = 'https://github.com/github/codeql-go'

TEMP_DIR ='/tmp'

# Error codes
ERROR_EXECUTING_COMMAND = 1
ERROR_EXECUTING_CODEQL = 2
ERROR_UNKNOWN_OS = 3
ERROR_GIT_COMMAND = 4

# get secrets from the env
def get_env_variable(self, var_name, optional=False):
    """
    Retrieve an environment variable. Any failures will cause an exception
    to be thrown.
    """
    try:
        return environ[var_name]
    except KeyError:
        if optional:
            return False
        else:
            error_msg = f'Error: You must set the {var_name} environment variable.'
            raise Exception(error_msg)

def check_output_wrapper(*args, **kwargs):
    """
        Thin wrapper around subprocess
    """

    logger.debug('Executing %s, %s', args, kwargs)
    try:
        return check_output(*args, **kwargs)
    except CalledProcessError as msg:
        logger.warning('Error %s,%s,%s from command.', msg.returncode, msg.output, msg.stderr)
        logger.debug('Output: %s', msg.output)
        sys.exit(ERROR_EXECUTING_COMMAND);

def setup():
    """
    Download and install the latest codeql cli
    Download and install the latest codeql queries
    """

    # check version and download the latest version
    get_latest_codeql()
    # install vscode?
    # clone codeql libs
    # setup vscode + codeql
    # wait for user


def get_latest_codeql():
    # what version do we have?
    current_installed_version = get_current_version()
    logger.info(f'Current codeql version: {current_installed_version}')
    latest_online_version = get_latest_codeql_github_version()
    if current_installed_version != latest_online_version.title:
        # we got a newer version online, download and install it
        download_and_install_latest_codeql(latest_online_version)
    # get the latest queries regardless (TODO: Optimize by storing and checking the last commit hash?)
    download_and_install_latest_codeql_queries()

def get_current_version():
    ret_string = check_output_wrapper(f'{CODEQL_HOME}/codeql-cli/codeql/codeql version', shell=True).decode("utf-8")
    if ret_string is CalledProcessError:
        logger.error("Could not run codeql command")
        sys.exit(ERROR_EXECUTING_CODEQL)
    version_match = search("Version: ([0-9.]+)\.", ret_string)
    if not version_match:
        logger.error("Could not determine existing codeql version")
        sys.exit(ERROR_EXECUTING_CODEQL)
    version = f'v{version_match.group(1)}'
    return version

def get_latest_codeql_github_version():
    client = Github()
    repo = client.get_repo("github/codeql-cli-binaries")
    releases = repo.get_releases()
    latest_release = get_latest_github_release(releases)
    return latest_release

def get_latest_github_release(releases):
    latest_release = None
    latest_date = datetime(MINYEAR, 1, 1)
    for release in releases:
        if release.created_at > latest_date:
            latest_date = release.created_at
            latest_release = release
    return latest_release

def download_and_install_latest_codeql(github_version):
    download_url = None
    download_path = None
    if os_name == 'posix':
        download_url = f'https://github.com/github/codeql-cli-binaries/releases/download/{github_version.title}/codeql-linux64.zip'
        download_path = f'{TEMP_DIR}/codeql_linux.zip'
    elif os_name == 'nt':
        download_url = f'https://github.com/github/codeql-cli-binaries/releases/download/{github_version.title}/codeql-win64.zip'
        download_path = f'{TEMP_DIR}/codeql_windows.zip'
    else:
        sys.exit(ERROR_UNKNOWN_OS)

    logger.info(f'Downloading codeql-cli version {github_version.title}...')
    check_output_wrapper(f"wget -q {download_url} -O {download_path}", shell=True).decode("utf-8")
    install_codeql_cli(download_path)
    #rm /tmp/codeql_linux.zip

def install_codeql_cli(download_path):
    logger.info("Installing codeql-cli...")
    codeql_dir = f'{CODEQL_HOME}/codeql-cli'
    wipe_and_create_dir(codeql_dir)
    ret1 = check_output_wrapper(f'unzip {download_path} -d {codeql_dir}', shell=True)

def download_and_install_latest_codeql_queries():
    logger.info("Downloading codeql queries...")
    codeql_repo_dir = f'{CODEQL_HOME}/codeql-repo'
    wipe_and_create_dir(codeql_repo_dir)
    ret1 = check_output_wrapper(f'git clone {CODEQL_QUERIES_URL} {codeql_repo_dir}', shell=True)

    codeql_go_repo_dir = f'{CODEQL_HOME}/codeql-go-repo'
    wipe_and_create_dir(codeql_go_repo_dir)
    ret2 = check_output_wrapper(f'git clone {CODEQL_GO_QUERIES_URL} {codeql_go_repo_dir}', shell=True)
    if ret1 is CalledProcessError or ret2 is CalledProcessError:
        logger.error("Could not run git command")
        sys.exit(ERROR_GIT_COMMAND)

def wipe_and_create_dir(dirname):
    rmtree(dirname)
    mkdir(dirname)

setup()

