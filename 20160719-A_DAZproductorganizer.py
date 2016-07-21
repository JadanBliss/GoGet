import glob,os,re,shutil,string,unicodedata,urllib2
from HTMLParser import HTMLParser
parser = HTMLParser()
from PIL import Image
from time import sleep
PromoThumbnailSize = 380,494
RootDirectory = os.getcwd()
ProductURLBase = 'http://www.daz3d.com/catalog/product/view/id/'
valid_chars = "-_.,&()' %s%s" % (string.ascii_letters, string.digits)
NumberPad = 5
NoImagePath = os.path.join(RootDirectory,"no-image.jpg")
def IsTemplateFile(filename):
    if filename.lower().startswith('template'):
        return True
    return False

def IsProductFile(filename):
    if filename.startswith('IM'):
        return True
    return False

def GetSKUFromFilename(filename):
    if IsTemplateFile(filename):
        return filename.split('_')[1]
    else:
        return str(int(filename[2:10]))

def GetProductNameFromSKU(SKU):
    firstfile = glob.glob('*' + str(SKU) + '*.zip')[0]
    if IsTemplateFile(firstfile):
        return filename.split('_')[2][:-4]
    else:
        return filename.split('_')[1][:-4]
        
## from http://stackoverflow.com/questions/5574042/string-slugification-in-python
def MakeSlug(text):
    slug = text.encode('ascii', 'ignore').lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-')
    slug = re.sub(r'[-]+', '-', slug)
    slug = re.sub(r':',' -'. slug)
    return slug
    
def RetrieveData(ProductURL):
    URL = ProductURL.strip()
    req = urllib2.Request(URL, headers={'User-Agent' : 'Codeschool'}) 
    con = urllib2.urlopen( req )
    data = con.read()
    con.close()
    sleep(1)
    return data

def RetrieveDataLines(ProductURL):
    URL = ProductURL.strip()
    req = urllib2.Request(URL, headers={'User-Agent' : 'Codeschool'}) 
    con = urllib2.urlopen( req )
    data = con.readlines()
    con.close()
    sleep(2)
    return data

def SaveHTMLFile(URL,HTMLFileDirectory):
    HTMLFileBase = URL.split('/')[-1]
    HTMLFilePath = os.path.join(HTMLFileDirectory,HTMLFileBase) + '.html'
    print 'Saving HTML file as: ' + HTMLFilePath
    HTMLData = RetrieveDataLines(URL)
    HTMLFile = open(HTMLFilePath,'w')
    for HTMLLine in HTMLData:
        HTMLFile.write(HTMLLine)
    HTMLFile.close()
        
def SaveImageFile(URL,ImageDirectory):
    try:
        ImageData = RetrieveData(URL)
        ImageFilePath = os.path.join(ImageDirectory,URL.split('/')[-1])
        print 'Saving image file as: ' + ImageFilePath
        ImageFile = open(ImageFilePath,'wb')
        ImageFile.write(ImageData)
        ImageFile.close()
        return ImageFilePath
    except urllib2.HTTPError:
##        This section is only reached when there's an image called in the wiki page, but the image called is no longer there.
        return None
    
def GetProductName(ProductData):
    for HTMLLine in ProductData:
        if HTMLLine.startswith('<title>'):
            HTMLLine = HTMLLine.split(' | ')[0][7:]
            return parser.unescape(HTMLLine)
    return "ERROR"

def GetNLAProductName(ProductData):
    for HTMLLine in ProductData:
        if 'Product Name:' in HTMLLine:
            tempNameData = HTMLLine.split('>')
            tempNameDataElement = tempNameData[len(tempNameData)-2]
            return parser.unescape(tempNameDataElement.split('<')[0].strip())
    return "ERROR"

def GetImages(ProductData,ImageDirectory):
    for HTMLLine in ProductData:
        if "data-fancybox-group=\"gallery_product\" data-fancybox-href=\"" in HTMLLine:
            ImageURL = HTMLLine.split("data-fancybox-group=\"gallery_product\" data-fancybox-href=\"")[1]
            ImageURL = ImageURL.split("\" data-fancybox-type=\"image\"")[0]
            print 'Grabbing image: ' + ImageURL
            SaveImageFile(ImageURL,ImageDirectory)

