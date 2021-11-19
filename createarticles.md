# How to Create EXAM Compatible Article Set Files
Ideally, you won't need to create these articles by hand, instead, you'll want your generator to create the files for
you. Here's a guide on how the output of the retrieve-and-generate system should be set up.

## Anatomy of an Article Set file

### The Format
Unlike the question file, the articles should be in a `.jsonl` format. This is a reasonable standard for files with
lots of separated text like sets of articles. Each new line of a `.jsonl` file is treated as a separate JSON object. In
EXAM's case, it treats each line as a separate article.

### The SQUID
EXAM was originally designed to read in articles from [TREC CAR Year 3](http://trec-car.cs.unh.edu/). Each article had
an SQUID which was an ID that made it possible to link an article to the appropriate textbook chapter from the
[TQA dataset](https://allenai.org/data/tqa). Since each textbook chapter had an associated question set, this made the
SQUID the link between the article and the question set used in EXAM. EXAM still requires SQUIDs to do this connection.
Your SQUID should be in the following format:

`ignored_text:link_to_question_set`

The ignored_text can be anything you like, blank even, but the colon must be there as well as an id that corresponds to
a set of questions like in `example_question_file.json`. This is the 'link_to_question_set' portion of the SQUID.

### The Title
The title can be anything you want really as long as it is consistent across sets of articles. Say you have 3 different
retrieve-and-generate systems, please make sure that the title for each article linked to question set X is always the
same. 

### The Text
Once you have your major properties, the rest is just the text. You create a "para_body" property that holds a list
of objects. Those objects contain a "text" property and is populated with some amount of text. These text snippets
should ideally be properly punctuated, as that tells the EXAM system how to split up the paragraph into individual
sentences. You can have any number of objects in the "para_body" list, and the text can be as long as you want within
the "text" objects. You can have 1 object per sentence (please include punctuation) or 1 single object within
"para_body" that contains the entire article.