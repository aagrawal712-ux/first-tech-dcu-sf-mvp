import os
import snowflake.connector

print("Connecting to Snowflake...")

- name: Check Secrets
  run: |
    echo "Account Exists: ${{ secrets.SNOWFLAKE_ACCOUNT != '' }}"
    echo "User Exists: ${{ secrets.SNOWFLAKE_USER != '' }}"
    echo "Password Exists: ${{ secrets.SNOWFLAKE_PASSWORD != '' }}"
    echo "Role Exists: ${{ secrets.SNOWFLAKE_ROLE != '' }}"
    echo "Warehouse Exists: ${{ secrets.SNOWFLAKE_WAREHOUSE != '' }}"

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

    with open("ddl/customer.sql", "r") as file:
        sql_script = file.read()

    print("Executing SQL...")

    cur.execute(sql_script)

    print("Deployment Successful!")

finally:
    cur.close()
    conn.close()
