from dramaScraper import Drama
from collections import namedtuple
import requests
import aiohttp
import re
import string
import json
import asyncio
_base_add_series = "https://upload.dramaworldapp.xyz/admin/dashboard_api/add_web_series_api.php"
_base_add_season = "https://upload.dramaworldapp.xyz/admin/dashboard_api/add_season.php"
_base_add_episode = "https://upload.dramaworldapp.xyz/admin/dashboard_api/add_episode.php"
_base_add_episode_download_link  = "https://upload.dramaworldapp.xyz/admin/dashboard_api/add_episode_download_links.php"
async def search_tv(title):
    data = await Drama().request(f"https://api.themoviedb.org/3/search/tv?api_key=13297541b75a48d82d70644a1a4aade0&language=en-US&page=1&query={title}&include_adult=true",get="json")
    results = data["results"]
    fields = ("tmdbid","media_type")
    result = namedtuple("result",fields,defaults=(None,)*len(fields))
    if results:
        for show in results:
            if show.get("original_language") and (show.get("original_language").lower() in ("ko","zh","ja","th")):
                tmdbid,media_type = show.get("id"),show.get("media_type")
                return result(tmdbid,media_type)
    return result()
async def add_serie(tmdbid,episodes):
    meta  = await Drama().request(f"https://api.themoviedb.org/3/tv/{tmdbid}?api_key=8d6d91941230817f7807d643736e8a49&language=en-US",get="json")
    try:
        youtube_key = (await Drama().request(f"https://api.themoviedb.org/3/tv/{tmdbid}/videos?api_key=1bfdbff05c2698dc917dd28c08d41096",get="json"))["results"][1]["key"]
    except:
        youtube_key=""
    data = json.dumps({
        "TMDB_ID":tmdbid,
        "name":meta["name"],
        "description":meta["overview"],
        "genres":",".join([genre["name"] for genre in meta["genres"]]),
        "release_date":meta["first_air_date"],
        "poster":f"https://www.themoviedb.org/t/p/original{meta['poster_path']}",
        "banner":f"https://www.themoviedb.org/t/p/original{meta['backdrop_path']}",
        "youtube_trailer":f"https://www.youtube.com/watch?v={youtube_key}",
        "downloadable":1,
        "type":0,
        "status":1
    })
    seasons = meta.get("seasons")
    serie_id = await Drama().request(_base_add_series,data=data,method="post")
    if serie_id:
        for season in seasons:
            if int(season["season_number"]) != 0:
                await add_season(episodes,serie_id,season["name"],int(season["season_number"]),int(season["episode_count"]))
    return serie_id
async def add_season(episodes,serie_id,s_name,s:int,e:int):
    data = json.dumps({"webseries_id":serie_id,"modal_Season_Name":s_name,"modal_Order":s,"Modal_Status":"1"})
    season_id = await Drama().request(_base_add_season,data=data,method="post")
    for episode_number,url in enumerate(episodes,start=1):
        await add_episode(url,season_id,episode_number)
async def add_episode(url,season_id,episode_number):
    meta = await Drama().get_title_links(url)
    episode=""
    for link in meta[-1]:
        if ("fplayer" in link):
            episode = link.replace("fplayer.info","fembed.com")
            break
    data = json.dumps({
        "season_id":season_id,
        "modal_Episodes_Name":f"Episode {episode_number}",
        "modal_Thumbnail":"",
        "modal_Order":f"{episode_number}",
        "modal_Source":"Fembed",
        "modal_Url":f"{episode}",
        "modal_Description":"",
        "Downloadable":"1",
        "Type":"0",
        "Status":"1",
        "add_modal_skip_available_Count":0,
        "add_modal_intro_start":"",
        "add_modal_intro_end":""
        })
    episodeID = await Drama().request(_base_add_episode,data=data,method="post")
    await add_episode_download_link(episodeID,episode,episode_number)
async def add_episode_download_link(episodeID,episode,episode_number):
    data = json.dumps({"EpisodeID":episodeID,"Label":f"Episode {episode_number}","Order":episode_number,"Quality":"Auto","Size":"","Source":"Fembed","Url":episode,"download_type":"Internal","Status":"1"})
    await Drama().request(_base_add_episode_download_link,data=data,method="post")
async def send_head(url):
    async with aiohttp.ClientSession() as session:
        async  with session.head(url) as resp:
            return resp.status
async def upload_serie_from_watchasian(url):
    title,episodes = await Drama().get_title_episodes(url)
    try:
        if episodes:
            tmdbid,media_type=await search_tv(title)
            await add_serie(tmdbid,episodes)
            # for episode in episodes:
            #     await send_head(f"https://coolapi.watchcool.in/?url={episode}&quality=720")
            return "Serie added"
    except Exception as e:
        return  "Unable add serie"
async def upload_all_serie():
    for char in string.ascii_uppercase:
        content = await Drama().request(f"https://watchasian.in/drama-list/char-start-{char}.html")
        soup = Drama().parse(content)
        dramas = ["https://watchasian.in"+re.search(r"/[/\-\.\w\d]*",drama.get("onclick")).group() for drama in soup.find("ul",{"class":"list-episode-item"}).find_all("h3",{"class":"title"})]
        for drama in dramas:
            await upload_serie_from_watchasian(drama)
# asyncio.run(upload_all_serie())
if __name__ == '__main__':
    print(asyncio.run(upload_serie_from_watchasian("https://watchasian.in/drama-detail/kill-me-heal-me")))