import asyncio
import aiomysql
import requests
import datetime
import string
from uploadTV import upload_serie_from_watchasian
from dramaScraper import Drama
async def getSerie():
    conn = await aiomysql.connect(
        host='45.13.132.154',
        port=3306,
        user='cooluser',
        password='Imcooluser@2021',
        db='dramaworldappv9',
        loop=asyncio.get_running_loop())
    cur = await conn.cursor()
    await cur.execute("SELECT TMDB_ID FROM web_series")
    series = await cur.fetchall()
    for serie in series:
        tmdb_id = serie[0]
        resp_data = await Drama().request(f"https://api.themoviedb.org/3/tv/{tmdb_id}?api_key=8d6d91941230817f7807d643736e8a49&language=en-US",get="json")
        name = resp_data.get("name")
        first_air_date = resp_data.get("first_air_date")
        if first_air_date:
            year = datetime.datetime.strptime(str(first_air_date),"%Y-%m-%d").year
        else:
            year = None
        for char in f"{string.punctuation}·":
            if char in name:
                name = name.replace(char," ")
        watchasian_url = (await Drama().request(f"https://was.watchcool.in/search/?q={name}&year={year}",get="json")).get
        await upload_serie_from_watchasian(watchasian_url)
        print(name)
    await cur.close()
    conn.close()
asyncio.run(getSerie())