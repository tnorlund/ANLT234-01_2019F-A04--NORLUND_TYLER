

# ANLT234-01_2019F-A03--NORLUND_TYLER

# My Blog Space 

*Does the Tomato Meter Mean a successful Movie?*

Movie reviews can determine whether the viewer will spend their money at the movie theater.

---

I started my career in the movie industry, and I learned that it is competitive, expensive, and full of people that are full of themselves. With this level of stress, I found it difficult to work, and I cannot imagine how bad it is today. Today, studios are not only making more money on successful movies, but they are also losing more money on the "flops" they chose not to see coming. Can movie reviews help the industry figure out which movies will be successful? 

In order to explore the data, I started with [Box Office Mojo](https://www.boxofficemojo.com/). This is a great website that uses data from [IMDb](https://www.imdb.com/). Using this website, I was able to scrape all the data from each [weekend box office](https://www.boxofficemojo.com/weekend/?ref_=bo_nb_di_secondarytab) from 2000 to the current day.  The domestic data obtained here was:
 - Weekend date
 - How much money the top 10 grossing movies made
 - How much money all of the movies grossed
 - The number of new releases 
 - The highest grossing movie 

So let's first look at how the movie industry's grossing has changed over the years.

![Top 10 Gross 2000-2009](https://github.com/tnorlund/ANLT234-01_2019F-A03--NORLUND_TYLER/blob/master/graphs/top_10_gross_2000-2009.png "Top 10 Gross 2000-2009")

![Top 10 Gross 2010-2019](https://github.com/tnorlund/ANLT234-01_2019F-A03--NORLUND_TYLER/blob/master/graphs/top_10_gross_2010-2019.png "Top 10 Gross 2010-2019")

It looks like the best movies have been consistently grossing more money since 2000. It might be messy, but if we look at all the best movie grosses on a single graph we can find some patterns.

![Top 10 Gross All](https://github.com/tnorlund/ANLT234-01_2019F-A03--NORLUND_TYLER/blob/master/graphs/top_10_gross_all.png "Top 10 Gross All")

Here, we see that at the end of August, movies are less likely to do successfully. We also can see that Avengers Endgame is the most successful movie of all time, grossing $357,115,007 it's opening [weekend](https://www.boxofficemojo.com/title/tt4154796/?ref_=bo_se_r_2) (I don't know why people like this movie).

Before we go any further, let's talk about the Rotten Tomatoes [scoring system]([https://www.rottentomatoes.com/about](https://www.rottentomatoes.com/about)). Rotten Tomatoes is one of the few websites that has both the audience's reviews and the critic's reviews. If the critic's consensus is more than 60% positive of the movie, the movie is considered "fresh," otherwise it is "rotten." The website does not label movies based on the audience's reviews. I was able to scrape Rotten Tomatoes for:
 - Tomato Scores
 - Audience Scores
 - The movie's synopsis
 - Meta-data (Rating, Genre, Writer, Director, etc.)

So we know that movie theaters are making more money now than ever before. Are movies reviews correlating to the gross of the most successful films? Let's first look at how the audience and critic reviews have changed since 2000.

![Tomato Score All](https://github.com/tnorlund/ANLT234-01_2019F-A03--NORLUND_TYLER/blob/master/graphs/tomato_score_all.png "Tomato Score All")

![Audience Score All](https://github.com/tnorlund/ANLT234-01_2019F-A03--NORLUND_TYLER/blob/master/graphs/aud_score_all.png "Audience Score All")

Would you look at that! It looks like the audience's reviews movies differently from the critic's. The audience's reviews correlate with the best film's grossing more than the critic's reviews. It'd be easy to stop here, but let's explore how much the reviews have diverged from each other. Below are graphs depicting the difference of the audience scores from the critic's scores. The difference is the audience's score minus the critic's score. 

![Diff in Scores 2000-2009](https://github.com/tnorlund/ANLT234-01_2019F-A03--NORLUND_TYLER/blob/master/graphs/score_diff_2000-2009.png "Diff in Scores 2000-2009")

![Diff in Scores 2010-2019](https://github.com/tnorlund/ANLT234-01_2019F-A03--NORLUND_TYLER/blob/master/graphs/score_diff_2010-2019.png "Diff in Scores 2010-2019")

Here we see that 2018 was the first time the critics reviewed the highest grossing films better than the audience. Looking back at the average audience scores over the years, we can see that the audience began to positively review the best films in 2019. Audiences were poorly reviewing the highest grossing films from 2016-2018. Critics are now poorly reviewing the highest grossing films since 2017.

The only way that I can explain the change in 2018 is that Rotten Tomatoes has changed. For some reason, Rotten Tomatoes has "edited" which reviews are relevant for the highest grossing films. In February 2018, Rotten Tomatoes added a new editor-in-chief, [Joel Meares](https://variety.com/2018/digital/news/rotten-tomatoes-joel-meares-editor-in-chief-1202711540/). Joel's Husband, [Kyle Griffin](https://twitter.com/kylegriffin1?ref_src=twsrc%5Egoogle%7Ctwcamp%5Eserp%7Ctwgr%5Eauthor) is a senior producer at MSNBC, and explains that he is "not as outlandish as [he] could be." With this out of the way, we can look at how all of Rotten Tomatoes reviews have changed since Joel took this position.

![Scores 2019](https://github.com/tnorlund/ANLT234-01_2019F-A03--NORLUND_TYLER/blob/master/graphs/aud_and_tomato_2019.png "Scores 2019")

Here we see that the audience have loved movies during the summer while the critics have poorly reviewed them. Some of these movies are "Aladdin," "Godzilla: King of the Monsters," "The Secret Life of Pets 2," and "Joker." 

Has Joel's editing changed how Rotten Tomatoes reviews movies? If movies are grossing more money year-by-year and audiences have positively reviewed the highest grossing movies, why are Rotten Tomatoes's critics reviewing these movies poorly? Can we still trust the "critics" that tell us which movies to watch? 




