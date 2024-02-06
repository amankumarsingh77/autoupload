import asyncio
import aiomysql
import datetime
import string
from uploadTV import upload_serie_from_watchasian
from dramaScraper import Drama


async def getSerie():
    conn = await aiomysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='',
        db='dooo275',
        loop=asyncio.get_running_loop())
    cur = await conn.cursor()
    await cur.execute("SELECT id,TMDB_ID FROM web_series ORDER BY id DESC")
    series = await cur.fetchall()
    for serie in series:
        tmdb_id = serie[-1]
        resp_data = await Drama().request(f"https://api.themoviedb.org/3/tv/{tmdb_id}?api_key=8d6d91941230817f7807d643736e8a49&language=en-US", get="json")
        if resp_data:
            name = resp_data.get("name")
            first_air_date = resp_data.get("first_air_date")
            if first_air_date:
                year = datetime.datetime.strptime(
                    str(first_air_date), "%Y-%m-%d").year
            else:
                year = None
            for char in f"{string.punctuation}·":
                if char in name:
                    if not (char in "&'"):
                        name = name.replace(char, " ")
            print(name)
            watchasian_url = (await Drama().request(f"https://was.watchcool.in/search/?q={name}&year={year}", get="json")).get("url")
            if watchasian_url:
                await upload_serie_from_watchasian(watchasian_url)
                print(serie[0], name, watchasian_url)
    await cur.close()
    conn.close()
asyncio.run(getSerie())
