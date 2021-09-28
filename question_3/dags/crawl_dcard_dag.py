import os
import sys
from functools import wraps

from airflow.utils.dates import days_ago
from airflow.settings import AIRFLOW_HOME
from airflow import DAG
from airflow.operators.python import BranchPythonOperator
from airflow.operators.dummy import DummyOperator

import requests

class EnvSetting(object):
    PROJECT_HOME = f'{AIRFLOW_HOME}/dags/foxit-homework'

    @staticmethod
    def append_project_to_path(f):
        @wraps(f)
        def insert_path(*args, **kwds):
            sys.path.insert(0, EnvSetting.PROJECT_HOME)
            return f(*args, **kwds)

        return insert_path


args = {
    'owner': 'sean',
}


def create_dag(forum):
    dag = DAG(
        dag_id=f'crawl_dcard_{forum}_dag',
        default_args=args,
        max_active_runs=1,
        schedule_interval='1 0/6 * * *',
        start_date=days_ago(1),
    )

    @EnvSetting.append_project_to_path
    def check_post_exist(**context):
        from datetime import datetime
        from datetime import timedelta
        import logging

        from airflow.providers.mongo.hooks.mongo import MongoHook
        mongo_hook = MongoHook(conn_id='dcard')
        dcard_db = mongo_hook.get_conn().dcard
        ts = context['ts']
        interval = timedelta(hours=6)
        this_ts_date = datetime.fromisoformat(ts)
        this_end = this_ts_date + interval

        logging.info(f'!!!!! search post from {this_ts_date} to {this_end} in {forum}')
        results = dcard_db[forum].find({
            'createdAt': {
                '$gte': this_ts_date,
                '$lt': this_end
            }
        })

        post_ids = [result['postID'] for result in results]

        if len(post_ids) == 0:
            logging.info(f'!!!!! No post in {forum}')
            return 'crawl_forum'

        else:
            ti = context['ti']
            ti.xcom_push('post_ids', post_ids)
            logging.info(f'!!!!! {forum} has {len(post_ids)} posts.')
            return 'update_posts'

    check_post_exist_task = BranchPythonOperator(
        task_id='check_post_exist',
        python_callable=check_post_exist,
        provide_context=True,
        depends_on_past=True,
        dag=dag,
    )

    @EnvSetting.append_project_to_path
    def crawl_forum(**context):
        import logging
        import time
        from datetime import datetime
        from datetime import timedelta
        import pytz
        import requests
        import random

        from airflow.providers.mongo.hooks.mongo import MongoHook

        ts = context['ts']
        interval = timedelta(hours=6)
        this_start_date = datetime.fromisoformat(ts)
        this_end_date = this_start_date + interval
        logging.info(f'!!!!! Date of the period: {this_start_date} to {this_end_date}.')
        utc = pytz.UTC

        def date_filter(post):
            this_post_date = datetime.fromisoformat(post['createdAt'].rstrip('Z'))
            return this_start_date <= utc.localize(this_post_date) < this_end_date

        resp = requests.get(
            f'https://www.dcard.tw/service/api/v2/forums/{forum}/posts?limit=100')
        got_posts = resp.json()
        posts_in_period = list(filter(date_filter, got_posts))

        oldest_post = got_posts[-1]
        oldest_post_date = datetime.fromisoformat(oldest_post['createdAt'].rstrip('Z'))
        oldest_post_date = utc.localize(oldest_post_date)
        logging.info(f'!!!!! Date of oldest_post: {oldest_post_date}.')
        oldest_id = oldest_post['id']

        insert_list = []
        while oldest_post_date > this_start_date or len(posts_in_period) > 0:
            logging.info(f'!!!!! There are {len(posts_in_period)} post(s) in the period.')
            for post in posts_in_period:
                post_id = post['id']
                try:
                    resp = requests.get(f'https://www.dcard.tw/service/api/v2/posts/{post_id}')
                    got_post = resp.json()
                except Exception as e:
                    logging.info(f'!!!!! {resp.text} has error: {e}.')
                    return 'has_error'
                this_post_date = datetime.fromisoformat(got_post['createdAt'].rstrip('Z'))
                this_post_date = utc.localize(this_post_date)
                insert_list.append({
                    'postID': post_id,
                    'title': got_post['title'],
                    'createdAt': this_post_date,
                    'mediaMeta': got_post.get('mediaMeta', {}),
                    'categories': got_post.get('categories', []),
                    'content': got_post.get('content', ""),
                    'topics': got_post.get('topics', []),
                })
                logging.info(f'!!!!! Got post {post_id}.')
                time.sleep(random.randint(15, 30))

            time.sleep(random.randint(15, 30))
            logging.info(f'!!!!! Get next page posts before {oldest_id}.')
            next_page_url = f'https://www.dcard.tw/service/api/v2/forums/{forum}/posts?limit=100&before={oldest_id}'
            logging.info(f'!!!!! url: {next_page_url}')
            resp = requests.get(next_page_url)
            got_posts = resp.json()
            posts_in_period = list(filter(date_filter, got_posts))

            oldest_post = got_posts[-1]
            oldest_post_date = datetime.fromisoformat(oldest_post['createdAt'].rstrip('Z'))
            oldest_post_date = utc.localize(oldest_post_date)
            logging.info(f'!!!!! Date of oldest_post: {oldest_post_date}.')
            oldest_id = oldest_post['id']

        if len(insert_list) > 0:
            logging.info(f'!!!!! There are {len(insert_list)} post(s) will be inserted to {forum}.')
            mongo_hook = MongoHook(conn_id='dcard')
            dcard_db = mongo_hook.get_conn().dcard
            dcard_db[forum].insert_many(insert_list, ordered=True)
        else:
            logging.info(f'!!!!! No post will be inserted to {forum}.')

        return 'done'

    crawl_forum_task = BranchPythonOperator(
        task_id='crawl_forum',
        python_callable=crawl_forum,
        provide_context=True,
        dag=dag,
    )

    @EnvSetting.append_project_to_path
    def update_posts(**context):
        import logging
        import random
        from airflow.providers.mongo.hooks.mongo import MongoHook

        import time
        ti = context['ti']
        post_ids = ti.xcom_pull(task_ids='check_post_exist', key='post_ids')

        mongo_hook = MongoHook(conn_id='dcard')
        dcard_db = mongo_hook.get_conn().dcard
        logging.info(f'!!!!! need update count: {len(post_ids)}.')
        for post_id in post_ids:
            try:
                resp = requests.get(f'https://www.dcard.tw/service/api/v2/posts/{post_id}')
                got_post = resp.json()

                result = dcard_db[forum].update({
                        'postID': post_id
                    },
                    {
                        "$set": {
                            'title': got_post['title'],
                            'createdAt': got_post['createdAt'],
                            'mediaMeta': got_post.get('mediaMeta', {}),
                            'categories': got_post.get('categories', []),
                            'content': got_post.get('content', ""),
                            'topics': got_post.get('topics', []),
                        }
                    }
                )
            except Exception as e:
                logging.info(f'!!!!! {resp.text} has error: {e}.')
                return 'update_has_error'

            logging.info(f'!!!!! update post {post_id}. result: {result}')
            time.sleep(random.randint(15, 30))

        logging.info(f'!!!!! updating is finished!')
        return 'update_done'

    update_posts_task = BranchPythonOperator(
        task_id='update_posts',
        python_callable=update_posts,
        provide_context=True,
        depends_on_past=True,
        dag=dag,
    )

    done_task = DummyOperator(
        task_id='done',
        dag=dag
    )

    update_done_task = DummyOperator(
        task_id='update_done',
        dag=dag
    )

    has_error_task = DummyOperator(
        task_id='has_error',
        dag=dag
    )

    update_has_error_task = DummyOperator(
        task_id='update_has_error',
        dag=dag
    )

    check_post_exist_task >> [crawl_forum_task, update_posts_task]
    crawl_forum_task >> [done_task, has_error_task]
    update_posts_task >> [update_done_task, update_has_error_task]

    return dag


apple_dag = create_dag(forum='apple')