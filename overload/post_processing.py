from overload.db import get_db
from flask import url_for

import re


def find_and_replace_image_urls(text:str): # This simplifies the process of inserting images stored on the server, using a syntax similar to normal markdown
    # ![id](number) or ![name](image_name) -> ![alt Text](imageurl)
    x = re.findall(r"!\[id\]\([0-9]+\)", text) # Use regex to find the strings that have the format ![id](id_number)
    db= get_db()
    for image in x: # for each image by id string
        image_id = int(re.findall(r"[0-9]+", image)[0]) # get the id number
        image_db = db.execute(f"SELECT * FROM image WHERE id={image_id}").fetchone() # pull data from db
        if image_db == None:
            image_db = {"id":1, "alt_text": "This image is not available."}
        pattern = f"![id]({image_id})" #get old text to replace
        newString = f"![{image_db['alt_text']}]({url_for('blog.get_image',id=image_db['id'])})" # generate proper markdown string
        text = text.replace(pattern, newString) # replace fake markdown with proper markdown
    
    x = re.findall(r"!\[name\]\([^)]*\)", text) # do the same as above but instead with pattern ![name](image_url)
    for image in x:
        image_name = image.split("(")[1][:-1]
        image_db = db.execute(f"SELECT * FROM image WHERE name='{image_name}'").fetchone()
        if image_db == None:
            image_db = {"id":1, "alt_text": "This image is not available."}
        pattern = f"![name]({image_name})"
        newString = f"![{image_db['alt_text']}]({url_for('blog.get_image',id=image_db['id'])})"
        text = text.replace(pattern, newString)

    return text