import csv
from titlecase import titlecase
import secrets

filePath = secrets.filePath

fileName = filePath+raw_input('Enter fileName (including \'.csv\'): ')

f=csv.writer(open('uppercaseValues.csv','wb'))
f.writerow(['orgTitle']+['modTitle']+['itemID'])
with open(fileName) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['value'].isupper() == True:
                orgTitle = row['value']
                modTitle = titlecase(orgTitle)
                f.writerow([orgTitle]+[modTitle]+[row['itemID']])
