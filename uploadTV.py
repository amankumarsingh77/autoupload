from dramaScraper import Drama
import re
import string
import json
from urllib.parse import urlparse
import asyncio
from getMeta import getSerie
import datetime
_base_url = "https://dooapp.dramaworldapp.xyz"
_base_add_series = f"{_base_url}/admin/dashboard_api/add_web_series_api.php"
_base_add_season = f"{_base_url}/admin/dashboard_api/add_season.php"
_base_add_episode = f"{_base_url}/admin/dashboard_api/add_episode.php"
_base_add_episode_download_link  = f"{_base_url}/admin/dashboard_api/add_episode_download_links.php"
async def search_tv(title,year=None):
    data = await Drama().request(f"https://api.themoviedb.org/3/search/tv?api_key=13297541b75a48d82d70644a1a4aade0&query={title}{'&first_air_date_year='+year if year else ''}&include_adult=true",get="json")
    results = data["results"]
    if results:
        for show in results:
            return show.get("id")
async def add_serie(tmdbid,episodes):
    seasons_in_db = await getSerie(tmdbid)
    meta  = await Drama().request(f"https://api.themoviedb.org/3/tv/{tmdbid}?api_key=8d6d91941230817f7807d643736e8a49&language=en-US",get="json")
    seasons = meta.get("seasons")
    if not seasons_in_db:
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
        serie_id = await Drama().request(_base_add_series,data=data,method="post")
    else:
        serie_id = seasons_in_db[0].serie_id
    if serie_id:
        for season in seasons:
            if int(season["season_number"]) != 0:
                if int(season["season_number"]) !=1:
                    year = datetime.datetime.strptime(str(season["air_date"]),"%Y-%m-%d").year
                    name = meta["name"]
                    for char in f"{string.punctuation}·":
                        if char in name:
                            name = name.replace(char,"")
                    url = (await Drama().request(f"https://was.watchcool.in/search/?q={name}&year={year}",get="json")).get("url")
                    episodes = (await Drama().request(f"https://was.watchcool.in/episodes/?url={url}",get="json")).get("sources")
                episodes_in_db = []
                season_in_db_id = None
                for season_in_db in seasons_in_db:
                    if season_in_db.season_number == int(season["season_number"]):
                        episodes_in_db = season_in_db.episodes
                        season_in_db_id = season_in_db.id
                await add_season(
                    episodes,
                    serie_id,season["name"],
                    int(season["season_number"]),
                    int(season["episode_count"]),
                    season_in_db_id,
                    episodes_in_db
                    )
    return serie_id
async def add_season(episodes,serie_id,s_name,s:int,e:int,season_in_db_id=None,episodes_in_db=[]):
    data = json.dumps({"webseries_id":serie_id,"modal_Season_Name":s_name,"modal_Order":s,"Modal_Status":"1"})
    season_id = await Drama().request(_base_add_season,data=data,method="post") if not season_in_db_id else season_in_db_id
    for episode_number,url in enumerate(episodes,start=1):
        if not (episode_number in episodes_in_db):
            await add_episode(url,season_id,episode_number)
async def add_episode(url,season_id,episode_number):
    meta = await Drama().get_title_links(url)
    episode=""
    for link in meta[-1]:
        # parsed_url = urlparse(link)
        if "streaming" in link:
            episode = f"https://stream.watchcool.in/watch/?source={link}"
            break
    data = json.dumps({
        "season_id":season_id,
        "modal_Episodes_Name":f"Episode {episode_number}",
        "modal_Thumbnail":"",
        "modal_Order":f"{episode_number}",
        "modal_Source":"M3u8",
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
    # print(episodeID)
    for link in meta[-1]:
        parsed_url = urlparse(link)
        if parsed_url.netloc in ("fembed-hd.com","fplayer.info","embedsito.com","diasfem.com","fembed.com"):
            episode = f"{parsed_url.scheme}://fembed.com{parsed_url.path}"
            await add_episode_download_link(episodeID,episode,episode_number)
            break;
async def add_episode_download_link(episodeID,episode,episode_number):
    data = json.dumps({"EpisodeID":episodeID,"Label":f"Episode {episode_number}","Order":episode_number,"Quality":"Auto","Size":"","Source":"Fembed","Url":episode,"download_type":"Internal","Status":"1"})
    await Drama().request(_base_add_episode_download_link,data=data,method="post")
async def upload_serie_from_watchasian(url):
    resp_data = await Drama().request(f"https://was.watchcool.in/episodes/?url={url}",get="json")
    try:
        year = resp_data.get("year")
        if not year:
            mo = re.search("\d{4}",url)
            if mo:
                year = mo.group()
    except:
        year = None
    title = resp_data.get("title")
    episodes = resp_data.get("sources")
    try:
        if episodes:
            tmdbid = await search_tv(title,year)
            await add_serie(tmdbid,episodes)
            return "Serie added"
    except Exception as e:
        return  "Unable add serie"
async def upload_all_serie():
    for char in string.ascii_uppercase:
        content = await Drama().request(f"https://watchasian.sh/drama-list/char-start-{char}.html")
        soup = Drama().parse(content)
        dramas = ["https://watchasian.sh"+re.search(r"/[/\-\.\w\d]*",drama.get("onclick")).group() for drama in soup.find("ul",{"class":"list-episode-item"}).find_all("h3",{"class":"title"})]
        for drama in dramas:
            await upload_serie_from_watchasian(drama)
if __name__ == '__main__':
    print(asyncio.run(upload_serie_from_watchasian("https://watchasian.so/drama-detail/father-is-strange")))