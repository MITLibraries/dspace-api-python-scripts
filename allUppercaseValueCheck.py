import csv
from titlecase import titlecase
import secrets

filePath = secrets.filePath

filename = filePath+raw_input('Enter filename (including \'.csv\'): ')

f=csv.writer(open('uppercaseValues.csv','wb'))
f.writerow(['orgTitle']+['modTitle']+['itemID'])
with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['value'].isupper() == True:
                orgTitle = row['value']
                modTitle = titlecase(orgTitle)
                f.writerow([orgTitle]+[modTitle]+[row['itemID']])
