#!/usr/bin/env python
# coding: utf-8

# # Publications markdown generator for academicpages (modified for my personal preference)
# 
# Takes a set of bibtex of publications and converts them for use with [academicpages.github.io](academicpages.github.io). This is an interactive Jupyter notebook ([see more info here](http://jupyter-notebook-beginner-guide.readthedocs.io/en/latest/what_is_jupyter.html)). 
# 
# The core python code is also in `pubsFromBibs.py`. 
# Run either from the `markdown_generator` folder after replacing updating the publist dictionary with:
# * bib file names
# * specific venue keys based on your bib file preferences
# * any specific pre-text for specific files
# * Collection Name (future feature)


from pybtex.database.input import bibtex
import pybtex.database.input.bibtex 
from time import strptime
import string
import html
import os
import re

#todo: incorporate different collection types rather than a catch all publications, requires other changes to template

bib_file = "../_data/main_reference.bib"

pub_attr = {
    "proceeding": {
        "venuekey": "booktitle",
        "venue-pretext": "in ",
        "category" : "conferences",
        "collection" : {"name":"publications",
                        "permalink":"/publication/"}
        
    },
    "journal":{
        "venuekey" : "journal",
        "venue-pretext" : "in ",
        "category" : "manuscripts",
        "collection" : {"name":"publications",
                        "permalink":"/publication/"}
    },
    # "dataset":{
    #     "venuekey" : "journal",
    #     "venue-pretext" : "in ",
    #     "category" : "datasets",
    #     "collection" : {"name":"publications",
    #                     "permalink":"/publication/"}
    # },
    "preprint":{
        "venuekey" : "preprint",
        "venue-pretext" : "in ",
        "category" : "preprints",
        "collection" : {"name":"publications",
                        "permalink":"/publication/"}
    } 
}

html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;"
    }

def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c,c) for c in text)


parser = bibtex.Parser()
bibdata = parser.parse_file(bib_file)
#loop through the individual references in a given bibtex file
for bib_id in bibdata.entries:
    #reset default date
    pub_year = "1900"
    pub_month = "01"
    pub_day = "01"
    
    b = bibdata.entries[bib_id].fields
    
    try:
        pub_year = f'{b["year"]}'

        #todo: this hack for month and day needs some cleanup
        if "month" in b.keys(): 
            if(len(b["month"])<3):
                pub_month = "0"+b["month"]
                pub_month = pub_month[-2:]
            elif(b["month"] not in range(12)):
                tmnth = strptime(b["month"][:3],'%b').tm_mon   
                pub_month = "{:02d}".format(tmnth) 
            else:
                pub_month = str(b["month"])
        if "day" in b.keys(): 
            pub_day = str(b["day"])

            
        pub_date = pub_year+"-"+pub_month+"-"+pub_day
        
        #strip out {} as needed (some bibtex entries that maintain formatting)
        clean_title = b["title"].replace("{", "").replace("}","").replace("\\","").replace(" ","-")    

        url_slug = re.sub("\\[.*\\]|[^a-zA-Z0-9_-]", "", clean_title)
        url_slug = url_slug.replace("--","-")

        md_filename = (str(pub_date) + "-" + url_slug + ".md").replace("--","-")
        html_filename = (str(pub_date) + "-" + url_slug).replace("--","-")

        #Build Citation from text
        citation = ""

        #citation authors - todo - add highlighting for primary author?
        for author in bibdata.entries[bib_id].persons["author"]:
            if 'Abhishek' in author.first_names[0] and 'Goudar' in author.last_names[0]:
                citation = citation+" <b>"+author.first_names[0]+" "+author.last_names[0]+"</b>, "
            else:
                citation = citation+" "+author.first_names[0]+" "+author.last_names[0]+", "

        #citation title
        citation = citation + "\"" + html_escape(b["title"].replace("{", "").replace("}","").replace("\\","")) + ".\""

        if "journal" in b:
            pubsource = "journal"
        elif "booktitle" in b:
            pubsource = "proceeding"
        else:
            if b["publisher"] == "arXiv":
                pubsource = "preprint"

        #add venue logic depending on citation type
        if pubsource == "preprint":
            venue = pub_attr[pubsource]["venue-pretext"]+ b["number"].replace("{", "").replace("}","").replace("\\","")
        else:
            venue = pub_attr[pubsource]["venue-pretext"]+b[pub_attr[pubsource]["venuekey"]].replace("{", "").replace("}","").replace("\\","")

        # citation = citation + " " + html_escape(venue)
        # citation = citation + ", " + pub_year + "."

        
        ## YAML variables
        md = "---\ntitle: \""   + html_escape(b["title"].replace("{", "").replace("}","").replace("\\","")) + '"\n'
        
        md += """collection: """ +  pub_attr[pubsource]["collection"]["name"]
        md += """\ncategory: """ +  pub_attr[pubsource]["category"]
        md += """\npermalink: """ + pub_attr[pubsource]["collection"]["permalink"]  + html_filename
        
        note = False
        if "note" in b.keys():
            if len(str(b["note"])) > 5:
                md += "\nexcerpt: '" + html_escape(b["note"]) + "'"
                note = True

        md += "\ndate: " + str(pub_date) 

        md += "\nvenue: '" + html_escape(venue) + "'"
        
        url = False
        if "urllink" in b.keys():
            if len(str(b["urllink"])) > 5:
                md += "\npaperurl: '" + b["urllink"] + "'"
                url = True

        md += "\ncitation: '" + html_escape(citation) + "'"
        md += "\n---"        
        ## Markdown description for individual page
        if note:
            md += "\n" + html_escape(b["note"]) + "\n"

        # if url:
        #     # md += "\n[Access paper here](" + b["urllink"] + "){:target=\"_blank\"}\n" 
        #     None
        # else:

        md += "\nUse [Google Scholar](https://scholar.google.com/scholar?q="+html.escape(clean_title.replace("-","+"))+"){:target=\"_blank\"} for full citation"

        md_filename = os.path.basename(md_filename)

        with open("../_publications/" + md_filename, 'w', encoding="utf-8") as f:
            f.write(md)
        print(f'SUCESSFULLY PARSED {bib_id}: \"', b["title"][:60],"..."*(len(b['title'])>60),"\"")
    # field may not exist for a reference
    except KeyError as e:
        print(f'WARNING Missing Expected Field {e} from entry {bib_id}: \"', b["title"][:30],"..."*(len(b['title'])>30),"\"")
        continue
