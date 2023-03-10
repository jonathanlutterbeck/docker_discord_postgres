import psycopg2
import os
import time


import socket

def get_my_tasks():
    sql_command = f"SELECT * FROM tasks WHERE worker = '{get_hostname()}' AND done = false;"
    result = db_action(sql_command)
    if result:
        return result
    else:
        return []

def get_hostname():

    SERVER_NAME = socket.gethostname()
    hostname = SERVER_NAME  
    return hostname

def get_blocked_users():
    sql_command = "SELECT user_id FROM users WHERE blocked=true;"
    result = db_action(sql_command)
    if result:
        return result
    else:
        return []

def insert_user(user_id):
    if not check_user_exists(user_id):
        sql_command = f"INSERT INTO users (user_id) VALUES ('{user_id}');"
        db_action(sql_command)

def check_user_exists(user_id):
    sql_command = f"SELECT user_id FROM users WHERE user_id = '{user_id}';"
    result = db_action(sql_command)
    if result:
        return True
    else:
        return False

def insert_message(user_id, message):
    sql_command = f"INSERT INTO messages (user_id, text) VALUES ('{user_id}', '{message}');"
    db_action(sql_command)

def insert_command(user_id, command):
    sql_command = f"INSERT INTO commands (user_id, text) VALUES ('{user_id}', '{command}');"
    db_action(sql_command)

def insert_session(user_id):
    sql_command = f"INSERT INTO session (user_id) VALUES ('{user_id}');"
    db_action(sql_command)

def update_session(user_id):
    sql_command = f"UPDATE session SET stop = NOW() WHERE user_id = '{user_id}' AND stop IS NULL;"
    db_action(sql_command)

def increase_tokens(user_id, tokens):
    sql_command = f"UPDATE users SET tokens = tokens + {tokens} WHERE user_id = '{user_id}';"
    db_action(sql_command)

def decrease_tokens(user_id, tokens):
    sql_command = f"UPDATE users SET tokens = tokens - {tokens} WHERE user_id = '{user_id}';"
    db_action(sql_command)


def add_task(user_id, task):
    sql_command = f"INSERT INTO queue (user_id, task) VALUES ('{user_id}', '{task}');"
    db_action(sql_command)

def claim_task(picker_id, task):
    sql_command = f"UPDATE queue SET taken_by = {picker_id} WHERE task = '{task}';"
    db_action(sql_command)

def get_tokens(user_id):
    sql_command = f"SELECT tokens FROM users WHERE user_id = '{user_id}';"
    result = db_action(sql_command, first=True)[0][0]
    return result
    
def check_my_task(picker_id):
    sql_command = f"SELECT * FROM queue WHERE taken_by = {picker_id} AND done = false;"
    result = db_action(sql_command)[0]
    return result

def get_tasks():
    sql_command = "SELECT * FROM queue WHERE done = false;"
    result = db_action(sql_command)
    return result

def finish_task(picker_id):
    sql_command = f"UPDATE queue SET done = true WHERE taken_by = {picker_id} AND done = false;"
    db_action(sql_command)

def get_messages_to_be_sent():
    sql_command = "SELECT message_id, text FROM messages WHERE sent = false;"
    result = db_action(sql_command)
    if result:
        return result

def message_claimed_yes(message_id):
    sql_command = f"SELECT taken_by FROM messages WHERE message_id = '{message_id}';"
    result = db_action(sql_command, first=True)
    if result == hostname:
        return True
    return False

def claim_message(message_id):
    sql_command = f"UPDATE messages SET taken_by = '{get_hostname()}' WHERE message_id = '{message_id}';"
    db_action(sql_command)


def get_unfinished_tasks():
    sql_command = "SELECT queue_id FROM queue WHERE done = false;"
    result = db_action(sql_command)
    if result:
        return result
    else:
        return None

def get_untaken_tasks():
    sql_command = "SELECT queue_id FROM queue WHERE taken_by IS NULL;"
    result = db_action(sql_command)
    if result:
        return result
    else:
        return None

def get_unsent_messages():
    sql_command = "SELECT message_id FROM messages WHERE sent = false;"
    result = db_action(sql_command)
    if result:
        return result
    else:
        return None

def get_my_tasks():
    tasks = []
    sql_command = f"SELECT task FROM queue WHERE taken_by = '{get_hostname()}' AND done = false;"
    result = db_action(sql_command)
    for task in result:
        tasks.append(task[0])
    if result:
        return tasks
    else:
        return None

def get_text_task(task_id):
    sql_command = f"SELECT text FROM queue WHERE queue_id = {task_id};"
    result = db_action(sql_command, first=True)[0]
    return result



# Connect to the database
def db_action(sql_command, first=False):
    conn = psycopg2.connect(
    host="postgres",
    port=5432,
    user="postgres",
    password="changeme",
    database="postgres")
    cur = conn.cursor()

    cur.execute(sql_command)

    results = []

    if first:
        try:
            results.append(cur.fetchone())
        except:
            results = []

    else:
        try:
            results = cur.fetchall()
        except:
            results = []
    
    # Commit the changes to the database
    conn.commit()

    cur.close()
    conn.close()

    return results
