import os
import psycopg2
from dotenv import load_dotenv
from tabulate import tabulate

# Load envinronment variables from .env file.
load_dotenv()                                                  

PG_USER = os.environ.get('DB_USERNAME')
PG_PASSWORD = os.environ.get('DB_PASSWORD') 
PG_HOST = os.environ.get('DB_HOST') 
PG_NAME = os.environ.get('DB_NAME') 

# Create connection to postgres
connection = psycopg2.connect(
                        user=PG_USER,
                        password=PG_PASSWORD,
                        host=PG_HOST,
                        dbname=PG_NAME
                        )

cursor = connection.cursor()


# Get list of failed testcases
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
-- Use the sha to retrieve authors from git log sha1...sha2
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

# TODO: get authors of commits using sha from query2.
def get_author(sha_list):
    latest_sha = sha_list[0]
    previous_sha = sha_list[1]




#get_failed_tests_cases()