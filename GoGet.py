#goget class
from HTMLParser import HTMLParser
parser = HTMLParser()
import os
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
import urllib2

def RetrieveData(ProductURL):
    """Retrieves raw data at a given URL. Useful for saving images."""
    ProductURL = parser.unescape(ProductURL)
    URL = ProductURL.strip()
    req = urllib2.Request(URL, headers={'User-Agent' : 'Codeschool'}) 
    con = urllib2.urlopen( req )
    data = con.read()
    con.close()
    sleep(1)
    return data

def RetrieveDataLines(ProductURL):
    """Retrieves a URL and returns its source as a list of lines."""
    ProductURL = parser.unescape(ProductURL)
    URL = ProductURL.strip()
    req = urllib2.Request(URL, headers={'User-Agent' : 'Codeschool'}) 
    con = urllib2.urlopen( req )
    data = con.readlines()
    con.close()
    sleep(2)
    return data

def SaveImageFile(URL,ImageDirectory):
    """Saves an image at URL to given ImageDirectory."""
    ImageData = RetrieveData(URL)
    ImageFilePath = os.path.join(ImageDirectory,URL.split('/')[-1])
    if not os.path.isfile(ImageFilePath):
        ImageFile = open(ImageFilePath,'wb')
        ImageFile.write(ImageData)
        ImageFile.close()

def SaveFileAs(URL,FilePath):
    """This lets us save a file as a name other than the one provided in the URL."""
    try:
        if not os.path.isfile(FilePath):
            FileData = RetrieveData(URL)
            File = open(FilePath,'wb')
            File.write(FileData)
            File.close()
        return FilePath
    except urllib2.HTTPError:
##        This section is only reached when there's an image called in the wiki page, but the image called is no longer there.
        return None
   

def TumblrImageArchive(tumblr):
    """Downloads every image post from a given tumblr's archive."""
    ImageList = TumblrImageArchiveList(tumblr)
    if len(ImageList) < 1:
        return None
    counter = 0
    for image in ImageList:
        counter += 1
        print "Progress: " + str(float(counter)/float(len(ImageList)) * 100.0) + "%"
        print str(counter) + " of " + str(len(ImageList)) + " in " + tumblr
        TumblrImagePost(image)

def TumblrImageArchiveList(tumblr):
    """Returns a list of image posts. Useful for adding to a queue."""
    posts = []
    source = []
    FirstPost = None
    LastPost = None
    PreviousLastPost = -1
    driver = webdriver.Firefox()
    URL = 'http://' + tumblr + '.tumblr.com/archive/filter-by/photo'
    end = False
    driver.get(URL)
    if '/post/' in driver.page_source:
        while end != True:
            x = '//a[@class="hover"]'
            theposts = driver.find_elements_by_xpath(x)
            currenthref = None
            for post in theposts:
                href = post.get_attribute("href")
                if '/post/' in href:
                    currenthref = href
                    if href not in posts:
                        posts.append(href)
            if LastPost != None:
                PreviousLastPost = LastPost
            LastPost = currenthref
            driver.execute_script( "window.scrollTo(0, document.body.scrollHeight);")
            sleep(5)
            if LastPost == PreviousLastPost:
                end = True
            else:
                source.append(driver.page_source)
    else:
        driver.quit()
        return None
    driver.quit()
    return posts

def TumblrImageArchiveQty(tumblr,postcount):
    """Downloads every image post from a given tumblr's archive."""
    ImageList = TumblrImageArchiveListQty(tumblr,postcount)
    if len(ImageList) < 1:
        return None
    for image in ImageList:
        TumblrImagePost(image)

def TumblrImageArchiveListQty(tumblr,postcount):
    """Returns a list of image posts. Useful for adding to a queue."""
    posts = []
    source = []
    FirstPost = None
    LastPost = None
    PreviousLastPost = -1
    driver = webdriver.Firefox()
    URL = 'http://' + tumblr + '.tumblr.com/archive/filter-by/photo'
    end = False
    driver.get(URL)
    if '/post/' in driver.page_source:
        while end != True:
            x = '//a[@class="hover"]'
            theposts = driver.find_elements_by_xpath(x)
            currenthref = None
            for post in theposts:
                href = post.get_attribute("href")
                if '/post/' in href:
                    currenthref = href
                    if href not in posts:
                        posts.append(href)
            if LastPost != None:
                PreviousLastPost = LastPost
            LastPost = currenthref
            driver.execute_script( "window.scrollTo(0, document.body.scrollHeight);")
            sleep(5)
            if LastPost == PreviousLastPost or len(posts) >= postcount:
                end = True
            else:
                source.append(driver.page_source)
    else:
        driver.quit()
        return None
    driver.quit()
    return posts



