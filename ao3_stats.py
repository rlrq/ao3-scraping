import urllib.request

from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup

from ao3_stats_classes import *
from ao3_stats_pred import *


###################
##   VERSION 2   ##
###################

# Created 29/08/2018
# Now with very beautiful soup


## SAMPLE USAGE AT END OF EACH MAIN SECTION

# TODO: handle getting data from users' works, bookmarks



###################
##   RETRIEVAL   ##
###################

# get data of works available in blurb
#   Returns dictionary of works (class Work) indexed by ids
#   TODO: CURRENTLY ON WORKS FOR WORKS NOT BOOKMARKS (to fix)
def get_query_items(query, query_type):

    '''
    Gets item info from listing
    Currently only works for works searched via tags (not appropriate for user works etc.)
    '''

    # general stuff (with some unused entries)
    urlformats = {"main": "http://archiveofourown.org/",
                  "tags": "tags/",
                  "users": "users/",
                  "work": "/works",
                  "bookmark": "/bookmarks",
                  "page": "?page="}

    # instantiate variables
    page_number = 1
    items = {}
    num_items = 0

    # iterate through all pages
    while True:
        try:
            # get URL contents and convert HTML to BeautifulSoup object
            url = urlformats["main"] + urlformats["tags"] + query +\
                  urlformats[query_type] + urlformats["page"] + str(page_number)
            page = urllib.request.urlopen(url).read()
            soup = BeautifulSoup(page, "html.parser")
            
            # get total number of items if we're at page 1
            if page_number == 1:
                
                # TODO: CURRENTLY ONLY WORKS FOR FICS (to fix to accommodate bookmarks)
                num_items = re.findall(re.compile(' [0-9]+? of (.+?) Works in '),
                                     soup.find("h2", {"class": "heading"}).contents[0])

                # check if there are items
                #   TODO: Modify to accommodate bookmarks
                if num_items:
                    try:
                        num_items = int(num_items[0].replace(',', ''))
                        if num_items == 0:
                            print("No items found. Try another search?")
                            return
                        else:
                            print("{} items found.\nExtracting data now.".format(num_items))
                    except:
                        print("Error parsing total number of items.\nExiting function.")
                        return

            # get data of individual work/bookmarks on page into list
            #   TODO: modify to accommodate bookmarks
            print("Accessing page", page_number)
            items_on_page = soup.find_all("li", {"class": "work blurb group"})

            # if no more returned results, exit loop
            #   TODO: modify to accommodate bookmarks
            if not items_on_page:
                print("No items found on page {}. Exiting function.".format(page_number))
                break

            # corral item data into items dictionary, where item id is key and
            #   everything else is contained in class Work
            # TODO: modify to accommodate bookmarks
            for curr_item in items_on_page:
                if query_type == "work":
                    items[curr_item['id']] = Work(curr_item)

            # increment page number
            page_number += 1

        # break if there are any errors
        except URLError:
            break

    # print web scraping results
    if len(items) >= num_items:
        print('Completed without errors')
    else:
        print('Completed with errors')

    return items



##### SAMPLE EXECUTION


# dictionary of fandom names + url (Some random and not-so-random fandoms)
fandoms = {"Captive Prince": "Captive%20Prince%20-%20C*d*%20S*d*%20Pacat",
           "Fullmetal Alchemist": "Fullmetal%20Alchemist%20-%20All%20Media%20Types",
           "50 First Dates": "50%20First%20Dates%20(2004)",
           "(500) Days of Summer": "(500)%20Days%20of%20Summer%20(2009)"}

# currently the only query_type handled by the function is "work"
#   TODO: accommodate "bookmark"
query_type = "work"
query = fandoms["(500) Days of Summer"]

# Retrieve all works in (500) Days of Summer fandom, chosen mostly because there aren't a lot of fics lol
summer500_works = get_query_items(query, query_type)






#######################
##   DISPLAY WORKS   ##
#######################

# prints work stats/details/fields nicely (kinda)
def disp_stats(works, *fields):
    '''
    Prints list/tuple/dict of words prettily...kinda.
    (There are still alignment issues)
    '''
    works = dict_to_list(works, "Works")
    # print header
    print('\t' + '\t'.join(map(lambda x: str(x), fields)))
    # print items
    for i, work in enumerate(works):
        print(i+1, '\t' + '\t'.join(map(lambda x: str(x.get(work)), fields)))


# field options for noobs
#   for those who know how to use lambda, feel free to access attributes directly
#   ALT: consider using message passing to get appropriate attributes (e.g. Work_instance.get("title") --> <work title>)
field_options = [work_title, work_id, work_authors, work_fandoms, work_ratings, work_warnings, work_categories,
                 work_status, work_date, work_relationships, work_characters, work_tags, work_summary,
                 work_language, work_words, work_hits, work_comments, work_bookmarks, work_chapters,
                 work_total_chap]



