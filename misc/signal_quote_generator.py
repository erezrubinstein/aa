from Crypto.Random.random import randint

__author__ = 'erezrubinstein'

def get_email_quote(line_break = '\n'):
    # default quote in case of an exception
    quote = { "quote": "I'll be back!", "author": "Arnie" }

    try:
        quotes = [
            { "quote": "I'll be back!", "author": "Arnie" },
            { "quote": "Who is your daddy and what does he do?", "author": "Arnie" },
            { "quote": "Consider dat a divorce!", "author": "Arnie" },
            { "quote": "Come with me if you want to live.", "author": "Arnie" },
            { "quote": "If it bleeds, we can kill it.", "author": "Arnie" },
            { "quote": "If I am not me, who da hell am I?", "author": "Arnie" },
            { "quote": "Hasta la vista, baby!", "author": "Arnie" },
            { "quote": "It's not a tumor!", "author": "Arnie" },
            { "quote": "Get to the Choppa!", "author": "Arnie" },
            { "quote": "Do it!", "author": "Arnie" },
            { "quote": "Who said you could eat MY cookies??", "author": "Arnie" },
            { "quote": "Put that cookie down. NOW!", "author": "Arnie" },
            { "quote": "You blew my cover!", "author": "Arnie" },
            { "quote": "Remember when I said I'd kill you last... I lied!", "author": "Arnie" },
            { "quote": "I live to see you eat that contract, but I hope you leave enough room for my fist because I'm going to ram it into your stomach and break your god-damn spine!", "author": "Arnie" },
            { "quote": "Your clothes, give them to me, now!", "author": "Arnie" },
            { "quote": "You're a funny guy, Sully. I like you. That's why I'm going to kill you last.", "author": "Arnie" },
            { "quote": "Oh, you think you're bad, huh? You're a ****** choir boy compared to me! A CHOIR BOY!", "author": "Arnie" },
            { "quote": "To survive a war, you gotta become war.", "author": "Rambo" },
            { "quote": "I've always believed that the mind is the best weapon.", "author": "Rambo" },
            { "quote": "Ey yo, don't I got some rights?", "author": "Rocky" },
            { "quote": "That depends on what your definition of is is", "author": "Bill Clinton" },
            { "quote": "With clarity comes conviction.", "author": "Stephen Blose & Greg Metro" },
            { "quote": "So what I told you was true... from a certain point of view.", "author": "Obi-Wan" },
            { "quote": "Hostage: Before you leave me, I didn't catch your name? Ali G: Me name is James Bond. James... Bond.", "author": "Ali G" },
            { "quote": "One time when me was high, me sold me car for like 24 chicken McNuggets.", "author": "Ali G" },
            { "quote": "You better learn about these things from my man Buzz Lightyear here.", "author": "Ali G" },
            { "quote": "I haven't slept for 10 days, because that would be too long.", "author": "Mitch Hedberg" },
            { "quote": "If you buy a room temperature cheese that you squeeze out of a can, you probably won't get mad 'cause it the glows-in-the-dark, too.", "author": "Mitch Hedberg" },
            { "quote": "An escalator can never break. It can only become stairs. You should never see an 'Escalator Temporarily Out Of Order' sign, just 'Escalator Temporarily Stairs. Sorry for the convenience.'", "author": "Mitch Hedberg" },
            { "quote": "I don't have a girlfriend. But I do know a woman who'd be mad at me for saying that.", "author": "Mitch Hedberg" },
            { "quote": "I'm gonna punch you in the ovary, that's what I'm gonna do. A straight shot, right to the babymaker.", "author": "Will Ferrel - Anchorman" },
            { "quote": "That's bee-YOU-tee-ful, what is that, velvet?", "author": "Coming to America" },
            { "quote": "'PC Load Letter'? What the f@ck does that mean?", "author": "Michael Bolton" },
            { "quote": "The thing is, Bob, it's not that I'm lazy, it's that I just don't care.", "author": "Peter Gibbons" },
            { "quote": "Bob Porter: Looks like you've been missing a lot of work lately. Peter Gibbons: I wouldn't say I've been *missing* it, Bob.", "author": "Office Space" },
            { "quote": "We're gonna be getting rid of these people here... First, Mr. Samir Naga... Naga... Naga... Not gonna work here anymore, anyway.", "author": "Bob Porter" },
            { "quote": "Samir: Yes, Peter, but I'm not going to do anything illegal. Peter Gibbons: Illegal? Samir, this is America.", "author": "Office Space" },
            { "quote": "Fill all your wishes with my taco-flavored kisses!", "author": "Eric Cartman" },
            { "quote": "Last night I lay in bed looking up at the stars in the sky, and I thought to myself, 'where the heck is the ceiling?'", "author": "Scott Adams" },
            { "quote": "If at first you don't succeed......skydiving isn't for you.", "author": "Scott Adams" },
            { "quote": "Life is a waste of time; time is a waste of life, so get wasted all of the time and have the time of your life.", "author": "Scott Adams" },
            { "quote": "I'm a fighter, not a farmer.", "author": "Rocky (Rocky II)" },
            { "quote": "I'm like a Kentucky fried idiot.", "author": "Rocky (Rocky II)" },
            { "quote": "It's time to kick ass and chew bubble gum... and I'm all outta gum.", "author": "Duke Nukem" },
            { "quote": "Bing bong bing-bong-bing, dl-dl-ding-ding *click* *click* *click-click*, bing bong bing-bong-bing, dl-dl-ding-ding *click* *click*", "author": "Korki Buchek" },
            { "quote": "I feel like American movie star Dirty Harold... Go ahead, make my day, J**", "author": "Borat" },
            { "quote": "Yagshemash! In U.S. and A., if you want to marry a girl, you cannot just go to her father's house and swap her for 15 gallons of insecticide.", "author": "Borat" },
            { "quote": "He is not man... he is like a piece of iron.", "author": "Drago (Rocky IV)" },
            { "quote": "I guess what I'm trying to say, is that if I can change, and you can change, everybody can change!", "author": "Rocky (Rocky IV)" },
            { "quote": "The face of a child can say it all, especially the mouth part of the face.", "author": "Jack Handey" },
            { "quote": "I can picture in my mind a world without war, a world without hate. And I can picture us attacking that world, because they'd never expect it.", "author": "Jack Handey" },
            { "quote": "If trees could scream, would we be so cavalier about cutting them down? We might, if they screamed all the time, for no good reason.", "author": "Jack Handey" },
            { "quote": "A common mistake people make when trying to design something completely foolproof is to underestimate the ingenuity of complete fools.", "author": "Douglas Adams" },
            { "quote": "It is a mistake to think you can solve any major problems just with potatoes.", "author": "Douglas Adams" },
            { "quote": "I love deadlines. I love the whooshing noise they make as they go by.", "author": "Douglas Adams" },
            { "quote": "May the Force be with you... for me... to poop on.", "author": "Triumph, the Insult Comic Dog" },
            { "quote": "All your trade area are belong to us.", "author": "Zero Wing" },
            { "quote": "The African stalking lungfish climbs trees and waits for its prey to walk underneath, whereupon it flings itself off the tree with its mouth open very wide, and hopes.", "author": "Neil Gaiman" },
            { "quote": "Patrician: 'what does your robot do, sam?'    bovril: 'it collects data about the surrounding environment, then discards it and drives into walls'", "author": "bash.org" },
            { "quote": "Lois! Lois! Lois! Lois! Lois! Mom! Mom! Mom! Mommy! Mommy! Mommy! Mama! Mama! Mama! Ma! Ma! Ma! Ma! Mum! Mum! Mum! Mum! Mummy! Mummy! Mumma! Mumma! Mumma!", "author": "Stewie Griffin" },
            { "quote": "It's all about the Pentiums, baby.", "author": "Weird Al" },
            { "quote": "Enough is enough! I have had it with these mo*********ng snakes on this mo*********ng plane!", "author": "Samuel L Jackson" },
            { "quote": "Back in my day, there was this doctor named Doctor Dre. He wasn't a real doctor, though... Do the kids still say 'hell yeah?'", "author": "Jeff's friend Tom" },
            { "quote": "Never gonna give you up, never gonna let you down, never gonna run around and desert you.", "author": "Josh's Computer" },
            { "quote": "Chuck norris can divide by 0", "author": "God" },
            { "quote": "Being in the Philippines is one of the defining moments of my life", "author": "Zach Tai" },
            { "quote": "chicken woot super cool", "author": "Rob" }
        ]

        index = randint(0, len(quotes) - 1)
        quote = quotes[index]

    finally:
        return line_break.join(["\"%s\"" % quote["quote"], "-%s" % quote["author"]])
