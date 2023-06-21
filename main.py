import os
import logging
import sys
from typing import List, Dict, TextIO

import psycopg2
from dotenv import load_dotenv
from tabulate import tabulate
from git import Repo
from slack import WebClient
from slack.errors import SlackApiError


# Load envinronment variables from .env file.
load_dotenv()                                                  
logging.basicConfig(level=logging.INFO)


PG_USER = os.environ.get("DB_USERNAME")
PG_PASSWORD = os.environ.get("DB_PASSWORD") 
PG_HOST = os.environ.get("DB_HOST") 
PG_NAME = os.environ.get("DB_NAME") 
YBD_REPO_PATH = os.environ.get("YBD_REPO_PATH")

BOT_TOKEN = os.environ.get("BOT_TOKEN")
USER_TOKEN = os.environ.get("USER_TOKEN")
CHANNEL = os.environ.get("CHANNEL")

repo = Repo(YBD_REPO_PATH)
client = WebClient(token=BOT_TOKEN)

connection = psycopg2.connect(
                        user=PG_USER,
                        password=PG_PASSWORD,
                        host=PG_HOST,
                        dbname=PG_NAME
                        )

cursor = connection.cursor()


def get_failed_tests_cases() -> str:
    """ Method to query for all failed test suites for current build """
    
    query = """
            WITH latest_master AS(
                SELECT
                    id as build_id
                FROM ybd_builds
                WHERE git_branch = 'master'
                AND length(build_number) < 10
                ORDER BY id DESC
                LIMIT 1
            )
            ,suite_runs AS (
                SELECT
                    S.suite_identity_id                      AS suite_identity_id
                    , S.id                                   AS suite_id
                    , SI.name                                AS suite_name
                    , BLD.git_branch
                    , BLD.version || '-' || BLD.build_number AS build
                    , S.failed_test_runs_count               AS fail_count
                    , S.skipped_test_runs_count              AS skip_count
                    , S.passed_test_runs_count               AS pass_count
                    , M.hostname
                FROM suites S
                JOIN suite_identities SI ON S.suite_identity_id = SI.id
                JOIN invocations I ON S.invocation_id = I.id
                JOIN machine_configurations M ON I.machine_configuration_id = M.id
                JOIN ybd_builds BLD ON BLD.id = I.ybd_build_id
                JOIN latest_master LM on LM.build_id = I.ybd_build_id
                WHERE S.failed_test_runs_count > 0
            
            )
            ,test_runs AS (
                SELECT
                    T.test_case_identity_id
                    , TI.name as test_case_name
                    , T.suite_id
                    , T.status
                    , T.expected_status
                    , T.status_reason
                    , T.status_detail
                FROM test_cases T
                JOIN test_case_identities TI on T.test_case_identity_id = TI.id
                JOIN suite_runs SR on T.suite_id = SR.suite_id
                WHERE T.status != T.expected_status
            )
            SELECT
                SR.suite_name
                , TR.test_case_name                             AS test_name
                , SR.fail_count                                 AS suite_failures
                , SR.pass_count                                 AS suite_passes
            --  , SR.suite_name || '/' || TR.test_cast_name     AS full_test_path
                , TR.status
                , TR.expected_status                            AS expected
            --  , TR.status_reason                              AS reason
            --  , TR.status_detail
                , SR.hostname
            --  , SR.git_branch
                , SR.build
            FROM suite_runs SR, test_runs TR
            """ 
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        if len(result) == 0:
            return ""
        else:
            colnames = [desc[0] for desc in cursor.description]
            table = tabulate(result, 
                            headers=colnames, 
                            tablefmt="grid",
                            )
            return table
    except Exception as e:
        logging.error("Error")
        return []
    

def get_sha() -> List[str]:
    """ Get git hash of the latest and latest-n build"""
    
    sha_list = []
    query = """
                SELECT
                    git_sha,
                    max(id)            as id,
                    max(build_number)  as build_number,
                    max(version)       as version
                FROM ybd_builds
                WHERE git_branch = 'master'
                AND length(build_number) < 10
                GROUP BY git_sha
                ORDER BY max(id) DESC
                LIMIT 2;
            """
    
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        for rec in result:
            sha_list.append(rec[0])
    except Exception as e:
        logging.error("Error: %s", str(e))
    
    return sha_list


def get_commit_info(sha_list: List[str]) -> List[Dict[str,str]]:
    """ Method to get committers info between two git hash"""

    if len(sha_list) < 2:
        return []

    author_info = []
    commit_hash_1,commit_hash_2 = sha_list
    
    try:
        committer_names = set()
        # git log commit_hash_1...commit_hash2
        commits = repo.iter_commits(f"{commit_hash_1}...{commit_hash_2}")
        for commit in commits:
            commit_info = {}
            author_name = commit.author.name
            author_email = commit.author.email

            if author_name not in committer_names and author_name != "jenkins":
                commit_info["author"] = author_name
                commit_info["email"] = author_email
                committer_names.add(author_name)
                author_info.append(commit_info)
            else:
                continue

        return author_info
    
    except ValueError as e:
        logging.error("Error: %s", str(e))
    except Exception as e:
        logging.error("Error: %s", str(e))
        logging.info("This error might be cause by reverted commits")

    
