VIDEO_PREFIX = "/video/ign"

NAME = "IGN"

ART  = 'art-default.jpg'
ICON = 'icon-default.png'

BASE_URL = 'http://www.ign.com'
TV_URL = 'http://tv.ign.com/index/videos.html'

SERIES_URL = '%s/videos/series' % BASE_URL

####################################################################################################

def Start():

  Plugin.AddPrefixHandler(VIDEO_PREFIX, VideoMainMenu, NAME, ICON, ART)

  Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
  Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
  
  ObjectContainer.title1 = NAME
  ObjectContainer.view_group = "List"
  ObjectContainer.art = R(ART)
  DirectoryObject.thumb = R(ICON)
  VideoItem.thumb = R(ICON)
  
  HTTP.CacheTime = CACHE_1HOUR

 

def VideoMainMenu():

  oc = ObjectContainer(view_group="InfoList")
  data = HTML.ElementFromURL(BASE_URL + '/videos')
  for category in data.xpath('//a[@class="filter-lnk"]'):
    title = category.text
    #Log(title)
    url = category.xpath('.')[0].get('href')
    #Log(url)
    oc.add(DirectoryObject(key=Callback(VideosPage, title=title, url=url), title=title, thumb=R(ICON)))
  oc.add(DirectoryObject(key=Callback(Series, title="Series"), title="All Series", summary="Video series on IGN"))
  oc.add(DirectoryObject(key=Callback(Systems, title="Systems"), title="Systems", summary="Browse videos specific to your system of choice."))
  oc.add(DirectoryObject(key=Callback(FeedPage, title="TV", url=TV_URL), title="TV Clips & Videos", summary="TV related videos and clips from IGN."))
  oc.add(SearchDirectoryObject(identifier="com.plexapp.search.ign", title="Search", summary="Search IGN for videos", prompt="Search for...", thumb=R(ICON), art=R(ART)))

  return oc
  
def Series(title, pageNum=None, url=None):
  if pageNum:
    oc = ObjectContainer(view_group="InfoList", title2='%s: %s' %(title, pageNum))
    data = HTML.ElementFromURL(BASE_URL + url)
  else:
    pageNum = 1
    oc = ObjectContainer(view_group="InfoList", title2=title)
    data = HTML.ElementFromURL(SERIES_URL)
  
  for series in data.xpath('//div[@class="grid_16 alpha bottom_2"]'):
    try:
      series_title = series.xpath('.//a[@class="grid_4 alpha"]')[0].get('title')
      #Log(series_title)
      series_url = series.xpath('.//a[@class="grid_4 alpha"]')[0].get('href')
      #Log(series_url)
      series_thumb = series.xpath('.//img[@class="thumb"]')[0].get('src')
      #Log(series_thumb)
    except:  
      series_title = series.xpath('.//h3[@class="video-title"]/a')[0].text
      #Log(series_title)
      series_url = series.xpath('.//h3[@class="video-title"]/a')[0].get('href')
      #Log(series_url)
    
    summary = series.xpath('.//ul[@class="video-details"]/li')[0].text
    #Log(summary)
      
    oc.add(DirectoryObject(key=Callback(VideosPage, title=series_title, url=series_url), title=series_title, summary=summary, thumb=Callback(Thumb, url=series_thumb)))
    
  try:
    more_url = data.xpath('//a[@id="moreVideos"]')[0].get('href')
    #Log(more_url)
    oc.add(DirectoryObject(key=Callback(Series, title=title, pageNum=int(pageNum)+1, url=more_url), title="Next Page", summary="More series from IGN", thumb=R(ICON)))
  except:
    pass
  
  return oc

def Systems(title):
  oc = ObjectContainer(view_group="InfoList", title2=title)
  data = HTML.ElementFromURL(BASE_URL)
  
  for system in data.xpath('//li[@class="navItem navChannel"]/a[contains(@class, "nav-lnk ")]'):
    title = system.text
    #Log(title)
    url = system.get('href')
    #Log(url)
    oc.add(DirectoryObject(key=Callback(FeedPage, title=title, url=url+'/index/videos.html'), title=title, thumb=R(ICON)))
    
  return oc

def VideosPage(title, url):
  oc = ObjectContainer(view_group="InfoList", title2=title)
  data = HTML.ElementFromURL(BASE_URL + url)
  
  for episode in data.xpath('//div[@class="grid_16 alpha bottom_2"]'):
    try:
      episode_title = episode.xpath('.//a[@class="grid_4 alpha"]')[0].get('title')
      #Log(episode_title)
      episode_url = episode.xpath('.//a[@class="grid_4 alpha"]')[0].get('href')
      #Log(episode_url)
      episode_thumb = episode.xpath('.//img[@class="thumb"]')[0].get('src')
      #Log(episode_thumb)
      episode_date = episode.xpath('.//span[@class="publish-date"]')[0].text
      #Log(episode_date)
      episode_summary = episode.xpath('.//p[@class="video-description"]/text()')[1].strip().strip('- ')
      #Log(episode_summary)
      duration = episode.xpath('.//ul[@class="video-details"]/li')[0].text
      #Log(duration)
      episode_duration = CalculateDuration(duration)
      #Log(episode_duration)
      
    except:  
      pass
      
    oc.add(VideoClipObject(url=BASE_URL+episode_url, title=episode_title, originally_available_at=Datetime.ParseDate(episode_date).date(), summary=episode_summary, duration=episode_duration, thumb=Callback(Thumb, url=episode_thumb)))
    
    try:
      more_url = data.xpath('//a[@id="moreVideos"]')[0].get('href')
      #Log(more_url)
      oc.add(DirectoryObject(key=Callback(Series, title=title, pageNum=int(pageNum)+1, url=more_url), title="Next Page", summary="More series from IGN", thumb=R(ICON)))
    except:
      pass
  
  return oc


def FeedPage(title, url):
  oc = ObjectContainer(view_group="InfoList", title2=title)
  data = HTML.ElementFromURL(url)
  
  for video in data.xpath('//div[@class="headlines"]'):
    video_url = video.xpath('.//a')[0].get('href')
    video_title = video.xpath('.//a')[0].text
    #Log(video_title)
    video_summary = video.xpath('.//div[@class="content-headlines"]/text()')[0].strip()
    #Log(video_summary)
    oc.add(VideoClipObject(url=video_url, title=video_title, summary=video_summary, thumb=R(ICON)))
  return oc

def Thumb(url):
  if url:
    try:
      url = url.replace('small', 'large')
    except:
      pass
    try:
      data = HTTP.Request(url, cacheTime=CACHE_1MONTH).content
      return DataObject(data, 'image/jpeg')
    except:
      Log("failed to get thumb image")
    
  return Redirect(R(ICON))
  
def CalculateDuration(duration):
  
  durationParts = duration.split(' ')[0].split(':')
  if len(durationParts) == 3:
    milliseconds = ((int(durationParts[0])*3600) + (int(durationParts[1])*60) + int(durationParts[2]))*1000
  elif len(durationParts) == 2:
    milliseconds = ((int(durationParts[0])*60) + int(durationParts[1]))*1000
  elif len(durationParts) == 1:
    milliseconds = (int(durationParts[0]))*1000
  else:
    milliseconds = None
    
  return milliseconds