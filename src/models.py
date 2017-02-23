from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()


class News(Base):
    __tablename__ = 'News'

    news_id = Column(Integer, primary_key=True)
    url = Column(String)
    title = Column(String)
    content = Column(String)
    create_time = Column(String)
    source_media = Column(String)
    changed_count = Column(Integer)

    def __init__(self, news_id, url, title, content, create_time,
                 source_media):
        self.news_id = news_id
        self.url = url
        self.title = title
        self.content = content
        self.create_time = create_time
        self.source_media = source_media
        self.changed_count = 1

    def __repr__(self):
        return ('News: ' + str(self.news_id) +
                ' url: ' + self.url +
                ' title: ' + self.title +
                ' create time: ' + self.create_time +
                ' source_media: ' + self.source_media)
                # ' content: ' + self.content)

    def update_changed_count(self):
        self.changed_count += 1

    def inspect_expiration_date(self, date):
        create_time = datetime.datetime.strptime(self.create_time, '%Y-%m-%d')
        changed_time = datetime.datetime.strptime(date, '%Y-%m-%d')
        period = changed_time - create_time

        if int(period.days) > 30:
            return False
        else:
            return True

    def get_id(self):
        return self.news_id

    def get_content(self):
        return self.content

    def get_url(self):
        return self.url

    def get_title(self):
        return self.title

    def get_news_file_name(self):
        prepare_title = self.title.strip('\n')
        prepare_title = prepare_title.replace('/', '／')
        return '{}／{}／{}／{}／{}／.txt'.format(self.create_time,
                                                  self.source_media,
                                                  self.news_id,
                                                  prepare_title,
                                                  self.changed_count)

        # return "({:s}{:d})".format(self.goals, self.penalties)