def TumblrImagePost(tumblr):
    if '/post/' not in tumblr:
        return
    """Downloads all images in a single tumblr image post."""
    ImageIndicator = '<meta property=\"og:image\" content=\"'
    tumblrname = tumblr.split('.tumblr.com')[0].split('/')[-1]
##    print "debug tumblrname " + tumblrname
    if not os.path.isdir(tumblrname):
        os.mkdir(tumblrname)
    try:
        sourcelines = RetrieveDataLines(tumblr)
    except:
        print "Issue with request at " + str(tumblr)
        return
    for line in sourcelines:
        if ImageIndicator in line:
            print "Found the tumblr images!"
            tempData = line.split('\"og:image\" content=\"')
            for element in tempData:
                if element.startswith('http:'):
                    try:
                        SaveImageFile(element.split('\"')[0],tumblrname)
                    except: # the original image has been removed
                        pass

def TumblrVideoArchive(tumblr):
    """Downloads every video post from a given tumblr's archive."""
    VideoList = TumblrVideoArchiveList(tumblr)
    if len(VideoList) < 1:
        return None
    for video in VideoList:
        TumblrVideoPost(video)

def TumblrVideoArchiveList(tumblr):
    """Downloads a list of URLs to every video post in a given tumblr's video archive."""
    posts = []
    source = []
    FirstPost = None
    LastPost = None
    PreviousLastPost = -1
    driver = webdriver.Firefox()
    #driver.set_window_size(ScreenSize())
    URL = 'http://' + tumblr + '.tumblr.com/archive/filter-by/video'
    #URL = 'http://www.amazon.com'
    end = False
    driver.get(URL)
    if '/post/' in driver.page_source:
        while end != True:
            x = '//a[@class="hover"]'
            theposts = driver.find_elements_by_xpath(x)
            currenthref = None
            for post in theposts:
                href = post.get_attribute("href")
                if '/post/' in href:
                    currenthref = href
                    if href not in posts:
                        posts.append(href)
            if LastPost != None:
                PreviousLastPost = LastPost
            LastPost = currenthref
            driver.execute_script( "window.scrollTo(0, document.body.scrollHeight);")
            sleep(5)
            if LastPost == PreviousLastPost:
                end = True
            else:
                source.append(driver.page_source)
    else:
        driver.quit()
        return None
    driver.quit()
    return posts

def TumblrVideoArchive(tumblr,postcount):
    """Downloads every video post from a given tumblr's archive."""
    VideoList = TumblrVideoArchiveList(tumblr,postcount)
    if len(VideoList) < 1:
        return None
    for video in VideoList:
        TumblrVideoPost(video)

def TumblrVideoArchiveList(tumblr,postcount):
    """Downloads a list of URLs to every video post in a given tumblr's video archive."""
    posts = []
    source = []
    FirstPost = None
    LastPost = None
    PreviousLastPost = -1
    driver = webdriver.Firefox()
    #driver.set_window_size(ScreenSize())
    URL = 'http://' + tumblr + '.tumblr.com/archive/filter-by/video'
    #URL = 'http://www.amazon.com'
    end = False
    driver.get(URL)
    if '/post/' in driver.page_source:
        while end != True:
            x = '//a[@class="hover"]'
            theposts = driver.find_elements_by_xpath(x)
            currenthref = None
            for post in theposts:
                href = post.get_attribute("href")
                if '/post/' in href:
                    currenthref = href
                    if href not in posts:
                        posts.append(href)
            if LastPost != None:
                PreviousLastPost = LastPost
            LastPost = currenthref
            driver.execute_script( "window.scrollTo(0, document.body.scrollHeight);")
            sleep(5)
            if LastPost == PreviousLastPost or len(posts) >= postcount:
                end = True
            else:
                source.append(driver.page_source)
    else:
        driver.quit()
        return None
    driver.quit()
    return posts


