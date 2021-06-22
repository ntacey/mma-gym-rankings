from models import Promotion, Event, Bout, Fighter
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # ignore this because its annoying
from bs4 import BeautifulSoup
import sqlite3
import sys, optparse

def main(promotion_name, url, date):
    fcff = Promotion(promotion_name, url)
    promotions = [fcff]
    for p in promotions:
        http = urllib3.PoolManager()
        response = http.request('GET', p.url)
        p_soup = BeautifulSoup(response.data, 'html.parser')
        # find how many event pages are needed to parse
        nav_parent = p_soup.find('nav', {'class': 'pagination'})
        children = nav_parent.findChildren('span', {'class': 'page'}, recursive=False)
        number_of_pages = 0
        for c in children:
            number_of_pages += 1
        gyms = []
        bouts = []
        for page in range(1, number_of_pages+1):
            if (page == 1):
                foundGyms, foundBouts = getPromotionInfo(p.url, p)
            else:
                foundGyms, foundBouts = getPromotionInfo(p.url + '?page=' + str(page), p)
            gyms.extend(foundGyms)
            bouts.extend(foundBouts)
        counts = {}
        for b in bouts:
            if b.winningGym not in counts:
                counts.update({b.winningGym: 1})
            else:
                counts.update({b.winningGym: counts[b.winningGym]+1})
        print(counts)
        
def getPromotionInfo(url, promotion):
    gyms = set([])
    bouts = []
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    p_soup = BeautifulSoup(response.data, 'html.parser')
    # each page should contain a max of 25 events
    event_sections = p_soup.findAll('section', {'class': 'fcListing'})
    for e in event_sections:
        eventInfo = e.find('div', {'class': 'promotion'})
        eventName = eventInfo.find('a').text if eventInfo.find('a') is not None else 'Unknown'
        eventDate = eventInfo.find('span', {'class': 'datetime'}).text
        event = Event(eventName, eventDate)
        promotion.addEvent(event)
        # go through bouts in this event
        fcBoutsCard = e.find('div', {'class': 'fcBoutsCard'})
        eventBouts = e.findAll('tr')
        # skip first element since this is header
        for b in eventBouts[1:]:
            # should only be two tds
            fighterUrlToFighter = {}
            tds = b.findAll('td')
            try:
                via = tds[0].find('span', {'class': 'good'}).text.split('via\n', 1)[1].strip('\n')
            except IndexError:
                via = 'Unknown'
            fighters = tds[0].findAll('a')
            winningFighterUrl = fighters[0]['href'] # first that comes up should be winner
            winningFighterName = fighters[0].text
            losingFighterUrl = fighters[1]['href'] # second will be loser
            losingFighterName = fighters[1].text
            if winningFighterUrl not in fighterUrlToFighter:
                # go to fighter url to get gym
                response2 = http.request('GET', 'www.tapology.com' + winningFighterUrl)
                p_soup2 = BeautifulSoup(response2.data, 'html.parser')
                try:
                    winningFighterGym = p_soup2.findAll('ul', {'class': 'clearfix'})[4].findAll('li')[7].find('a').text
                except AttributeError:
                    try: 
                        winningFighterGym = p_soup2.findAll('ul', {'class': 'clearfix'})[4].findAll('li')[7].find('span').text
                    except AttributeError:
                        winningFighterGym = 'Unknown'
                gyms.add(winningFighterGym) # will only add if its not in there since its a set
                newFighter = Fighter(winningFighterName, winningFighterUrl, winningFighterGym)
                fighterUrlToFighter.update({winningFighterUrl: newFighter})
                winningFighter = newFighter
            else:
                winningFighter = fighterUrlToFighter[winningFighterUrl]
            if losingFighterUrl not in fighterUrlToFighter:
                # go to fighter url to get gym
                response2 = http.request('GET', 'www.tapology.com' + losingFighterUrl)
                p_soup2 = BeautifulSoup(response2.data, 'html.parser')
                try:
                    losingFighterGym = p_soup2.findAll('ul', {'class': 'clearfix'})[4].findAll('li')[7].find('a').text
                except AttributeError:
                    try: 
                        losingFighterGym = p_soup2.findAll('ul', {'class': 'clearfix'})[4].findAll('li')[7].find('span').text
                    except AttributeError:
                        losingFighterGym = 'Unknown'
                gyms.add(losingFighterGym) # will only add if its not in there since its a set
                newFighter = Fighter(losingFighterName, losingFighterUrl, losingFighterGym)
                fighterUrlToFighter.update({losingFighterUrl: newFighter})
                losingFighter = newFighter
            else:
                 losingFighter = fighterUrlToFighter[losingFighterUrl]
            bout = Bout(winningFighter,losingFighter,winningFighterGym,via)
            print('-- Bout Results --')
            print('Winner: ' + bout.winningFighter.name)
            print('Loser: ' + bout.losingFighter.name)
            print('Gym: ' + bout.winningGym)
            print('Via: ' + bout.wonVia)
            print('\n')
            bouts.append(bout)
            event.addBout(bout)
            winningFighter.addBout(bout)
            losingFighter.addBout(bout)
            #TODO: handle draw
    return gyms, bouts 
        
def writeResultsToDB():
    pass

if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-n", "--promotion_name", dest="promotion_name")
    parser.add_option("-u", "--url", dest="url")
    parser.add_option("-d", "--date", dest="date")
    options, arguments = parser.parse_args()
    
    promotion_name = options.promotion_name
    url = options.url
    date = options.date
    
    # url: https://www.tapology.com/fightcenter/promotions/303-full-contact-fighting-federation-fcff
    main(promotion_name, url, date)