def GetFirstImage(tr):
    for HTMLLine in tr:
        if 'data-fancybox-group=\"gallery_product\" data-fancybox-href=\"' in HTMLLine:
                ImageURL = HTMLLine.split('data-fancybox-group=\"gallery_product\" data-fancybox-href=\"')[1]
                ImageURL = ImageURL.split('\" data-fancybox-type=\"image\"')[0]
                return ImageURL.split('/')[-1]
    return None

def GetProduct(ProductIndex):
    ProductURL = ProductURLBase + str(ProductIndex)
    print 'Attempting to retrieve: ' + ProductURL
    ProductData = RetrieveDataLines(ProductURL)
    ProductName = GetProductName(ProductData).replace(':',' -')
    ProductName = ''.join(c for c in ProductName if c in valid_chars)
    print 'Product Name: ' + ProductName
    ProductDirectory = str('0' * max(0,NumberPad - len(str(ProductIndex)))) + str(ProductIndex) + '_' + ProductName
    ProductPath = os.path.join(RootDirectory,ProductDirectory)

    if not os.path.isdir(ProductPath):
        os.mkdir(ProductPath)
        GetImages(ProductData,ProductPath)
        LastGoodProduct = ProductIndex
        Fail = 0
        SaveHTMLFile(ProductURL,HTMLDirectory)
        MainPromo = GetFirstImage(ProductData)
        MainPromoPath = os.path.join(ProductDirectory,MainPromo)
        SlugName = MakeSlug(ProductName)
        PromoName = SlugName + '.jpg'
        NewPromoPath = os.path.join(ProductDirectory,PromoName)
        tn = Image.open(MainPromoPath)
        tn.thumbnail(PromoThumbnailSize,Image.ANTIALIAS)
        tn.save(NewPromoPath, 'JPEG', quality=100)

def NoImage(OutputDirectory):
    if os.path.isfile(NoImagePath):
        shutil.copy(NoImagePath,OutputDirectory)
    else:
        noimagetext = open(os.path.join(OutputDirectory,'NO-IMAGE-FILES-EXIST.TXT'),'w')
        noimagetext.write('')
        noimagetext.close()
        
def GetMissingProduct(ProductIndex):
    ProductIndex = int(ProductIndex)
    WikiPageURL = 'http://docs.daz3d.com/doku.php/public/read_me/index/' + str(ProductIndex) + '/start'
    CurrentDirectoryList = glob.glob('*/')
    NLAProductDirectory = None
    ImageFile = None
    for Directory in CurrentDirectoryList:
        Directory = Directory.strip()
        if len(Directory) < 11:
            continue
        SKUCheck = re.match('[0-9]+_',Directory)
        if not SKUCheck:
            continue
        DirectorySKU = int(Directory.split('_')[0])
        if DirectorySKU == ProductIndex:
            NLA = re.match('[0-9]+_\(NLA\)',Directory)
            if NLA:
                ProductName = GetProductNameFromSKU(ProductIndex)
                NewDirectory = str('0' * max(0,NumberPad - len(str(ProductIndex)))) + str(ProductIndex) + '_' + ProductName + ' (NLA)'
                OldPath = os.path.join(RootDirectory,Directory)
                NewPath = os.path.join(RootDirectory,NewDirectory)
                shutil.move(OldPath,NewPath)
                try:
                    ProductData = RetrieveDataLines(WikiPageURL)
                    ImageFile = GetWikiImage(ProductData,NewPath)
                    if ImageFile == None:
                        NoImage(NewPath)
                    else:
                        PromoName = os.path.split(ImageFile)[-1]
                        NewPromoPath = os.path.join(NewPath,str(ProductIndex) + '_' + ProductName + '.jpg')
                        tn = Image.open(ImageFile)
                        tn.thumbnail(PromoThumbnailSize,Image.ANTIALIAS)
                        tn.save(NewPromoPath, 'JPEG', quality=100)
                except urllib2.HTTPError:
                    shutil.copy(NoImagePath,NewPath)
                return NewPath
            else:
                return Directory
            return Directory


    
        ProductData = None
    ProductPath = RootDirectory
    try:
