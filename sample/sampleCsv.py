import csv
with open('eggs.csv', 'wb') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=' ',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(['Spam'] * 5 + ['Baked Beans'])
    spamwriter.writerow(['Spam', 'Lovely Spam', 'Wonderful Spam'])


with open('test.csv', 'wb') as fp:
    a = csv.writer(fp, delimiter=',')
    data = [['Me', 'You'],
            ['293', '219'],
            ['54', '13']]
    a.writerows(data)
