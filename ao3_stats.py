import urllib.request
import datetime
import re

from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup


###################
##   VERSION 2   ##
###################

# Created 29/08/2018
# Now with very beautiful soup



# dictionary of fandom names + url (Some random and not-so-random fandoms)
fandoms = {"Captive Prince": "Captive%20Prince%20-%20C*d*%20S*d*%20Pacat",
           "Fullmetal Alchemist": "Fullmetal%20Alchemist%20-%20All%20Media%20Types",
           "50 First Dates": "50%20First%20Dates%20(2004)",
           "(500) Days of Summer": "(500)%20Days%20of%20Summer%20(2009)"}

query_type = "work"
query = fandoms["(500) Days of Summer"]

# get data of works available on blurb
#   Returns dictionary of works (class Work) indexed by ids
#   CURRENTLY ON WORKS FOR WORKS NOT BOOKMARKS
def get_works_stats(query, query_type):

    # general stuff
    urlformats = {"main": "http://archiveofourown.org/",
                  "tags": "tags/",
                  "users": "users/",
                  "work": "/works",
                  "bookmark": "/bookmarks",
                  "page": "?page="}

    # instantiate variables
    page_number = 1
    works = {}
    number_of_fics = 0

    # iterate through all pages
    while True:
        try:
            # get URL and convert HTML to string
            url = urlformats["main"] + urlformats["tags"] + query +\
                  urlformats[query_type] + urlformats["page"] + str(page_number)
            page = urllib.request.urlopen(url).read()
            soup = BeautifulSoup(page, "html.parser")
##            soup.prettify()
            
            # get total number of fics if we're at page 1
            if page_number == 1:
                
                no_fics = re.findall(re.compile(' [0-9]+? of (.+?) Works in '),
                                     soup.find("h2", {"class": "heading"}).contents[0])

                # check if there are fics
                #   TODO: Modify to accommodate bookmarks
                if no_fics:
                    try:
                        number_of_fics = int(no_fics[0].replace(',', ''))
                        if number_of_fics == 0:
                            print("No works found. Try another search?")
                            return
                        else:
                            print("{} works found".format(number_of_fics))
                    except:
                        print("Error parsing total number of works.\nExiting function.")
                        return

            # get data of individual work/bookmarks on page into list
            #   TODO: modify to accommodate bookmarks
            works_on_page = soup.find_all("li", {"class": "work blurb group"})

            # if no more returned results, exit loop
            #   TODO: modify to accommodate bookmarks
            if not len(works_on_page):
                break

            # corral works data into works dictionary, where work id is key and
            #   everything else is in a sub-dictionary with things like 'hits'
            #   as keys
            # TODO: modify to accommodate bookmarks
            for curr_work in works_on_page:
                works[curr_work['id']] = Work(curr_work)

            # increment page number
            page_number += 1

        # break if there are any errors
        except URLError:
            break

    # print web scraping results
    if len(works) >= number_of_fics:
        print('Completed without errors')
    else:
        print('Completed with errors')

    return works



class Work:

    def __init__(self, data):

        self.id = data['id']

        ###########
        # GENERAL #
        ###########
        
        # get heading data
        heading = data.find("h4", {"class": "heading"})

        # set title
        self.title = str(heading.find(href = re.compile("/works/")).contents[0])

        # get and set authors
        authors = heading.find_all(rel = re.compile("author"))
        self.authors = []
        for author in authors:
            self.authors.append(str(author.contents[0]))

        # get and set update date
        self.date = datetime.datetime.strptime(data.find("p",
                                                         {"class": "datetime"}).contents[0],
                                               "%d %b %Y")

        # get and set summary
        self.summary = str(data.find("blockquote",
                                     {"class": "userstuff summary"}).p.contents[0])


        ###########
        # FANDOMS #
        ###########
        
        # get and set fandoms
        fandom_heading = data.find("h5", {"class": "fandoms heading"})
        fandoms = fandom_heading.find_all("a", {"class": "tag"})
        self.fandoms = list(map(lambda x: str(x.contents[0]), fandoms))


        #################
        # REQUIRED TAGS #
        #################
        
        # get required tags
        req_tags_data = data.find("ul", {"class": "required-tags"})

        # function to corral multiple tags per required category into list
        def get_req_tags(tag_type):
            tags = req_tags_data.find("span", {"class": re.compile(tag_type)})
            return list(str(tags.span.contents[0]).split(", "))
        
        # set required tags
        self.rating = get_req_tags("rating")
        self.warnings = get_req_tags("warning")
        self.categories = get_req_tags("category")
        self.status = get_req_tags("complete")


        #################
        # OPTIONAL TAGS #
        #################

        # get optional tags
        opt_tags_data = data.find("ul", {"class": "tags commas"})

        # function to corral multiple tags per optional category into list
        def get_opt_tags(tag_type):
            matched_tags = opt_tags_data.find_all("li",
                                                  {"class": re.compile(tag_type)})
            return list(map(lambda x: str(x.a.contents[0]), matched_tags))

        # set optional tags
        self.characters = get_opt_tags("characters")
        self.relationships = get_opt_tags("relationships")
        self.additional_tags = get_opt_tags("freeforms")


        ##############
        # STATISTICS #
        ##############

        # get statistics
        stats_data = data.find("dl", {"class": "stats"})

        # function to extract stats (with option to convert to integer value)
        #   NOTE: keyword argument 'deep' is for stats that have links (e.g. kudos)
        def get_stats(stats_type, to_int = False, deep = False):
            out = stats_data.find("dd", {"class": stats_type})
            # handle works with hidden stats
            if not out:
                return None
            # retrieves data hidden in a <a> tag layer
            if deep:
                out = out.a
            # extract contents and convert to string
            out = str(out.contents[0])
            # convert string to integer
            if to_int:
                out = int(out.replace(',', ''))
            return out

        # set stats for language, words, and hits
        self.language = get_stats("language")
        self.words = get_stats("words", to_int = True)
        self.hits = get_stats("hits", to_int = True)
        self.comments = get_stats("comments", to_int = True, deep = True)
        self.kudos = get_stats("kudos", to_int = True, deep = True)
        self.bookmarks = get_stats("bookmarks", to_int = True, deep = True)

        # set chapter counts
        chapter_stats = re.findall(re.compile('([0-9]+?)/([0-9\?]+)'),
                                   get_stats("chapters"))
        self.chapters, self.total_chapters = map(lambda x: x if x == '?' else int(x.replace(',', '')),
                                                 chapter_stats[0])

    def get_stats(self):
        return {"Language": self.language,
                "Word count": self.words,
                "Hits": self.hits,
                "Comments": self.comments,
                "Kudos": self.kudos,
                "Bookmarks": self.bookmarks,
                "Current chapters": self.chapters,
                "Chapters planned": self.total_chapters}

    def get_descriptions(self):
        return {"Title": self.title,
                "Author(s)": self.authors,
                "Fandoms": self.fandoms,
                "Rating": self.rating,
                "Warnings": self.warnings,
                "Categories": self.categories,
                "Status": self.status,
                "Updated": self.date,
                "Relationships": self.relationships,
                "Characters": self.characters,
                "Additional tags": self.additional_tags,
                "Summary": self.summary}

    def print_stats(self):
        for k, v in self.get_stats().items():
            print(k + ":", v)

    def print_descriptions(self):
        for k, v in self.get_descriptions().items():
            print(k + ":", v)
