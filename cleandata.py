import ConfigParser
import datetime
import os

import sqlalchemy

import db

def main():
    # Load configuration
    config = ConfigParser.RawConfigParser()
    config.read('app.config')
    
    # Connect to a database produced by the scraper at:
    # https://github.com/c4fcm/ytrends/tree/master/scraper
    db_engine = sqlalchemy.create_engine("%s://%s:%s@%s/%s" % (
        config.get('database', 'protocol')
        , config.get('database', 'user')
        , config.get('database', 'password')
        , config.get('database', 'host')
        , config.get('database', 'database')
    ))
    Session = sqlalchemy.orm.sessionmaker(bind=db_engine)
    db_session = Session()
    
    # Load data
    # Remove countries that have missing data on many days.
    # Remove dates where remaining countries have no data.
    # Some countries may have less than 10 videos on a day, but we assume this is
    # due to having fewer trending videos rather than missing data.
    dates = config.get('cleanup', 'dates').split(',')
    countries = config.get('cleanup', 'countries').split(',')
    ranks = db_session.query(db.Rank.date, db.Rank.loc, db.Rank.video_id).\
        filter_by(source='view').\
        filter(db.Rank.loc.in_(countries)).\
        filter(db.Rank.date.in_(dates))
    
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    index = 1;
    while os.path.exists("data/%s-%d.csv" % (today, index)):
        index += 1
    with open("data/%s-%d.csv" % (today, index), 'wb') as f:
        f.write("date, country, video_id\n")
        for rank in ranks:
            f.write("%s, %s, %s\n" % (rank[0], clean(rank[1]), rank[2]))
            
def clean(name):
    '''Clean country codes'''
    # Since we're in the US, YouTube replaces our country code with --
    if name == '--':
        return 'usa'
    return name

# Run the main script
if __name__== '__main__':
    main()
