import aiohttp
import asyncio
import json
import re
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from bs4 import BeautifulSoup
def get_ua():
    
    software_names = [SoftwareName.CHROME.value,SoftwareName.FIREFOX.value]
    operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value,OperatingSystem.ANDROID.value]   
    
    user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)

    # Get Random User Agent String.
    user_agent = user_agent_rotator.get_random_user_agent()
    return user_agent
class Drama:
    async def request(self,url,headers:dict={},data:dict={},get="text",method="get"):
        headers["User-Agent"]=get_ua()
        headers["Accept"]="text/html" if get=="text" else "application/json"
        async with aiohttp.ClientSession(headers=headers) as session:
            if method=="get":
                async with session.get(url) as resp:
                    if resp.status == 200:
                        if get=="text":
                            return await resp.text()
                        else:
                            try:
                                data= await resp.json()
                            except Exception as e:
                                data = json.loads(await resp.text())
                            finally:
                                return data
            elif method =="post":
                async with session.post(url,data=data) as resp:
                    if resp.status == 200:
                        if get=="text":
                            return await resp.text()
                        else:
                            try:
                                data= await resp.json()
                            except Exception as e:
                                data = json.loads(await resp.text())
                            finally:
                                return data
    def parse(self,content):
        soup = BeautifulSoup(content,"html.parser")
        return soup
    def get_title(self,soup):
        h1 = soup.find("h1").text.strip()
        splitted = re.split("[\(\)]",h1)
        title_season = splitted[0].strip().split("Season")
        if len(title_season)==2:
            title,season= title_season
        else:
            title=title_season[0]
            season="1"
        episode = splitted[-1]
        episode = episode.split("Episode")[-1].strip()
        title = title.split("Episode")[0]
        return (title.strip(),season.strip(),episode)
    async def get_title_episodes(self,url):
        content = await self.request(url,get="text")
        soup = BeautifulSoup(content,"html.parser")
        title,season_number,episode_number=self.get_title(soup)
        episodes = []
        all_episodes = soup.find("ul",{"class":"all-episode"})
        if all_episodes:
            for episode in all_episodes.find_all("h3",{"class":"title"}):
                mo = re.search(r"/[\-\.\w\d]*",episode.get("onclick"))
                if mo:
                    episode = f"https://watchasian.in{mo.group()}"
                    episodes.append(episode)
        if episodes:
            episodes.reverse()
        return (title,episodes)

    async def get_title_links(self,url):
        content = await self.request(url)
        soup = self.parse(content)
        title,season,episode=self.get_title(soup)
        links = [link.get("data-video") if link.get("data-video").startswith("http") else f"https:{link.get('data-video')}" for link in soup.find("div",{"class":"anime_muti_link"}).find("ul").find_all("li")]
        return (title,season,episode,links)
    async def sb_watchable(self,url):
        id = re.split("[.\-/]",url)[-2]
        url = f"https://sbplay.one/play/{id}?auto=0&referer=&"
        content = await self.request(url)
        soup = self.parse(content)
        for script in soup.find_all("script"):
            if script.text.strip().startswith("//jwplayer"):
                for wl in re.findall("(?P<url>https?://[^\s\"']+)", script.text):
                    if "sbcdnvideo.com" in wl:
                        return wl
    async def downloadable(self,url):
        self.url = url
        for link in await self.get_links(url):
            if "streamtape" in link:
                id = re.split("[./]",link)[-1]
                for _ in range(5): #5 retries
                    content = await self.request(link,headers={"Referer":link,"x-forwarded-for":"7.34.35.78"})
                    if content != None:
                        break;
                soup = self.parse(content)
                for script in soup.find_all("script"):
                    if "document.getElementById('ideoolink').innerHTML" in script.text.strip():
                        innerHTML= script.text.strip().split(";")
                        innerHTML.remove("")
                        url = ""
                        for html in re.findall("(?P<id>['\"\w\d\?.=&_\-/]+)",innerHTML[-1]):
                            if "//" in html:
                                url += "https://"+html.strip("//\"'")
                            elif "xnft" in html:
                                url+=html.lstrip("\"'xnft").rstrip("\"'")
                        return url
    async def watchable(self,url):
        self.url = url
        for link in await self.get_links(url):
            if "sbplay" in link:
                return await self.sb_watchable(url)
            elif "asianload1.com/streaming.php" in link:
                content = await self.request(link)
                soup = self.parse(content)
                for link in soup.find("div",{"id":"list-server-more"}).find_all("li",{"class":"linkserver"}):
                    link = link.get("data-video")
                    if "sbplay" in link:
                        return await self.sb_watchable(link)
if __name__ == "__main__":
    print(asyncio.run(Drama().get_title_episodes("https://watchasian.in/boy-for-rent-episode-12.html")))
