import ConfigParser
import csv
import unittest

class DataTest(unittest.TestCase):
    
    def setUp(self):
        config = ConfigParser.RawConfigParser()
        config.read('../app.config')
        # Load the data from the csv into an array
        self.data = []
        with open('../data/%s' % config.get('data', 'filename'), 'rb') as csvfile:
            reader = csv.reader(csvfile)
            # Skip header and parse data
            reader.next()
            for row in reader:
                self.data.append([s.strip() for s in row])
    
    def test_complete(self):
        '''Ensure there are no day/country pairs missing data'''
        date_country = dict()
        dates = set()
        countries = set()
        for date, country, video_id in self.data:
            dates.add(date)
            countries.add(country)
            date_country[date] = date_country.get(date, {})
            date_country[date][country] = date_country[date].get(country, 0) + 1
        for date in dates:
            for country in countries:
                count = date_country.get(date,{}).get(country,0)
                self.assertNotEqual((date, country, count), (date, country, 0))

if __name__ == '__main__':
    unittest.main()
