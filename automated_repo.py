from git import Repo
from git.exc import GitCommandError, NoSuchPathError

import argparse
import logging
from json import loads

from os.path import exists
from os import access, chmod, W_OK

from tempfile import mkdtemp as maketempdir
from shutil import rmtree


logging.basicConfig(level=logging.DEBUG)

parser = argparse.ArgumentParser(
    description='Automate multiple repos management in a folder.')
parser.add_argument('command', type=str, choices=[
                    'clone', 'pull', 'backup'], help='The command to execute')
parser.add_argument('--file', type=str, dest='file',
                    default='repos.json', help='The file to parse')
parser.add_argument('--tag', '-t', dest='tag', action='append', default=[],
                    help='Specify the tags on which you want to execute the command')
parser.add_argument('--not-tag', '-nt', dest='not_tag', action='append',
                    default=[], help='Specify the tags to be ignored')
parser.add_argument('--repo', '-r', dest='repo', action='append', default=[],
                    help='Specify the repo on which you want to execute the command')
parser.add_argument('--not-repo', '-nr', dest='not_repo',
                    action='append', default=[], help='Specify the repo to be ignored')
parser.add_argument('--force', '-f', dest='force',
                    action='store_true', default=False, help='Force the command')

args = parser.parse_args()


def onerror(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    import stat
    # Is the error an access error?
    if not access(path, W_OK):
        chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise


def match_tags(tags: list):
    for tag in tags:
        if tag in args.tag:
            return True

    return False


def ignore_tags(tags: list):
    for tag in tags:
        if tag in args.not_tag:
            return True

    return False


def match_repo(repo: str):
    if repo in args.repo:
        return True

    return False


def ignore_repo(repo: str):
    if repo in args.not_repo:
        return True

    return False


def check(tags: list, repo: str):
    if args.repo is not []:
        if match_repo(repo):
            return True
    if args.tag is not []:
        if match_tags(tags):
            return True

    if args.tag is not [] or args.repo is not []:
        return False

    if args.not_repo is not []:
        if ignore_repo(repo):
            return False
    if args.not_tag is not []:
        if ignore_tags(tags):
            return False

    return True


if __name__ == '__main__':
    if exists(args.file):
        # Open the file, parse the json
        json = ''
        with open(args.file, 'r') as f:
            json = loads(f.read())

        if args.command == 'clone':
            # Clone every repo inside the file
            logging.debug('Action: clone')
            for repo in json:
                # Generate the destination folder
                name = ''
                dest = ''
                if repo['name'] == '':
                    # Get the name of the page and remove the eventual .git
                    name = repo['url'].split('/')[-1].replace('.git', '')
                else:
                    name = repo['name']

                if not check(repo['tags'], name):
                    logging.debug('Skipped ' + name)
                    continue

                if repo['subfolder'] == '':
                    dest = name
                else:
                    dest = repo['subfolder'] + '/' + name

                try:
                    Repo.clone_from(repo['url'], dest)
                    logging.debug('Cloned ' + name)
                except GitCommandError as e:
                    if args.force:
                        logging.error('Couldn\'t clone ' +
                                      name + ', trying to pull')
                        try:
                            git_repo = Repo(dest)
                            git_repo.remotes[0].pull()
                            logging.debug('Pulled ' + name)
                        except GitCommandError as e2:
                            logging.exception(e2)
                    else:
                        logging.exception(e)

        if args.command == 'pull':
            # Pull every repo inside the file
            logging.debug('Action: pull')
            for repo in json:
                # Generate the destination folder
                name = ''
                dest = ''
                if repo['name'] == '':
                    # Get the name of the page and remove the eventual .git
                    name = repo['url'].split('/')[-1].replace('.git', '')
                else:
                    name = repo['name']

                if not check(repo['tags'], name):
                    logging.debug('Skipped ' + name)
                    continue

                if repo['subfolder'] == '':
                    dest = name
                else:
                    dest = repo['subfolder'] + '/' + name

                try:
                    git_repo = Repo(dest)
                    git_repo.remotes[0].pull()
                    logging.debug('Pulled ' + name)
                except NoSuchPathError as e:
                    if args.force:
                        logging.error('Couldn\'t pull ' +
                                      name + ', trying to clone')
                        try:
                            Repo.clone_from(repo['url'], dest)
                            logging.debug('Cloned ' + name)
                        except GitCommandError as e2:
                            logging.exception(e2)
                    else:
                        logging.exception(e)

        if args.command == 'backup':
            # Pull every repo inside the file
            logging.debug('Action: backup')
            for repo in json:
                # Generate the destination folder
                name = ''
                if repo['name'] == '':
                    # Get the name of the page and remove the eventual .git
                    name = repo['url'].split('/')[-1].replace('.git', '')
                else:
                    name = repo['name']

                if not check(repo['tags'], name):
                    logging.debug('Skipped ' + name)
                    continue

                if args.force:
                    # Create a temporary dir to download the repos to
                    dirpath = maketempdir(prefix='automated_repo')
                    try:
                        # Clone and archive
                        git_repo = Repo.clone_from(
                            repo['url'], dirpath + '/' + name)
                        with open(name + '.tar', 'wb+') as f:
                            git_repo.archive(f)
                        logging.debug('Backed up ' + name)
                    except GitCommandError as e:
                        logging.exception(e)
                    # For weird reasons, some git files are not deletable.
                    rmtree(dirpath, onerror=onerror, ignore_errors=True)

                else:
                    try:
                        git_repo = Repo(dest)
                        with open(name + '.tar', 'wb+') as f:
                            git_repo.archive(f)
                        logging.debug('Backed up ' + name)
                    except NoSuchPathError as e:
                        logging.exception(e)
