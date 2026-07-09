##deploy.py

import os
import subprocess
import snowflake.connector

# ----------------------------------
# Connect to Snowflake
# ----------------------------------

print("Connecting to Snowflake...")

conn = snowflake.connector.connect(
    account=os.environ["SNOWFLAKE_ACCOUNT"],
    user=os.environ["SNOWFLAKE_USER"],
    password=os.environ["SNOWFLAKE_PASSWORD"],
    warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
    role=os.environ["SNOWFLAKE_ROLE"]
)

cur = conn.cursor()

try:

    # ----------------------------------
    # Target database comes from workflow
    #
    # develop -> FIRST_TECH_DCU_D
    # main    -> FIRST_TECH_DCU_U
    # ----------------------------------

    target_db = os.environ["TARGET_DATABASE"]

    print(f"Deploying to {target_db}")

    cur.execute(f"USE DATABASE {target_db}")
    cur.execute("USE SCHEMA PUBLIC")

    # ----------------------------------
    # Get changed files between
    # current commit and previous commit
    #
    # Example:
    #
    # customer.sql modified
    # product.sql added
    #
    # Only these files are deployed
    # ----------------------------------

    changed_files = subprocess.check_output(
        [
            "git",
            "diff",
            "--name-only",
            "HEAD~1",
            "HEAD"
        ]
    ).decode().splitlines()

    # ----------------------------------
    # Deploy SQL files only
    # ----------------------------------

    sql_files = [
        f for f in changed_files
        if f.endswith(".sql")
    ]

    print("Changed SQL files:")

    for file_name in sql_files:
        print(file_name)

    # ----------------------------------
    # No SQL changes
    # ----------------------------------

    if not sql_files:
        print("No SQL files found for deployment.")
        exit(0)

    # ----------------------------------
    # Execute each changed SQL file
    # ----------------------------------

    for file_name in sql_files:

        print(f"Executing: {file_name}")

        with open(file_name, "r", encoding="utf-8") as f:
            sql_script = f.read()

        # Execute multiple statements
        cur.execute(
            sql_script,
            num_statements=0
        )

        print(f"Completed: {file_name}")

    print("Deployment Successful")

finally:

    cur.close()
    conn.close()

    print("Snowflake Connection Closed")
