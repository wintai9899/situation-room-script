import os
import psycopg2
from dotenv import load_dotenv
from tabulate import tabulate
from git import Repo
import subprocess

# Load envinronment variables from .env file.
load_dotenv()                                                  

PG_USER = os.environ.get('DB_USERNAME')
PG_PASSWORD = os.environ.get('DB_PASSWORD') 
PG_HOST = os.environ.get('DB_HOST') 
PG_NAME = os.environ.get('DB_NAME') 
YBD_REPO_PATH = os.environ.get('YBD_REPO_PATH')

repo = Repo(YBD_REPO_PATH)

connection = psycopg2.connect(
                        user=PG_USER,
                        password=PG_PASSWORD,
                        host=PG_HOST,
                        dbname=PG_NAME
                        )

cursor = connection.cursor()


def get_failed_tests_cases():
    
    query = """
            WITH latest_master AS(
                SELECT
                    id as build_id
                FROM ybd_builds
                WHERE git_branch = 'master'
                AND length(build_number) < 10
                ORDER BY id DESC
                limit 1
            )
            ,suite_runs AS (
                SELECT
                    S.suite_identity_id                  AS suite_identity_id
                    , S.id                               AS suite_id
                    , SI.name                            AS suite_name
                    , BLD.git_branch
                    , BLD.version || '-' || BLD.build_number AS build
                    , S.failed_test_runs_count           AS fail_count
                    , S.skipped_test_runs_count          AS skip_count
                    , S.passed_test_runs_count           AS pass_count
                    , M.hostname
                FROM suites S
                JOIN suite_identities SI ON S.suite_identity_id = SI.id
                JOIN invocations I ON S.invocation_id = I.id
                JOIN machine_configurations M ON I.machine_configuration_id = M.id
                JOIN ybd_builds BLD ON BLD.id = I.ybd_build_id
                JOIN latest_master LM on LM.build_id = I.ybd_build_id
                WHERE S.failed_test_runs_count > 0
            
            )
            , test_runs AS (
                SELECT
                    T.test_case_identity_id
                    , TI.name as test_cast_name
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
                , SR.fail_count                                 AS suite_failures
                , SR.pass_count                                 AS suite_passes
                , SR.suite_name || '/' || TR.test_cast_name     AS test_name
                , TR.status
                , TR.expected_status
                , TR.status_reason
            --  , TR.status_detail
                , SR.hostname
            --  , SR.git_branch
            --   , SR.build
            FROM suite_runs SR, test_runs TR
            limit 5;
            """ 
    
    cursor.execute(query)
    result = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description]
    
    table = tabulate(result, headers=colnames, tablefmt="grid")
    print(table)


# stored the sha of the latest build and latest - n build
def get_sha():
    sha_list = []
    query = """
                SELECT
                    git_sha,
                    max(id)    as id,
                    max(build_number)  as build_number,
                    max(version) as version
                FROM ybd_builds
                WHERE git_branch = 'master'
                AND length(build_number) < 10
                group by git_sha
                ORDER BY max(id) DESC
                limit 2;
            """
    cursor.execute(query)
    result = cursor.fetchall()
    for rec in result:
        sha_list.append(rec[0])
    
    return sha_list

# get author,email of commits using git hash from get_sha().
def get_commit_info(sha_list):

    author_info = []

    commit_hash_1, commit_hash_2= sha_list
    commits = repo.iter_commits(f'{commit_hash_1}...{commit_hash_2}')
    
    try:
        #committer_names = set(commit.committer.name for commit in commits)
        committer_names = set()
        
        for commit in commits:
            commit_info = {}
            author_name = commit.author.name
            author_email = commit.author.email

            if author_name not in committer_names and author_name != 'jenkins':
                commit_info['author'] = author_name
                commit_info['email'] = author_email
                #commit_info['date'] = commit.authored_datetime
                #commit_info['message'] = commit.message
                committer_names.add(author_name)
                author_info.append(commit_info)
            
            else:
                continue 
    
    except Exception as e:
        print(f'Error; {e}')
        return []
    
    return author_info


#get_commit_author_gitpython(get_sha())
# result = get_commit_info(['d350e75ad7adef091347587350beca8fd29d00c3','cb2ff30b347522e81610cd3bf758b0a864260f58'])
# print(result)

get_failed_tests_cases()
    

