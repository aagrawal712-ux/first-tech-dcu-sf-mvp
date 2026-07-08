import os
import subprocess
import snowflake.connector

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

    target_db = os.environ["TARGET_DATABASE"]

    print(f"Deploying to {target_db}")

    cur.execute(f"USE DATABASE {target_db}")
    cur.execute("USE SCHEMA PUBLIC")

    tags = subprocess.check_output(
        ["git", "tag", "--sort=-version:refname"]
    ).decode().splitlines()

    if len(tags) < 2:
        raise Exception(
            "Minimum 2 tags required. Example: v1.0 and v1.1"
        )

    current_tag = tags[0]
    previous_tag = tags[1]

    print(f"Comparing {previous_tag} -> {current_tag}")

    changed_files = subprocess.check_output(
        [
            "git",
            "diff",
            "--name-only",
            previous_tag,
            current_tag
        ]
    ).decode().splitlines()

    sql_files = [
        f for f in changed_files
        if f.endswith(".sql")
    ]

    print("Changed SQL files:")
    print(sql_files)

    if not sql_files:
        print("No SQL changes found.")
        exit(0)

    for file_name in sql_files:

        print(f"Executing {file_name}")

        with open(file_name, "r") as f:
            sql_script = f.read()

        cur.execute(sql_script)

        print(f"Completed {file_name}")

    print("Deployment Successful")

finally:
    cur.close()
    conn.close()
