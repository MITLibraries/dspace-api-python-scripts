import csv
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--fileNameCSV', help='the metadata CSV file. optional - if not provided, the script will ask for input')
parser.add_argument('-b', '--baseURL', help='the base URL to use for the series links. optional - if not provided, the script will ask for input')
parser.add_argument('-i', '--handle', help='handle of the collection. optional - if not provided, the script will ask for input')
args = parser.parse_args()

if args.fileNameCSV:
    fileNameCSV =args.fileNameCSV
else:
    fileNameCSV = raw_input('Enter the metadata CSV file (including \'.csv\'): ')
if args.baseURL:
    baseURL =args.baseURL
else:
    baseURL = raw_input('Enter the base URL to use for the series links: ')
if args.handle:
    handle = args.handle
else:
    handle = raw_input('Enter collection handle: ')

handle  = handle.replace('/', '%2F')

#Enter abstract text here
abstractText = 'Educational slides played an important role in the history of public health campaign in P.R. China. From the beginning of the 1950s, Chinese government\'s health policy put an emphasis on public hygiene and preventive treatment. Along with radio, posters, and movies, slides became a favored propaganda tool for educating the public. Slides were inexpensive to produce and disseminate. They were widely used in school teaching and various public health activities/campaigns in both rural and urban China. These health slides aimed at disseminating scientific and medical concepts and behaviors among a population with very different understanding of what constituted illness and well-being.''

seriesTitles = []

with open(fileNameCSV) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        seriesTitle = row['Series title']
        if seriesTitle not in seriesTitles:
            seriesTitles.append(seriesTitle)

seriesLinks = ''

for seriesTitle in seriesTitles:
    editedSeriesTitle = seriesTitle.replace(' ','+')
    seriesLink = '<li><a href="'+baseURL+'discover?scope='+handle+'&query=%22'+editedSeriesTitle+'%22&sort_by=dc.title_sort&order=asc&submit=">'+seriesTitle+'</a></li>'
    seriesLinks += seriesLink

abstractText = '<p>'+abstractText+'</p>'
seriesLinks = '<ul>'+seriesLinks+'</ul>'

f = open('collectionLevelAbstract.txt', 'wb')
f.write(abstractText + seriesLinks)
