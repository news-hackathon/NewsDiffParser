#!/usr/bin/env python
# encoding: utf-8

import json
import os
import glob
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import News, Base
from datetime import date
import shutil


media_list = {
    1: '蘋果',
    2: '中時',
    3: '中央社',
    4: '東森',
    5: '自由',
    6: '新頭殼',
    7: 'NowNews',
    8: '聯合',
    9: 'TVBS',
    10: '中廣新聞網',
    11: '公視新聞網',
    12: '台視',
    13: '華視',
    14: '民視',
    # //            15 : '三立',
    16: '風傳媒',
}


def inspect_josn_format(inspect_str):
    try:
        json.loads(inspect_str)
    except ValueError:
        return False
    return True


def create_output_file(f, news_event):
    print('title: ' + f.name)
    f.write('--->\n')
    f.write(news_event.get_url() + '\n\n')
    f.write(news_event.get_title() + '\n')
    f.write(news_event.get_content())


def get_news_info(news_file, session, is_diff_file):
    title = ''
    content = ''
    is_exists_id = False
    already_get_id = False
    for line in news_file:
        if inspect_josn_format(line) and line.startswith('{'):
            already_get_id = True
            is_exists_id = False
            title = ''
            content = ''
            meta = json.loads(line)
            id = meta['id']
            create_time = date.fromtimestamp(int(meta['created_at'])).strftime("%Y-%m-%d")
            try_get = session.query(News).filter_by(news_id=id).first()

            if try_get and is_diff_file:
                is_exists_id = True
                session.query(News).filter_by(news_id=id).first().update_changed_count()
            elif (not try_get) and (not is_diff_file):
                url = meta['url']
                source_media = media_list[int(meta['source'])]
            else:
                already_get_id = False
                print('Error item!')
        else:
            if already_get_id == False:
                continue
            if is_exists_id == True:
                if content == '' and title != '':
                    content = line
                    already_get_id = False
                    if not(("404" in content) or ("404" in title)):
                        session.query(News).filter_by(news_id=id).update({'title': title, 'content': content})
                if title == '':
                    title = line
            else:
                if content == '' and title != '':
                    content = line
                    already_get_id = False
                    news_add = News(news_id=id, url=url, title=title,
                                    source_media=source_media,
                                    content=content, create_time=create_time)
                    session.add(news_add)
                    session.commit
                if title == '':
                    title = line
    return session


def create_diff_map(source_dir):
    print('source_dir: ' + source_dir)
    if os.path.exists('db.sqlite'):
        os.remove('db.sqlite')
    engine = create_engine("sqlite:///db.sqlite", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    for file_name in glob.glob(source_dir + '/*'):
        if 'diff' in file_name:
            continue
        with open(file_name, 'r') as f:
            print('normal: ' + file_name)
            session = get_news_info(f, session, False)

    for file_name in glob.glob(source_dir + '/*diff*'):
        print('diff: ' + file_name)
        with open(file_name, 'r') as f:
            session = get_news_info(f, session, True)

    all_of_news = session.query(News).all()
    output_dir = source_dir + '_output'
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    for news_event in all_of_news:
        print('title: ' + news_event.get_news_file_name())
        with open(output_dir + '/' + news_event.get_news_file_name(), 'w') as f:
            create_output_file(f, news_event)


def arrange(source_dir, dest_dir):
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)

    create_diff_map(source_dir)


arrange('extract', 'tmp')
