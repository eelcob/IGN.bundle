import Thumb, CalculateDuration

SEARCH_URL = 'http://search.ign.com/video?query=%s'

def Search(query):
    data = HTML.ElementFromURL(SEARCH_URL % query)
    
    oc = ObjectContainer(title2='Search Results')
    
    for result in data.xpath('//div[@id="searchResults"]/div[@class="video-result clear"]'):
        title = result.xpath('.//a[@class="video-title"]')[0].text.strip()
        Log(title)
        summary = result.xpath('.//span[@class="publisherLink"]/::parent/text()')[0]
        Log(summary)
        video_url = result.xpath('.//a[@class="video-title"]')[0].get('href')
        Log(video_url)
        thumbUrl = result.xpath('.//img[@class="videoThumb"]')[0].get('src')
        Log(thumbUrl)
        duration = CalculateDuration(result.path('.//p[@class="videoDuration"]')[0].text.split(' '))
        Log(duration)
        date = Datetime.ParseDate(result.xpath('.//span[@class="publisherLink"]')[0].text).date()
        oc.add(VideoClipObject(url=video_url, title=title, summary=summary, duration=duration, originally_available_at=date, thumb=Callback(Thumb, url=thumbUrl), art=R('art-default.png')))
    
    return  oc    


#def Thumb(url):
#  if url:
#    try:
#        large_url = url.replace('small', 'large')
#        try:
#          data = HTTP.Request(large_url, cacheTime=CACHE_1MONTH).content
#          return DataObject(data, 'image/jpeg')
#        except:
#            return Redirect(R('icon-default.png'))
#    except:
#        try:
#          data = HTTP.Request(url, cacheTime=CACHE_1MONTH).content
#          return DataObject(data, 'image/jpeg')
#        except:
#            return Redirect(R('icon-default.png'))
#  return None

#def CalculateDuration(duration):
#  
#  durationParts = duration.split(' ')[0].split(':')
#  if len(durationParts) == 3:
#    milliseconds = ((int(durationParts[0])*3600) + (int(durationParts[1])*60) + int(durationParts[2]))*1000
#  elif len(durationParts) == 2:
#    milliseconds = ((int(durationParts[0])*60) + int(durationParts[1]))*1000
#  elif len(durationParts) == 1:
#    milliseconds = (int(durationParts[0]))*1000
#  else:
#    milliseconds = None
#    
#  return milliseconds