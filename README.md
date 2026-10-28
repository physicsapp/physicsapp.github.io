# Freebody Physics

A free, open source study app for calculus based introductory physics, built from
[OpenStax University Physics Volume 1](https://openstax.org/details/books/university-physics-volume-1).
Each chapter has short summaries, every key equation, the book's worked examples,
a step by step kinematics solver, and quick review sessions built for a phone: about
8 items, a few minutes, no paper or calculator. Right answers grow a private garden,
one plant per section, and a fully bloomed garden unlocks a rocket launch pad where
students predict a flight with real kinematics. Nothing is behind a paywall.

The app opens on a chapter list for all 15 chapters of the course. Chapters 1 through 6 are
written so far; the others say "Coming soon" until their files are added.
Each chapter has its own address, like `https://physicsapp.github.io/#ch3`, and its own garden.

## What's in this folder

| Path | What it is | Do you edit it? |
|---|---|---|
| `notes/chNN.txt` | Your summaries and review items, one file per chapter | **Yes, this is the one** |
| `settings.txt` | Questions per review, right answers to grow a flower, daily limit, class dates on or off | **Yes** |
| `schedule.txt` | The class date for each section | **Yes** |
| `book/chNN.json` | Content taken from the OpenStax book by the extraction script | No, regenerate it with the script |
| `img/` | Figures from the book, resized | No |
| `index.html` | The app itself | Only to change how the app works |
| `tools/` | Scripts that read the OpenStax source files and build `book/chNN.json` | Only to add chapters |

## Editing your content

Everything you'd want to change as a teacher is in the `notes` folder, one file per chapter, like `notes/ch03.txt`. The top of that
file explains the format. There are four kinds of blocks, each tagged with its section:

```
## SUMMARY 3.4
In short: Your explanation here, with math like \(v = v_0 + at\).
Watch out: The common mistake.

## QUIZ 3.4
Q: Your question?
A) First choice
B) Second choice
Answer: B
Why: Shown after the student answers.

## DRILL 3.4
Q: A car accelerates from rest at \({{a}}\ \text{m/s}^2\) for \({{t}}\ \text{s}\). How far does it go?
Let: a = 2 to 6 by 2; t = 2 to 5 by 1
Answer: 0.5*a*t^2
Wrong: a*t^2 | You left out the 1/2.
Wrong: a*t | That's the final velocity.
Unit: m
Work: \Delta x = \tfrac12({{a}})({{t}})^2 = {{answer}}\ \text{m}

## GRAPH 3.2
Q: Tap the moment the velocity is zero.
Plot: x = 4*t - t^2; t from 0 to 4; y from 0 to 5
Tap: t = 2
Why: The slope of x(t) is zero at the top.
```

Drills get new numbers every time and are answered by tapping a choice. Each `Wrong:`
line is a tempting wrong answer plus the feedback a student sees if they pick it.

To edit on GitHub: open `notes/ch03.txt`, tap the pencil icon, make your changes, and
press **Commit changes**. The live site updates within a few minutes.

If you make a mistake, like an `Answer:` letter that doesn't match a choice, the app
skips that block and lists the problem with its line number on the **About** page
(the "i" button at the top).

## How the garden works

- Each section has its own plant. Every question answered right on the first try grows it,
  and a set number of right answers makes it bloom. Each bloom adds a rocket part, and a
  full rocket unlocks the launch pad, where students predict a flight with real kinematics.
- The Grow button picks the first section that hasn't bloomed yet. Students can also tap any
  plant to grow that section.
- A question with set choices grows a plant once a day, so students can't bloom a flower by
  repeating one question. Number drills get new numbers every time, so they count every time.
- Wrong answers never shrink a plant; the question comes back the next day.
- Progress is saved in the student's browser only. There are no accounts and nothing is
  sent anywhere. Students can copy a backup code to move their garden to another device.
  One code holds the gardens from every chapter.
- Teachers can turn on a fully grown preview garden from the About page.

### Changing the pace: `settings.txt`

```
Questions per review: 5
Right answers to grow a flower: 15
Reviews per day: 0
Show class dates: yes
```

With these numbers one review grows a flower by about a third, and three reviews bloom it.
`Reviews per day: 0` means no limit, so anyone can grow their garden as fast as they can
answer. Set it to 1 or 2 to slow students down. Practice is always open and never grows plants.

### Class dates: `schedule.txt`

Each line is a date and the sections taught that day, like `1/29: 3.1, 3.2`,
`2/1: 3.3 to 3.6`, or `1/25: Ch. 1`. The date shows on the section's page so students can
find that day's notes. Set `Show class dates: no` in `settings.txt` to hide them.

If either file has a mistake, the About page (the "i" button) lists the line number.

## Putting it online with GitHub Pages (one time setup, easiest on a computer)

1. Create a free account at github.com if you don't have one.
2. Create a new **public** repository, for example `freebody`.
3. On the new repository page, choose **uploading an existing file** and drag in
   everything from this folder (keep the folders as they are). Press **Commit changes**.
4. Go to **Settings › Pages**. Under "Build and deployment", set Source to
   **Deploy from a branch**, branch **main**, folder **/ (root)**, and save.
5. After a minute or two the page shows your site's address, something like
   `https://yourname.github.io/freebody/`. That's the link for students.

## Adding a chapter

The extraction script reads OpenStax's own source files:

```
git clone https://github.com/openstax/osbooks-university-physics-bundle
python3 tools/extract.py osbooks-university-physics-bundle book/ch04.json m58289 m58293 4 "Motion in Two and Three Dimensions"
```

The module ids for each chapter are listed in
`collections/university-physics-volume-1.collection.xml` in that repository.
Skip each chapter's first module, which is its introduction.
A chapter appears in the app's chapter list as soon as `book/chNN.json` is on the site
(two digits, like `ch04`). Add `notes/chNN.txt` for its summaries and review items, in the
same format as `notes/ch03.txt`. Files inside a folder have to be uploaded from inside that
folder on GitHub.

## Licenses

- **Content** (everything in `book/`, `notes/`, and `img/`) is adapted from
  *University Physics Volume 1* by Samuel J. Ling, Jeff Sanny, and William Moebs,
  published by OpenStax, and is shared under
  [CC BY NC SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
  Access for free at openstax.org. It may not be used commercially, and changes
  must be shared under the same license. See `CONTENT-LICENSE.md`.
- **Code** (`index.html` and `tools/`) is under the MIT License. See `LICENSE`.

Freebody Physics is not affiliated with or endorsed by OpenStax or Rice University.
