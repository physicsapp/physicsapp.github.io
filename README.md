# Freebody Physics

A free, open source study app for calculus based introductory physics, built from
[OpenStax University Physics Volume 1](https://openstax.org/details/books/university-physics-volume-1).
Each chapter has short summaries, every key equation, the book's worked examples,
a step by step kinematics solver, and quick review sessions built for a phone: about
8 items, a few minutes, no paper or calculator. Right answers grow a private garden,
one plant per section, and a fully bloomed garden unlocks a rocket launch pad where
students predict a flight with real kinematics. Nothing is behind a paywall.

This first version covers Chapter 3, Motion Along a Straight Line.

## What's in this folder

| Path | What it is | Do you edit it? |
|---|---|---|
| `notes/ch03.txt` | Your summaries and review items | **Yes, this is the one** |
| `book/ch03.json` | Content taken from the OpenStax book by the extraction script | No, regenerate it with the script |
| `img/` | Figures from the book, resized | No |
| `index.html` | The app itself | Only to change how the app works |
| `tools/` | Scripts that read the OpenStax source files and build `book/ch03.json` | Only to add chapters |

## Editing your content

Everything you'd want to change as a teacher is in `notes/ch03.txt`. The top of that
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

- A review session serves up to 8 items: ones due again first, then at least 4 new ones
  when there are new ones left.
- Items come back after 1, 3, 7, and 14 days. Right answers on later days grow the plant most.
- Wrong answers never shrink a plant; the item comes back the next day, and getting it
  right then earns a bonus.
- A plant blooms at 75% of its section's possible growth. One session a day blooms the
  whole chapter in about three weeks; two a day, in about ten days. These numbers are at
  the top of the review code in `index.html` (`SESSION_LEN`, `MIN_NEW`, `GAP`, `BLOOM`).
- Progress is saved in the student's browser only. There are no accounts and nothing is
  sent anywhere. Students can copy a backup code to move their garden to another device.
- Teachers can turn on a fully grown preview garden from the About page.

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
The app currently loads Chapter 3 only; supporting several chapters is the next code change.

## Licenses

- **Content** (everything in `book/`, `notes/`, and `img/`) is adapted from
  *University Physics Volume 1* by Samuel J. Ling, Jeff Sanny, and William Moebs,
  published by OpenStax, and is shared under
  [CC BY NC SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
  Access for free at openstax.org. It may not be used commercially, and changes
  must be shared under the same license. See `CONTENT-LICENSE.md`.
- **Code** (`index.html` and `tools/`) is under the MIT License. See `LICENSE`.

Freebody Physics is not affiliated with or endorsed by OpenStax or Rice University.
