NAME = "IGN"
ART = 'art-default.jpg'
ICON = 'icon-default.png'

BASE_URL = 'http://www.ign.com'
TV_URL = 'http://tv.ign.com/index/videos.html'

SERIES_URL = '%s/videos/moreseriesajax' % BASE_URL

####################################################################################################
def Start():

  Plugin.AddPrefixHandler("/video/ign", MainMenu, NAME, ICON, ART)

  Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
  Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

  ObjectContainer.title1 = NAME
  ObjectContainer.view_group = "InfoList"
  ObjectContainer.art = R(ART)
  DirectoryObject.thumb = R(ICON)
  VideoItem.thumb = R(ICON)

  HTTP.CacheTime = CACHE_1HOUR
  HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:10.0.2) Gecko/20100101 Firefox/10.0.2'
  HTTP.Headers['Cookie'] = 'i18n-cc=US; decc=US' # Prevent redirects for people outside the US

####################################################################################################
def MainMenu():

  oc = ObjectContainer()
  data = HTML.ElementFromURL(BASE_URL + '/videos')

  for category in data.xpath('//a[@class="filter-lnk"]'):
    title = category.text
    url = category.xpath('.')[0].get('href')
    oc.add(DirectoryObject(key=Callback(VideosPage, title=title, url=url), title=title, thumb=R(ICON)))

  oc.add(DirectoryObject(key=Callback(Series, title="Series"), title="All Series", summary="Video series on IGN"))
  oc.add(DirectoryObject(key=Callback(Systems, title="Systems"), title="Systems", summary="Browse videos specific to your system of choice."))
  oc.add(DirectoryObject(key=Callback(FeedPage, title="TV", url=TV_URL), title="TV Clips & Videos", summary="TV related videos and clips from IGN."))
  oc.add(SearchDirectoryObject(identifier="com.plexapp.plugins.ign", title="Search", summary="Search IGN for videos", prompt="Search for...", thumb=R(ICON), art=R(ART)))

  return oc

####################################################################################################
def Series(title, pageNum=None, url=None):

  if pageNum:
    oc = ObjectContainer(title2='%s: %d' % (title, pageNum), no_cache=True)
    url = BASE_URL + url
  else:
    pageNum = 1
    oc = ObjectContainer(title2=title, no_cache=True)
    url = SERIES_URL + '?r=' + str(Util.Random())

  data = HTTP.Request(url, cacheTime=0).content
  data = HTML.ElementFromURL(url, cacheTime=0, sleep=1.0)

  for series in data.xpath('//div[@class="grid_16 alpha bottom_2"]'):
    series_title = series.xpath('.//a[@class="grid_4 alpha"]')[0].get('title')
    series_url = series.xpath('.//a[@class="grid_4 alpha"]')[0].get('href')
    series_thumb = series.xpath('.//img[@class="thumb"]')[0].get('src')
    summary = series.xpath('.//p[@class="video-description"]')[0].text

    oc.add(DirectoryObject(key=Callback(VideosPage, title=series_title, url=series_url), title=series_title, summary=summary, thumb=Callback(Thumb, url=series_thumb)))

  more_url = data.xpath('//a[@id="moreVideos"]')

  if len(more_url) > 0:
    more_url = more_url[0].get('href') + '&r=' + str(Util.Random())
    oc.add(DirectoryObject(key=Callback(Series, title=title, pageNum=pageNum+1, url=more_url), title="Next Page", summary="More series from IGN"))

  return oc

####################################################################################################
def Systems(title):

  oc = ObjectContainer(title2=title)
  data = HTML.ElementFromURL(BASE_URL)

  for system in data.xpath('//li[@class="navItem navChannel"]/a[contains(@class, "nav-lnk ")]'):
    title = system.text
    url = system.get('href')
    oc.add(DirectoryObject(key=Callback(FeedPage, title=title, url=url+'/index/videos.html'), title=title, thumb=R(ICON)))

  return oc

####################################################################################################
def VideosPage(title, pageNum=None, url=None):

  if pageNum:
    oc = ObjectContainer(title2='%s: %d' % (title, pageNum), no_cache=True)
  else:
    pageNum = 1
    oc = ObjectContainer(title2=title, no_cache=True)

  if not url.startswith(BASE_URL):
    url = BASE_URL + url

  data = HTML.ElementFromURL(url)

  for episode in data.xpath('//div[@class="grid_16 alpha bottom_2"]'):
    episode_title = episode.xpath('.//a[@class="grid_4 alpha"]')[0].get('title')
    episode_url = episode.xpath('.//a[@class="grid_4 alpha"]')[0].get('href')
    episode_thumb = episode.xpath('.//img[@class="thumb"]')[0].get('src')
    episode_date = episode.xpath('.//span[@class="publish-date"]')[0].text
    episode_summary = episode.xpath('.//p[@class="video-description"]/text()')[1].split('-')[1].strip()
    try:
      duration = episode.xpath('.//ul[@class="video-details"]/li')[0].text.split(' ')[0]
      episode_duration = CalculateDuration(duration)
    except:
      episode_duration = None

    oc.add(VideoClipObject(url=episode_url, title=episode_title, originally_available_at=Datetime.ParseDate(episode_date).date(), summary=episode_summary, duration=episode_duration, thumb=Callback(Thumb, url=episode_thumb)))

  try:
    more_url = data.xpath('//a[@id="moreVideos"]')[0].get('href')
    oc.add(DirectoryObject(key=Callback(VideosPage, title=title, pageNum=pageNum+1, url=more_url), title="Next Page", thumb=R(ICON)))
  except:
    pass

  return oc

####################################################################################################
def FeedPage(title, url):

  oc = ObjectContainer(title2=title)
  data = HTML.ElementFromURL(url)

  for video in data.xpath('//div[@class="headlines"]'):
    video_url = video.xpath('.//a')[0].get('href')
    video_title = video.xpath('.//a')[0].text
    video_summary = video.xpath('.//div[@class="content-headlines"]/text()')[0].strip()
    oc.add(VideoClipObject(url=video_url, title=video_title, summary=video_summary, thumb=R(ICON)))

  return oc

####################################################################################################
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
      pass

  return Redirect(R(ICON))
  
####################################################################################################
def CalculateDuration(timecode):

  seconds  = 0
  duration = timecode.split(':')
  duration.reverse()

  for i in range(0, len(duration)):
    seconds += int(duration[i]) * (60**i)

  return seconds * 1000