def TumblrVideoPost(tumblr):
    """Downloads the video in a single given tumblr post."""
    sourcelines = RetrieveDataLines(tumblr)
    tumblrname = tumblr.split('.tumblr.com')[0].split('/')[-1]
    if not os.path.isdir(tumblrname):
        os.mkdir(tumblrname)
    videolink = None
    for line in sourcelines:
        if 'tumblr_video_container' in line and videolink == None:
            videolink = line.split('iframe src=\'')[1].split('\'')[0]
        if videolink != None:
            videolines = RetrieveDataLines(videolink)
            for newline in videolines:
                if 'source src' in newline:
                    VideoURL = newline.split('source src=\"')[1].split('\"')[0]
                    VideoType = newline.split('video/')[1].split('\"')[0]
                    LocalFile = 'tumblr_' + VideoURL.split('tumblr_')[1].replace('/','_') + '.' + VideoType
                    SaveFileAs(VideoURL,os.path.join(tumblrname,LocalFile))
                    return # due to the way the code is generated, the script will keep downloading the same video. There is only ever 1 video to a post, so we can safely return after the first download.
                


def DAZProduct(DAZsku,DAZusername,DAZpassword):
    """Downloads a purchased product from DAZ."""
    driver = selenium.webdriver.Firefox()
    URL = 'https://www.daz3d.com/downloader/customer/files'
    driver.get(URL)
    time.wait(6)
    username = driver.find_element_by_id("email")
    password = driver.find_element_by_id("pass")
    submit = driver.find_element_by_name("send2")
    ### this doesn't actually work. something on the page renders these elements invisible (codewise)
    ### ask for help as no search result has worked yet (even those on stackoverflow)
    username.send_keys(DAZusername)
    password.send_keys(DAZpassword)
    submit.click()
    
def DAZProductImages(DAZsku):
    """Downloads all images associated with a given product SKU or zip file."""
    pass

def Hivewire3DProductImages(hw3d):
    """Downloads all images of a given Hivewire3D product. Full URL expected."""
    pass

def RenderosityProductImages(rendo):
    """Downloads all promo images at full size, plus the store thumbnail, for a Renderosity product number."""
    URL = 'https://www.renderosity.com/mod/bcs/?ViewProduct=' + str(rendo)
    source = RetrieveDataLines(URL)
    productnameindicator = '<meta name=\"keywords\" content=\"'
    print "debug: source has " + str(len(source)) + " lines."
    for line in source:
        if productnameindicator in line:
            names = line.split(productnameindicator)[1].split(',')
            productname = names[0]
            vendorname = names[1]
            print "Product:",productname,"by",vendorname
            foldername = "ROSITY - " + str(rendo) + " - " + vendorname + " - " + productname
            if not os.path.isdir(foldername):
                os.mkdir(foldername)
            print foldername
        if ('"promoImageView\"' in line or '\"mainImage\"' in line) and 'href' in line:
            ImageURL = line.split('href=\"')[1].split('\"')[0]
            SaveImageFile(ImageURL, foldername)

def RenderoticaProductImages(rotica):
    """Downloads all promo images at full size from a girven Renderotica URL."""
    source = RetrieveDataLines(rotica)
    SKU = rotica.split('sku/')[1].split('_')[0]
    productnameindicator = '<div class=\"primary-image\">'
    print "debug: source has " + str(len(source)) + " lines."
    lookingforproductname = False
    haveproductname = False
    havevendorname = False
    images = []
    for line in source:
        if productnameindicator in line and haveproductname == False:
            lookingforproductname = True
        if lookingforproductname and 'img src' in line:
            productname = parser.unescape(line.split('title=\"')[1].split('\"')[0])
            mainProductImage = 'http://www.renderotica.com' + line.split('img src=\"')[1].split('\"')[0].replace('.aspx','.jpg') # I included the . because there's a chance aspx could be part of an item's name
            lookingforproductname = False
            haveproductname = True
        if 'data-lightbox=\'images\'' in line:
            images.append(line.split('href = \'')[1].split('.aspx')[0])
        if 'class=\"vendor\"' in line and havevendorname == False:
            vendor = parser.unescape(line.split('>')[1].split('<')[0])
            if vendor.strip() == '' or vendor.strip() == None:
                pass
            else:
                vendor + " is the vendor"
                havevendorname = True
            
    if havevendorname and haveproductname:
        foldername = "ROTICA - " + str(SKU) + " - " + vendor + " - " + productname
        if not os.path.isdir(foldername):
            os.mkdir(foldername)
        print foldername
        SaveImageFile(mainProductImage,foldername)
    for image in images:
        SaveImageFile(image,foldername)

def YouTubeVideo(vid):
    """Downloads a single YouTube video, given the ID or full URL."""
    pass

def YouTubeVideoPlaylist(playlist):
    """Downloads all videos in a YouTube playlist, into a folder named after the playlist."""
    pass