def save_table(table: TextIO) -> None:
    with open("table.txt", "w") as outputfile:
        outputfile.write(table)


def upload_file_to_slack(file: TextIO) -> None:
    """ Method to send table.txt to slack channel """
    
    try:
        response = client.files_upload(channels=CHANNEL, 
                                       file=file, 
                                       title="Failed test suites"
                                       )
        assert response["file"]        # the uploaded file
    except SlackApiError as e:
        logging.error(f"Got an error: {e.response['error']}")


def get_slack_users():
    try:
        response = client.users_identity(token=USER_TOKEN)
        slack_users = response['user']
    except SlackApiError as e:
        logging.error(f"Got an error: {e.response['error']}")
    
    return [slack_users]


def mention_relevevant_committers() -> None:
    git_hash_list = get_sha()
    committers_info = get_commit_info(git_hash_list) 
    committers_email = [info["email"] for info in committers_info]
    #print(committers_email)
    channel_users = get_slack_users()
    mention_users_str = ""
    
    if len(committers_info) == 0 or committers_info is None:
        logging.warning("There are no committers found or commiter not in current channel")
        return

    try:
        for user in channel_users: 
            if user["email"] in committers_email:
                user_id = user["id"]
                mention_users_str += "<@" + user_id + ">"

        response = client.chat_postMessage(token=BOT_TOKEN,
                                           channel=CHANNEL,
                                           as_user=True,
                                           text=mention_users_str
                                          )
    except SlackApiError as e:
        logging.warning("There are no committers found or commiter not in current channel")
        logging.error(e.response['error'])
    except Exception as e:
        logging.error(e)

# ignore, for testing purpose only. 
# def get_sha_test() -> List[str]:
#     temp = []
#     query = """
#                 SELECT
#                     git_sha,
#                     max(id)            as id,
#                     max(build_number)  as build_number,
#                     max(version)       as version
#                 FROM ybd_builds
#                 WHERE git_branch = 'master'
#                 AND length(build_number) < 10
#                 GROUP BY git_sha
#                 ORDER BY max(id) DESC
#                 LIMIT 4;
#             """
#     cursor.execute(query)
#     result = cursor.fetchall()
#     for rec in result:
#         temp.append(rec[0])
    
#     first_last_sha = [temp[0],temp[-1]] 
#     return first_last_sha

# def test_mention_relevevant_committers() -> None:
#     git_hash_list = get_sha_test()
#     committers_info = get_commit_info(git_hash_list) 
#     channel_users = [{'name': 'Wintai Chan', 'id': 'U057A8A3G49', 'email': 'wintai.chan@yellowbrick.com'},
#                      {'name': 'Maxence Menager', 'id': 'XXXXXXXXX', 'email': 'maxence.menager@yellowbrick.com'},
#                      {'name': 'Alexey Bashtanov', 'id': 'XXXXXXXXX', 'email': 'alexey.bashtanov@yellowbrick.com'},
#                      {'name': 'Xuezhou Wen', 'id': 'XXXXXXXXX', 'email': 'xuezhou.wen@yellowbrick.com'},
#                      {'name': 'Dmitry Sokolov', 'id': 'XXXXXXXXX', 'email': 'dmitry.sokolov@yellowbrick.com'},]
    
#     committers_email = [info["email"] for info in committers_info]
#     mention_users_str = ""
    
#     if len(committers_info) == 0 or committers_info is None:
#         logging.warning("There are no committers found or commiter not in current channel")
#         return

#     try:
#         for user in channel_users: 
#             if user["email"] in committers_email:
#                 user_id = user["id"]
#                 mention_users_str += "<@" + user_id + ">"

#         response = client.chat_postMessage(
#                                             token=BOT_TOKEN,
#                                             channel=CHANNEL,
#                                             as_user=True,
#                                             text = mention_users_str
#                                         )
    
#     except SlackApiError as e:
#         logging.warning("There are no committers found or commiter not in current channel")
#         logging.error(e.response['error'])

#     except Exception as e:
#         logging.error(e)

def main():
    failed_tests = get_failed_tests_cases()
    
    if len(failed_tests) == 0 or failed_tests is None:
        logging.info("There are no failed test suites")
        sys.exit(0)
    
    else:
        print(failed_tests)                     # print failed test suites result
        save_table(failed_tests)                # save result to table.txt
        mention_relevevant_committers()         # mention relevent committers in slack channel
        upload_file_to_slack('table.txt')       # send result to slack channel
    
    
if __name__ == "__main__":
    main()

    

