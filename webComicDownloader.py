m#! python3
# webComicDownloader.py - checks some internet comic pages, and downloads the images.
# it will try to download once a day using linux scheduler

import requests, os, bs4, threading, json 

def getLastComic(page):
    res = requests.get('http://%s.com' %(page))
    res.raise_for_status
    if page == 'exocomics':
        soup = bs4.BeautifulSoup(res.text, 'html.parser')
        pageSelect = soup.select('#main-comic img')
        return pageSelect[0].get('alt')
    else:
        soup = bs4.bs4.BeautifulSoup(res.text, 'html.parser')
        prevLink = soup.select('a[rel="prev"]')[0]
        return int(prevLink[1:-1]) +1
    

def downloadExocomics(startComic, endComic,frstPages):
    for urlNumber in range(startComic  +1, endComic +1):

        #Dowload the page
        print('Downloading page https://exocomics.com/%s/...' % (urlNumber))
        res = requests.get('https://exocomics.com/%s/' % (urlNumber))
        soup = bs4.BeautifulSoup(res.text, 'html.parser')

        #FInd the url to the comics image
        comicElem = soup.select('#main-comic img')
        if comicElem == []:
            print('Could not find comic image.')
        else:
            comicUrl = comicElem[0].get('src')

            # Dowload the image
            print('Downloading image %s...' % (comicUrl))
            res = requests.get('https://www.exocomics.com' + comicUrl)
            
            # Save the image to ./exocomics.
            imageFile = open(os.path.join('exocomics', os.path.basename(comicUrl)), 'wb')
            for chunk in res.iter_content(100000):
                imageFile.write(chunk)
            imageFile.close()
        if urlNumber == endComic:
            frstPages['exocomics'] = urlNumber

def downloadXkcd(startComic, endComic, frstPages):
    frstPages['xkcd'] = endComic
    while startComic != endComic:

        #Dowload the page
        print('Downloading page https://xkcd.com/%s...' % (endComic))
        res = requests.get('https://xkcd.com/%s' % (endComic))
        res.raise_for_status

        soup = bs4.BeautifulSoup(res.text, 'html.parser')

        #Find the url to the comics image
        comicElem = soup.select('#comic img')
        if comicElem == []:
            print('Could not find comic image.')
        else:
            comicUrl = comicElem[0].get('src')

            # Dowload the image
            print('Downloading image %s...' % (comicUrl))
            res = requests.get('https:' + comicUrl)
            res.raise_for_status
            
            # Save the image to ./xkcd.
            imageFile = open(os.path.join('xkcd', os.path.basename(comicUrl)), 'wb')
            for chunk in res.iter_content(100000):
                imageFile.write(chunk)
            imageFile.close()
        endComic -= 1
    

os.makedirs('exocomics', exist_ok=True)      # store comics in ./exocomics
os.makedirs('xkcd', exist_ok=True)      # store comics in ./xkcd

#find the last comic downloaded
exocomics = os.listdir('./exocomics')
xkcdComics = os.listdir('./xkcd')

jsonFIle = open('lastPage.json','rb')
frstPages = json.load(jsonFIle)

# Create and start the Threads objects
downloadThreads = []

downloadThreadExo = threading.Thread(target=downloadExocomics, args = (frstPages['exocomics'], int(getLastComic('exocomics')),frstPages))
downloadThreads.append(downloadThreadExo)
downloadThreadExo.start()

downloadThreadExo = threading.Thread(target=downloadXkcd, args = ( frstPages['xkcd'], frstPages['xkcd'] +10 ,frstPages))
downloadThreads.append(downloadThreadExo)
downloadThreadExo.start()

for downloadThread in downloadThreads:
    downloadThread.join()

#update json file
lastPages = json.dumps(frstPages)
jsonFIle.close()
jsonFIle = open('lastPage.json','w')
jsonFIle.write(lastPages)
print('Done')