##### SAMPLE EXECUTION

print("\nDisplaying all works in '(500) Days of Summer' fandom")
disp_stats(summer500_works, work_id, work_date, work_title)
#   NOTE: Please use discretion so results don't run off of page






####################
##   FILTERING   ###
####################

# function to filter works
def filter_works(works, *conditions):
    '''
    Filters works
    '''    
    works = dict_to_list(works, "Works")    
    def multi_filter(work):
        for condition in conditions:
            if not condition(work):
                return False
        return True
    return list(filter(lambda x: multi_filter(x), works))


# some boolean operators
#   all numerical values are excluive
#   NOTE: field options are identical to those for disp_stats
#   See sample usage below
def more_than(field, val):
    def helper(work):
        if not is_num(field.get(work)):
            raise TypeError("Stats should be numerical to use 'more_than' function")
        return field.get(work) > val
    return helper

def less_than(field, val):
    def helper(work):
        if not is_num(field.get(work)):
            raise TypeError("Stats should be numerical to use 'more_than' function")
        return field.get(work) < val
    return helper

def is_same(field, val):
    return lambda x: (field.get(x) == val)

def is_complete(completed):
    return lambda x: x.complete() if completed else (not x.complete())



##### SAMPLE EXECUTION

# FILTERING Example 1
#   get works with fewer than 1000 hits
summer500_below1000hits = filter_works(summer500_works,
                                       less_than(work_hits, 1000))
print("\nFILTER 1: Exclude works with 1000 hits or more")
disp_stats(summer500_below1000hits, work_id, work_hits, work_title)

# FILTERING Example 2
#   get completed multichaptered works (>1 chapters)
summer500_complete_multichap = filter_works(summer500_works,
                                            is_complete(True),
                                            more_than(work_chapters, 1))
print("\nFILTER 2: Find only completed multichaptered works")
disp_stats(summer500_complete_multichap, work_id, work_status, work_chapters, work_total_chap, work_title)








#################
##   SORTING   ##
#################


def sort_works(works, field, reverse = False):
    '''
    Sorts works by hits, kudos, etc.
    Default behaviours sorts alphabetical or ascending order unless reverse == True
    '''
    works = dict_to_list(works, "Works")
    return sorted(works, reverse = reverse, key = field)



# NOTE: field options are identical to those for disp_stats
#   See sample usage below
def sort_field(field):
    return lambda x: field.get(x)

# TODO: figure out how to get creative/longer with combinations (e.g. kudos/hits/chapters)
def ratio(field_1, field_2):
    def sort_ratio(work):
        if not is_num(field_1.get(work)) or not is_num(field_2.get(work)):
            raise TypeError("Both stats must be numerical")
        # convert both values into the same type (NumOrQ) before evaluating
        v_1 = NumOrQ(field_1.get(work)) if not isinstance(field_1.get(work), NumOrQ) else field_1.get(work)
        v_2 = NumOrQ(field_2.get(work)) if not isinstance(field_2.get(work), NumOrQ) else field_2.get(work)
        return v_1/v_2
    return sort_ratio





##### SAMPLE EXECUTIONS

# SORTING Example 1
#   sort works with below 1000 hits in descending order of hit count (i.e. highest hit count first)
summer500_below1000hits_desc = sort_works(summer500_below1000hits,
                                          sort_field(work_hits),
                                          reverse = True)
print("\nSORT 1: Works with fewer than 1000 hits sorted in descending order of hit count")
disp_stats(summer500_below1000hits_desc, work_id, work_hits, work_title)


# SORTING Example 2
#   sort works in old -> new order of update date
summer500_oldtonew = sort_works(summer500_works,
                                sort_field(work_date))
print("\nSORT 2: Sorted from oldest to most recent update")
disp_stats(summer500_oldtonew, work_id, work_date, work_title)


# SORTING Example 3
#   sort works in descending order of kudos/hits ratio (i.e. highest kudos/hits first)
summer500_kudos_hits = sort_works(summer500_works,
                                  ratio(work_kudos, work_hits),
                                  reverse = True)
print("\nSORT 3: Sorted in descending order of kudos/hits")
disp_stats(summer500_kudos_hits,
           work_id,
           work_kudos,
           work_hits,
           WorkField("Kudos/Hits", lambda x: str(round(ratio(work_kudos, work_hits)(x) * 100, 2))+' %'),
           work_title)
## NOTE: this super verbose method of displaying kudos/hits by creating a new WorkField object needs to be fixed