##        This means that we were able to load the wiki page for this product.
        ProductData = RetrieveDataLines(WikiPageURL)
        ProductName = GetNLAProductName(ProductData).replace(':',' -')
        if ProductName == 'ERROR':
##            This means that a page loads for this product, but there's no product name. It happens rarely.
            ProductName = GetProductNameFromSKU(ProductIndex) ## This function needs a more accurate name
            ProductData = None
    except urllib2.HTTPError:
##         This means that no wiki page exists for this product. (very rare)
        ProductName = GetProductNameFromSKU(ProductIndex)
        ProductData = None
        
        
    NLAProductDirectory = str('0' * max(0,NumberPad - len(str(ProductIndex)))) + str(ProductIndex) + '_' + ProductName + ' (NLA)'
    NLAProductPath = os.path.join(RootDirectory,NLAProductDirectory)
    ImageFile = GetWikiImage(ProductData,NLAProductPath) ## temporarily store the image file in the main directory, i
    if not os.path.isdir(NLAProductPath): ## This should never be true. If so, we should have already returned this path as seen in the code above.
        os.mkdir(NLAProductPath)
    if ImageFile == None:
        NoImage(NLAProductPath)
    else:
        PromoName = os.path.split(ImageFile)[-1]
        NewPromoPath = os.path.join(NLAProductPath,str(ProductIndex) + '_' + ProductName + '.jpg')
        tn = Image.open(ImageFile)
        tn.thumbnail(PromoThumbnailSize,Image.ANTIALIAS)
        tn.save(NewPromoPath, 'JPEG', quality=100)
    return NLAProductPath
 
 
def GetWikiImage(ProductData,ImageDirectory):
    if not os.path.isdir(ImageDirectory):
        os.mkdir(ImageDirectory)
    if ProductData == None:
        return None
    for HTMLLine in ProductData:
        if 'Click for original' in HTMLLine:
            ProductImage = HTMLLine.split('title=\"')[1].split('\"><')[0]
            OutputFileName = SaveImageFile(ProductImage,ImageDirectory)
            return OutputFileName
    return None

for filename in glob.glob('*.zip'):
    if IsTemplateFile(filename):
        filenametemp = filename.split('_')
        skip = len(filenametemp[0])
        newfilename = 'Templates' + filename[skip:]
        oldpath = os.path.join(RootDirectory,filename)
        newpath = os.path.join(RootDirectory,newfilename)
        shutil.move(oldpath,newpath)
    if IsTemplateFile(filename) or IsProductFile(filename):
        SKU = GetSKUFromFilename(filename)
        ProductURL = ProductURLBase + SKU
        try:
            ProductData = RetrieveDataLines(ProductURL)
            ProductName = GetProductName(ProductData).replace(':',' -')
            ProductName = ''.join(c for c in ProductName if c in valid_chars)
            ProductDirectory = str('0' * max(0,NumberPad - len(str(SKU)))) + str(SKU) + '_' + ProductName
            ProductPath = os.path.join(RootDirectory,ProductDirectory)
            
            if not os.path.isdir(ProductPath):
                os.mkdir(ProductPath)
                GetImages(ProductData,ProductPath)
            shutil.move(os.path.join(RootDirectory,filename),os.path.join(ProductPath,filename))
        except urllib2.HTTPError:
            ProductDirectory = GetMissingProduct(SKU)
            ProductPath = os.path.join(RootDirectory,ProductDirectory)
            if not os.path.isdir(ProductPath):
                os.mkdir(ProductPath)
            shutil.move(os.path.join(RootDirectory,filename),os.path.join(ProductPath,filename))
            print "nothing exists for this product.. but it should still be moved into place."
                    
            
    
