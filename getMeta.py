import asyncio
import aiomysql
from collections import namedtuple


async def getSerie(tmdbid):

    conn = await aiomysql.connect(
        host='142.93.208.56',
        port=3306,
        user='dram_dramahood',
        password='Aman2005@',
        db='dram_dramahood',
        loop=asyncio.get_running_loop())
    cur = await conn.cursor()
    
    await cur.execute("SELECT serie.id,season.id,season.season_order FROM web_series serie INNER JOIN web_series_seasons season ON serie.id = season.web_series_id WHERE serie.TMDB_ID=%(tmdbid)s", {"tmdbid": tmdbid})
    serie = await cur.fetchall()
    
    season_tuple = namedtuple(
        "season", ("id", "serie_id", "season_number", "episodes"))
    seasons = []
    if len(serie):
        for season in serie:
            await cur.execute("SELECT episoade_order FROM web_series_episoade WHERE season_id=%(seasonid)s", {"seasonid": season[1]})
            episodes = await cur.fetchall()
            list_episodes = []
            for episode in episodes:
                list_episodes.append(episode[0])
            seasons.append(season_tuple(
                season[1], season[0], season[-1], list_episodes))
    await cur.close()
    print(seasons)
    conn.close()
    return seasons


# async def main():
#     await getSerie(146393)
#
# asyncio.run(main())