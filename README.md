# Winter-een-mas tool

I should call it something else since we're renaming the event, but here we go.

This is supposed to be the "ultimate" weemas tool. If you don't know what weemas is, check out
[Mega Sweden](https://www.megasweden.se/category/evenemang/) and look for an event that is not called Winter-een-mas.

The tool looks at a the games that you own, uses [HowLongToBeat.com](https://howlongtobeat.com/) to look up how long
they take to beat and compares the results to the current Weemas list. (It currently takes the Karan-tään-mas list into
account as well; I guess that will be incorporated into the official document in the future.) The output is a list of
eligible Weemas games that you own, sorted according to HLTB time.

## Some more details

You need to create an API project at [Google Developer Console](https://console.developers.google.com/), add the Sheets
API and create Oauth credentials in order to run the app. Place the credentials file as `google_credentials.json`.

This is based on my personal gaming habits, so I ignore HLTB's "Co-Op" and "Vs." game times, which might not be
appropriate for other people. If there is interest, I might add configuration options for this.

The string matching between HLTB and your games is primitive, because HLTB can handle pretty fuzzy search terms. Before
the tool searches HLTB, it removes everything except letters and numbers from the game title and the matching is case-
insensitive. If there is only one search result, it is considered a match (but emits a warning if it is not exact). If
there is more than one search result, the match has to be exact. See the next section for a way to tweak this manually.

I wish I had a good idea on how to improve matching to the Weemas list. At the moment it strips everything but letters
and numbers and also removes whitespace, in order to increase the chances of matching. Expect some false positives in
your result and don't get too disappointed if you find that your favourite game has indeed already been played, due to
being called something else in the Weemas document.

## If your games aren't found at HLTB

If you put a file `custom_names.json` in the same directory, you can map any games that you know is listed under a
different name on HLTB but that you don't want to rename in your collection list (or, in my case at Backloggery). The
format is:
```
"What you call the game": "HLTB search string"
```
The HLTB search string should either be the exact name or something that is guaranteed to only return one hit on HLTB.

You can also use the special value `"skip"` to indicate that the game should be completely excluded:
```
"Derp Quest 2: I hate this game": "skip"
```

I'll include the file that I use as an example.

## Future improvements

At the moment, it scrapes my personal [Backloggery](https://www.backloggery.com/) account. In the future, it will take
some generic input, probably a text file. I should also learn how to structure a Python module properly and separate
the moving parts better.

It would be cool to host this somewhere public so people can use it more easily, but it needs considerable cleanup
first. And, er, a frontend of course.

No tests nor a proper structure at all, because it's Friday night. I haven't really learned Python 3 yet either, so
this is probably a mish-mash of Python 2 and 3, sorry.

## Honorable mention

This project would not exist without the [weemas-game-list](https://github.com/hagmo/weemas-game-list) project. Credits
to Fenris/Sabin/Fredrik for the idea. However, that project stalled due to the chaotic structure of his input file. Fix
your file, dude! And then use this script instead.
