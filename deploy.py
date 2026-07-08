import os
import glob
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

    # Find all TXT files
    txt_files = glob.glob("**/*.txt", recursive=True)

    if not txt_files:
        raise Exception("No .txt files found in repository")

    for file_name in sorted(txt_files):
        print(f"Executing {file_name}")

        with open(file_name, "r", encoding="utf-8") as f:
            sql_script = f.read().strip()

        if not sql_script:
            print(f"Skipping empty file: {file_name}")
            continue

        cur.execute(sql_script)

        print(f"Completed {file_name}")

    print("Deployment Successful!")

finally:
    cur.close()
    conn.close()
