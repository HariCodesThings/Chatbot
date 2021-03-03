import requests
from bs4 import BeautifulSoup
import re
from recipe_scrapers import scrape_me


available_sites = {"https://www.acouplecooks.com", "https://www.acouplecooks.com", "https://claudia.abril.com.br/",
                    "https://allrecipes.com/", "https://amazingribs.com/", "https://ambitiouskitchen.com/",
                    "https://archanaskitchen.com/", "https://www.atelierdeschefs.fr/", "https://averiecooks.com/",
                    "https://bbc.com/", "https://bbc.co.uk/", "https://bbcgoodfood.com/",
                    "https://bakingmischief.com/", "https://bettycrocker.com/", "https://bigoven.com/",
                    "https://blueapron.com/", "https://bonappetit.com/", "https://bowlofdelicious.com/",
                    "https://budgetbytes.com/", "https://castironketo.net/", "https://cdkitchen.com/",
                    "https://chefkoch.de/", "https://closetcooking.com/", "https://cookeatshare.com/",
                    "https://cookpad.com/", "https://cookieandkate.com/", "https://cookinglight.com/",
                    "https://cookstr.com/", "https://copykat.com/", "https://countryliving.com/",
                    "https://cucchiaio.it/", "https://cuisineaz.com/", "https://cybercook.com.br/",
                    "https://delish.com/", "https://domesticate-me.com/", "https://downshiftology.com/",
                    "https://www.dr.dk/", "https://eatwhattonight.com/", "https://www.eatingbirdfood.com/",
                    "https://eatsmarter.com/", "https://eatsmarter.de/", "https://epicurious.com/",
                    "https://recipes.farmhousedelivery.com/","https://fifteenspatulas.com/", "https://finedininglovers.com/",
                    "https://fitmencook.com/", "https://food.com/", "https://food52.com/", "https://foodandwine.com/",
                    "https://foodnetwork.com/", "https://foodrepublic.com/", "https://www.750g.com",
                    "https://geniuskitchen.com/", "https://giallozafferano.it/", "https://gimmesomeoven.com/",
                    "https://recietas.globo.com/", "https://gonnawantseconds.com/", "https://gousto.co.uk/",
                    "https://greatbritishchefs.com/", "https://www.heb.com/", "https://halfbakedharvest.com/",
                    "https://www.hassanchef.com/", "https://heinzbrasil.com.br/", "https://hellofresh.com/",
                    "https://hellofresh.co.uk/", "https://www.hellofresh.de/", "https://hostthetoast.com/",
                    "https://101cookbooks.com/", "https://receitas.ig.com.br/", "https://indianhealthyrecipes.com",
                    "https://www.innit.com/", "https://inspiralized.com/", "https://jamieoliver.com/",
                    "https://justbento.com/", "https://kennymcgovern.com/", "https://www.kingarthurbaking.com",
                    "https://kochbar.de/", "https://kuchnia-domowa.pl/", "https://lecremedelacrumb.com/",
                    "https://littlespicejar.com/","http://livelytable.com/", "https://lovingitvegan.com/",
                    "https://marmiton.org/", "https://www.marthastewart.com/", "https://matprat.no/",
                    "https://www.melskitchencafe.com/", "http://mindmegette.hu/", "https://minimalistbaker.com/",
                    "https://misya.info/", "https://momswithcrockpots.com/", "http://motherthyme.com/",
                    "https://mybakingaddiction.com/", "https://myrecipes.com/", "https://healthyeating.nhlbi.nih.gov/",
                    "https://cooking.nytimes.com/", "https://nourishedbynutrition.com/", "https://nutritionbynathalie.com/blog",
                    "https://ohsheglows.com/", "https://101cookbooks.com/", "https://www.paleorunningmomma.com/",
                    "https://www.panelinha.com.br/", "https://paninihappy.com/", "https://popsugar.com/",
                    "https://przepisy.pl/", "https://purelypope.com/", "https://purplecarrot.com/",
                    "https://rachlmansfield.com/", "https://realsimple.com/", "https://recipietineats.com/",
                    "https://seriouseats.com/", "https://simplyquinoa.com/", "https://simplyrecipes.com/",
                    "https://simplywhisked.com/", "https://skinnytaste.com/", "https://southernliving.com/",
                    "https://spendwithpennies.com/", "https://www.thespruceeats.com/", "https://steamykitchen.com/",
                    "https://streetkitchen.hu/", "https://sunbasket.com/", "https://sweetpeasandsaffron.com/",
                    "https://tasteofhome.com", "https://tastesoflizzyt.com", "https://tasty.co",
                    "https://tastykitchen.com/", "https://theclevercarrot.com/", "https://thehappyfoodie.co.uk/",
                    "https://thekitchn.com/", "https://thenutritiouskitchen.co/", "https://thepioneerwoman.com/",
                    "https://thespruceeats.com/", "https://thevintagemixer.com/", "https://thewoksoflife.com/",
                    "https://tine.no/", "https://tudogostoso.com.br/", "https://twopeasandtheirpod.com/",
                    "https://vanillaandbean.com/", "https://vegrecipesofindia.com/", "https://vegolosi.it/",
                    "https://watchwhatueat.com/", "https://whatsgabycooking.com/", "https://www.wholefoodsmarket.com/",
                    "https://www.wholefoodsmarket.co.uk/", "https://en.wikibooks.org/", "https://yummly.com/"
 }


def get_links(food_item):
    food_item.replace(" ","+")
    food_item+="+recipe"
    food_item_search = "https://www.google.dz/search?q="+food_item
    page = requests.get(food_item_search)
    soup = BeautifulSoup(page.content,features="html.parser")
    import re
    links = soup.findAll("a")
    link_list = []
    for link in  soup.find_all("a",href=re.compile("(?<=/url\?q=)(htt.*://.*)")):
        link = re.split(":(?=http)",link["href"].replace("/url?q=",""))[0]
        index = link.find("&sa")
        if index > -1:
            link = link[:index]
        link_list.append(link)
    # print(link_list)
    return link_list


def get_root_website(link):
    site = link.strip("https://")
    arr = site.split("/")
    root_website = "https://"+arr[0]+"/"
    return root_website


def check_links(link_list):
    for link in link_list:
        root = get_root_website(link)
        if root in available_sites:
            scraper = scrape_me(link)
            if len(scraper.ingredients()) > 0:
                return (scraper.ingredients(),scraper.instructions(),link)
            # return link,True
    scraper = scrape_me(link_list[0],wild_mode=True)
    if len(scraper.ingredients()) > 0:
        return (scraper.ingredients(),scraper.instructions(),link)
    else:
        return ([],"",link_list[0])
    # return link_list[0],False


link_list = get_links("Gobi Manchurian")
print("Getting best link")
print(check_links(link_list))
# link, valid = check_links(link_list)
# print(link)
# if valid:
#     scraper = scrape_me(link+"/")
# else:
#     scraper = scrape_me(link+"/",wild_mode=True)

# scraper = scrape_me('https://www.indianhealthyrecipes.com/gobi-manchurian-recipe/')
# print(scraper.instructions())