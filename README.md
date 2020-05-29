# Winter-een-mas tool

I should call it something else since we're renaming the event, but here we go.

This is supposed to be the "ultimate" weemas tool. If you don't know what weemas is, check out
[Mega Sweden](https://www.megasweden.se/category/evenemang/) and look for an event that is not called Winter-een-mas.

The tool looks at a list of the games that you own, uses [HowLongToBeat.com](https://howlongtobeat.com/) to look up
how long it takes to beat and compares the results to the current Weemas list.
(It currently takes the Karan-tään-mas list into account as well; I guess that will be incorporated into the official
document in the future.) The output is a list of eligible Weemas games that you own, sorted according to HLTB time.

## Some more details

It needs permission to view "your" Google Sheets, but will of course only look at the sheet(s) specified in the source
code. Google will warn you very carefully about this.

This is based on my personal gaming habits, so I ignore HLTB's "Co-Op" and "Vs." game times, which might not be
appropriate for other people. If there is interest, I might add configuration options for this.

## Future improvements

At the moment, it crawls my personal [Backloggery](https://www.backloggery.com/) account. In the future, it will take some generic input, probably a
text file. I should also learn how to structure a Python module properly and separate the moving parts better.

It would be cool to host this somewhere public so people can use it more easily, but it needs considerable cleanup
first. And, er, a frontend of course.

No tests nor a proper structure at all, because it's Friday evening. I haven't really learned Python 3 yet either, so
this is probably a mish-mash of Python 2 and 3, sorry.

## Honorable mention

This project would not exist without the [weemas-game-list](https://github.com/hagmo/weemas-game-list) project. Credits
to Fenris/Sabin/Fredrik for the idea. However, that project stalled due to the chaotic structure of his input file. Fix
your file, dude! And then use this script instead.
