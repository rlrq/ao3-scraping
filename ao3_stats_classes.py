import datetime
import re



###################
##   VERSION 2   ##
##   (CLASSES)   ##
###################

# Created 30/08/2018
# Now with very beautiful soup





######################
##   MAIN OBJECTS   ##
######################

# Main objects inclde Work and Bookmark classes
#   NOTE: class Bookmark is still a WIP

class Work:

    '''
    This class reads the blurb of a work and stores relevant stats/info
    '''

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
        self.authors = list(map(lambda x: str(x.contents[0]), authors))

        # get and set update date
        self.date = datetime.datetime.strptime(data.find("p", {"class": "datetime"}).contents[0],
                                               "%d %b %Y")

        # get and set summary
        self.summary = str(data.find("blockquote", {"class": "userstuff summary"}).p.contents[0])


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
        self.rating = get_req_tags("rating")[0]
        self.warnings = get_req_tags("warning")
        self.categories = get_req_tags("category")
        self.status = get_req_tags("complete")[0]


        #################
        # OPTIONAL TAGS #
        #################

        # get optional tags
        opt_tags_data = data.find("ul", {"class": "tags commas"})

        # function to corral multiple tags per optional category into list
        def get_opt_tags(tag_type):
            matched_tags = opt_tags_data.find_all("li", {"class": re.compile(tag_type)})
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
                # NumOrQ('?') to be used as default for fields without values
                return NumOrQ('?')
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
        chapter_stats = re.findall(re.compile('([0-9]+?)/([0-9\?]+)'), get_stats("chapters"))
        self.chapters, self.total_chapters = map(lambda x: NumOrQ(x) if x == '?' else NumOrQ(int(x.replace(',', ''))),
                                                 chapter_stats[0])

    def __repr__(self):
        return self.id

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
        return {"ID": self.id,
                "Title": self.title,
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

    def complete(self):
        return self.status == "Complete Work"

    def get_date(self):
        return self.date.date()





################
##   FIELDS   ##
################
            
class WorkField:

    '''
    This class was created to allow sorting and filtering for those unfamiliar with lambda.
    '''

    def __init__(self, name, access_key, is_num = False):

        self.field = name
        self.access_key = access_key
        self.num = is_num

    def __repr__(self):
        return self.field

    # work must be a Work class object
    def get(self, work):
        if not isinstance(work, Work):
            raise TypeError("Work must be a Work class object")
        return self.access_key(work)

    def is_num(self):
        return self.num




######################
##   MISC CLASSES   ##
######################

# This class was created to handle None or '?' values where numbers were expected
#   E.g. When hits are not shown (None), or when there are no kudos (None), or when total chapter count is
#           to be determined ('?')
class NumOrQ:

    '''
    This class was created to handle None or '?' values where numbers were expected (therefore Num or Q).
    Non-'?' can be handled as well, but will be treated the same as '?'
    '''

    def __init__(self, val):
        self.val = val

    def __repr__(self):
        return str(self.val)

    def __str(self):
        return str(self.val)

    def is_num(self, other):
        return isinstance(other, int) or isinstance(other, float)

    def __lt__(self, other):
        other_val = other.val if isinstance(other, NumOrQ) else\
                    other if self.is_num(other) else other
        if not self.is_num(self.val):
            return True
        elif not self.is_num(other_val):
            return False
        return self.val < other_val

    def __gt__(self, other):
        other_val = other.val if isinstance(other, NumOrQ) else\
                    other if self.is_num(other) else other
        if not self.is_num(self.val):
            return False
        elif not self.is_num(other_val):
            return True
        return self.val > other_val

    def __le__(self, other):
        other_val = other.val if isinstance(other, NumOrQ) else\
                    other if self.is_num(other) else other
        if not self.is_num(self.val):
            return True
        elif not self.is_num(other_val):
            return False
        return self.val <= other_val

    def __ge__(self, other):
        other_val = other.val if isinstance(other, NumOrQ) else\
                    other if self.is_num(other) else other
        if not self.is_num(self.val):
            return False
        elif not self.is_num(other_val):
            return True
        return self.val >= other_val

    # note that if any value is not a number (or if is zero), the
    #   return value is 0, and the item will be treated as having a
    #   value of 0 when sorted
    def __truediv__(self, other):
        other_val = other.val if isinstance(other, NumOrQ) else\
                    other if self.is_num(other) else other
        if self.val == '?' or other_val == '0' or other_val == '?':
            return 0
        return self.val/other_val



# The following AO3-prefixed classes are not currently in use
#   TODO: incorporate them into the code to allow proper equivalence checking of tags/users
class AO3Author:

    # TODO: accommodate author's pseuds
    def __init__(self, usrname, link):
        self.name = usrname
        self.link = link

class AO3Tag:

    def __init__(self, name, link):
        self.name = name
        self.link = link

    def __eq__(self, other):
        self.link == other.link
    



###################
##     FIELD     ##
##   INSTANCES   ##
###################

# Field objects for class Work
#   Needs to be streamlined lol

work_fields = {"title": WorkField("Title", lambda x: x.title),
               "id": WorkField("ID", lambda x: x.id),
               "authors": WorkField("Author(s)", lambda x: x.authors),
               "fandoms": WorkField("Fandom(s)", lambda x: x.fandoms),
               "ratings": WorkField("Rating", lambda x: x.rating),
               "warnings": WorkField("Warning(s)", lambda x: x.warnings),
               "categories": WorkField("Categories", lambda x: x.categories),
               "status": WorkField("Status", lambda x: x.status),
               "date": WorkField("Date", lambda x: x.get_date()),
               "relationships": WorkField("Relationship(s)", lambda x: x.relationships),
               "characters": WorkField("Character(s)", lambda x: x.characters),
               "tags": WorkField("Additional tags", lambda x: x.additional_tags),
               "summary": WorkField("Summary", lambda x: x.summary),
               "language": WorkField("Language", lambda x: x.language),
               "words": WorkField("Word count", lambda x: x.words, is_num = True),
               "hits": WorkField("Hits", lambda x: x.hits, is_num = True),
               "comments": WorkField("Comments", lambda x: x.comments, is_num = True),
               "kudos": WorkField("Kudos", lambda x: x.kudos, is_num = True),
               "bookmarks": WorkField("Bookmarks", lambda x: x.bookmarks, is_num = True),
               "chapters": WorkField("Chapters", lambda x: x.chapters, is_num = True),
               "total chapters": WorkField("Total chapters", lambda x: x.total_chapters)}
               
work_title = work_fields["title"]
work_id = work_fields["id"]
work_authors = work_fields["authors"]
work_fandoms = work_fields["fandoms"]
work_ratings = work_fields["ratings"]
work_warnings = work_fields["warnings"]
work_categories = work_fields["categories"]
work_status = work_fields["status"]
work_date = work_fields["date"]
work_relationships = work_fields["relationships"]
work_characters = work_fields["characters"]
work_tags = work_fields["tags"]
work_summary = work_fields["summary"]
work_language = work_fields["language"]
work_words = work_fields["words"]
work_hits = work_fields["hits"]
work_comments = work_fields["comments"]
work_kudos = work_fields["kudos"]
work_bookmarks = work_fields["bookmarks"]
work_chapters = work_fields["chapters"]
work_total_chap = work_fields["total chapters"]
