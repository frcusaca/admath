<!-- Copyright © 2026-present CAehi.us -->
<!-- SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0 -->
# Open (50)

<!--
How this list is organised:
- Ids are plain numbers, handed out in order and never reused; the number in
  "# Open (N)" is the next one.
- Items sit under topic headings: "## <aspect>" (Content, Style, Fixes, ...), then
  "### <module>", then "#### <part>". Add a heading wherever a new item needs one.
- A big item is a parent; its steps are indented checkboxes beneath it. Tick a
  parent only when all of its children are ticked.
- New items, moves and ticks get an entry at the top of the Log.
-->

## Content

### Module 0

#### Part 0.1: Vectors as moves

- [ ] (0) Lesson 0: introduce the word "heading" early, where vectors first mean a direction
  Where a vector is first read as a direction (Part 0.1, "Vectors as moves", or near it), name it: a vector's **heading** is the way it points, a direction taken *from a position*, and that position is itself a vector. Today "heading" first appears in Part 0.3 ("speed times heading") and then in Deep 9 (heading and facing), with no early introduction.
  Purpose: start the intuition that runs from direction to position. Converting a direction vector (from $\mathbf{0}$ toward point $\mathbf{p}$) into a position (point $\mathbf{p}$) means moving from the origin along that direction: $\mathbf{0} + \mathbf{v} = \mathbf{p}$. A vector can itself be a position.
  - [x] (4) Settle what "heading" means. Decided 2026-11-19: admit that people use the word two ways. A ship's captain orders a heading as an angle, measured from a fixed direction such as north on a compass; and people often call a velocity "the heading". In our documents we say either that something is **heading (or headed) in the direction of** a vector $\mathbf{v}$, of any length, or that **the heading** is the length-1 vector for that direction. Deep 9's first output, which can be shorter than 1 or $(0, 0)$, is therefore not called a heading.
  - [x] (5) Write the definition in Part 0.1, bold where defined and explained in plain words (AGENTS.md Style, Words). Likely next to "One list of numbers, two ways to read it".
  - [x] (6) Tie the later uses back to it: Part 0.3's "speed times heading" and Deep 9's heading and facing.
  - [x] (7) Add "heading" to the Words table in AGENTS.md, in the same commit as (5).
  - [x] (8) Teacher guide 00: mention the word in the Part 0.1 lesson notes.

#### Part 0.2: Adding, subtracting and scaling

- [ ] (1) Lesson 0: a short "clarification" section after vector addition: one written vector, two meanings
  After element-wise addition is introduced (Part 0.2), add a small section that clarifies what a vector written in parentheses, such as $(3, 4)$, means. **As a direction:** a dot starting at $\mathbf{0}$ that takes each axis one at a time, moving the amount written in that slot. **As a point:** where you land when you go from $\mathbf{0}$ in that direction, worked out by element-wise addition, $\mathbf{0} + \mathbf{v} = \mathbf{p}$.
  Could instead sit early in the lesson; decide when writing it. Keep it short, and link it to item (0)'s "heading".
  - [ ] (9) Compare with Part 0.1's existing "One list of numbers, two ways to read it". Decided 2026-11-19: extend that section (the one-axis-at-a-time walk, "headed in the direction of"); then one short piece in Part 0.2 right after "Does the order matter?" with $\mathbf{0} + \mathbf{v} = \mathbf{p}$ and the routes of (2).
  - [x] (10) Add what is new: the direction read one axis at a time, each slot's amount in turn.
  - [x] (11) Write $\mathbf{0} + \mathbf{v} = \mathbf{p}$ as element-wise addition, once addition has been taught.
  - [x] (12) Maybe a picture: `draw_path` walking each axis in turn, then the arrow from home; predict, then run.

- [ ] (2) Lesson 0: show the associative property of vector addition with directions and destinations
  Build on item (1): several directions can be added first and then started from $\mathbf{0}$, or walked one at a time from $\mathbf{0}$, and every way reaches the same final destination, e.g. $(\mathbf{0} + \mathbf{u}) + \mathbf{v} = \mathbf{0} + (\mathbf{u} + \mathbf{v})$. A picture with two or three routes to the same point would make the build-up from direction to position "click".
  Check against existing material first (Part 0.2's "Does the order matter?" and the teacher guide's note on rules kids already know) so it extends rather than repeats them.
  - [ ] (13) Read what exists: Part 0.2's "Does the order matter?" (order, not grouping) and the teacher guide's "Why this is easy" note (grouping does not matter, among five rules). Plan the extension.
  - [x] (14) A picture with two or three routes to the same point; a code cell with a prediction before it.
  - [x] (15) The prose that links it to (1): add the moves first and start from $\mathbf{0}$, or walk them one at a time.
  - [x] (16) Decided 2026-11-19: no new Mastery Coin and no "Beyond the coins"; the short Part 0.2 piece with a picture is enough.
  - [x] (17) Teacher guide 00: lesson note, and answers if (16) adds a problem.

## Style

### Prose: read like good English

- [ ] (3) All modules: read like good English prose, starting with Module 0's introduction
  Module 0's introduction gives orders ("The one rule: predict, then run. Before you run a cell, say out loud what you think it will print or draw. Being wrong is fine. Being surprised is how you learn."). Rewrite it to be friendly and inviting, keeping the predict-then-run idea but as an invitation rather than a command.
  Then do the same in every module: an opening sentence at the top of the document that grabs the reader, a good topic sentence at the start of each introductory paragraph, and, sometimes, a concluding sentence to close a concluding paragraph. The notebooks should read like good English prose that happens to contain a foreign language of graphs, math symbols and computation.
  - [x] (18) Write the convention first: a "Prose" subsection in AGENTS.md's Style section (grabbing opener, topic sentences, concluding sentences where they fit, invite rather than command). Keep "Predict, then run" as an invitation, since Style requires a prediction prompt before code cells.
  - [x] (19) Module 0: rewrite the introduction's "The one rule: predict, then run" paragraph.
  - [x] (20) Module 0: a prose pass over Parts 0.0 to 0.6, the cheat sheet, the proficiency check and the Deep End.
  - [ ] (21) Module 1: prose pass (`01_rover_moves_linear_combinations`).
  - [ ] (22) Module 2: prose pass (`02_span_everywhere_the_rover_can_reach`).
  - [ ] (23) Module 3: prose pass (`03_getting_back_home_dependence`).
  - [ ] (24) Module 4: prose pass (`04_basis_and_dimension`).
  - [x] (25) Decided 2026-11-19 (default, change if wanted): teacher guide 00 gets the same pass, lighter, since its readers are adults.

### Words: inner product and dot product

- [ ] (47) Decided 2026-11-19: a chapter may say "inner product" or "dot product", but each chapter uses one consistently. Change the Words row in AGENTS.md (today: "dot product" only as the name other books and `np.dot` use). Then use the two about equally across the course, or alternate by chapter; list which chapter uses which.

## Kid Comfort

### "Your turn": room to work

- [ ] (27) Every "Your turn" exercise gets its own place to work, with skeleton code in the early modules
  A "Your turn" inside a chapter should be followed by a code cell that is the kid's own workspace, not an instruction to edit a cell further up. In the first few modules that cell starts with skeleton code to change: for the seven-segment display, the cell already draws a 7 and the kid changes it into a 4.
  The hope: kids save their copy of the notebook and can come back to see their own work.
  - [x] (28) Audit every "Your turn" in all modules (done 2026-11-19). No workspace cell of their own: Module 0 Part 0.0's seven-segment digit (the next cell is the pizza orders), Notebook 1 Part 5's "Change the charger", Notebook 4 Part 1's "Try three other chargers". They send the kid back to edit an example: Module 0 Part 0.0's "Change `speed` and `time` in the cell above", Part 0.2's "draw `b` first ... in the cell above", Part 0.6's "Go back to the cell where `v` and `f` are made" (four cells to re-run). Partial skeletons already there: Part 0.3 (length, no length-1 line), Part 0.3's L-p tests, Part 0.4's "two more pairs". Fine as they are: Notebook 2's and 3's "Your turn" sections and Notebook 4's slanted paper and basis check, which have `# change me` cells.
  - [x] (29) Write the convention in AGENTS.md's Style section: a "Your turn" is followed by its own code cell; in the first modules it starts as a copy of the example, with `# change me` marks (the pattern several cells already use).
  - [x] (30) Module 0: the seven-segment cell, already drawing a 7, ready to change into a 4.
  - [x] (31) Module 0: the other "Your turn" cells found by (28).
  - [ ] (32) Modules 1 to 4: the "Your turn" cells found by (28). Decided 2026-11-19 (default): skeleton code that already shows the example's answer in Modules 0 and 1; from Notebook 2 on, `# change me` cells as they are now.
  - [x] (33) Tell kids how to keep their work. A notebook opened in Colab from the course link is not saved unless they make a copy (File, then "Save a copy in Drive"). Say so in Module 0's introduction and on the home page, and add a note to the teacher guide.
  - [x] (34) Teacher guide 00: answers or notes for any "Your turn" whose cell changes.
  - [ ] (35) Maybe a check in `make check` (with a test in `tools/tests/`) that every "Your turn" cell is followed by a code cell.
  - [ ] (36) Predict-then-run magics: the first run asks for a prediction, the second run shows the answer. Two forms, both tested in the repo's IPython on 2026-11-19:
    - a line magic for one expression, `%you_predict 1 + 1`. It remembers the expression text in the kernel, so it needs no hash and nothing for make to write. It can only evaluate, not assign, so "Run all" can never leave a name undefined.
    - a cell magic for a multi-line "Your turn" cell, `%%your_turn 0.0.1`, with no hash (changed 2026-11-19): the first run fingerprints the cell as its original, and the cell runs only once the kid has changed it. Unchanged, it prints a short message instead, along the lines of "Your turn: make a change and answer the question. This cell runs once you have changed something." (wording in (42)). It knows which cell is which by the name on its line (45).
    Decided 2026-11-19: the fingerprint is taken on the first run, so make writes nothing into the cells; authors write the name on the magic line ((39), (45)); the fingerprint ignores leading and trailing whitespace and comments; use the magics only where needed, with no `%%always` for the other cells. The seven-segment cell (30) uses neither, because seeing the 7 is the point. The memory resets with the kernel, so a restart asks again.
    - [x] (37) Put both in their own module, so `__init__.py` stays plain (rule 4); `register_magic_function` needs no decorator. Tests in `python/tests/`. The setup cell loads it as an IPython extension, `%load_ext vecdraw._predict` (the module defines `load_ipython_extension(ipython)`), so nothing new lands in the kids' variables.
    - [x] (38) Cell form: the fingerprint strips whitespace and removes comments with Python's `tokenize`, not by cutting at `#`, which would break strings such as `"#ff0000"`. Decided 2026-11-19 (default): blank lines and trailing spaces do not count either.
    - [ ] (39) A check in `make check`, like `check-coins`: every `%%your_turn` has a name of the right shape, no name is used twice, and names are not renumbered once published. Tests in `tools/tests/`; AGENTS.md's map and Commands updated if it is a new script.
    - [ ] (40) Cell form: on a first "Run all" every guarded cell is skipped, so a later cell that uses a name it defines fails with `NameError`. The tool in (39) rejects a guarded cell that defines a name used further down.
    - [x] (41) Builds: the site, PDF and teacher-guide runs execute each cell once and would publish the prompt in place of the answer. `run_notebooks.py` and `stage_site.py` set an environment variable that makes the magics always run (keep the teacher guide's "All N checks passed").
    - [ ] (42) The names and the messages. Decided 2026-11-19: `%guess_first` (line) and `%%your_turn` (cell). `%%your_turn`'s message says, more gracefully: "Your turn: make a change and answer the question. This cell runs once you have changed something." Add the names to AGENTS.md's Style ("Predict, then run").
    - [ ] (43) Pick the cells that use each form, from the audit (28).
    - [x] (44) Hide the magics' memory from the kids (decided 2026-11-19). The set of cells that already asked lives inside the module under a private name (`_asked`), never in the notebook's variables, so a kid cannot see it, overwrite it or trip over it. Watch out: the setup cell runs `from vecdraw import *`, and without `__all__` (rule 4 forbids it) that copies every public name in `vecdraw`, including a loaded submodule. A submodule named `predict` would land in the kids' variables as `predict` once loaded, so give the module a private name such as `_predict`. A test checks that loading the magics adds no name to the notebook's variables.
    - [ ] (45) How `%%your_turn` knows which cell it is after the kid has edited it. Decided 2026-11-19: a human-readable name on the magic line, written by the author, `%%your_turn 0.5.1`: module, part, and which "Your turn" it is in that part (a book's unit, an exercise; not a Jupyter cell number). Counting follows the course: 0-based where the module is. Modules 1 to 4 still number parts from 1 (see (48)); their names follow the parts as they stand until then. No quotes needed; quotes accepted. The magic keeps `{name: first-run fingerprint}` in its private memory (44).
      Why not the editor's cell id: the kernel learns it only if the editor sends it with the run request (`cellId`, passed on as `info.cell_id`). Tested 2026-11-19: sent gives the id, not sent gives `None`. JupyterLab, Notebook 7 and VS Code send it; `nbclient`, which `make` uses, does not; Colab is undocumented and untested. A name on the magic line works everywhere, including a copy saved to Drive.
      - [ ] (46) Optional, for curiosity: in Colab, run `print(get_ipython().kernel.get_parent()["metadata"])` and see whether Colab sends a cell id. It changes nothing above.

## Structure

- [ ] (48) Renumber every module to count from 0, like Module 0: "Module N" titles, parts N.0, N.1, ...; today Modules 1 to 4 are titled "Notebook N" with Part 1, Part 2, .... Update the chapter navigation, `index.qmd`, every cross-reference ("Part 6 of Notebook 1"), and the `%%your_turn` names (45).

## Fixes

- [ ] (49) Module 4, Deep 1 points to "Notebook 0, Part 5" for what is special about $\mathbf{p}$ and $\mathbf{q}$ (they are perpendicular). Perpendicular and the sign rule are Part 0.4 today.

- [x] (26) Teacher guide 00 says "the answer key for all 70 Mastery Coins" in its opening paragraph, but its "What changed" list says "There are now 71 coins", and the student notebook has 71. Make the opening say 71.

# Log

## (33): keep your work, on the home page
*2026-11-19 14:15* done

index.qmd says how to save a copy in Drive, and its "one rule" became an invitation. Module 0's introduction and the teacher guide already say it.

## (8), (17), (34), (25): teacher guide 00
*2026-11-19 14:13* done

Conventions: the three uses of heading, the two magics, and saving a copy in Drive (also in session 1's plan). Part 0.1: heading notes; Part 0.2: Many routes, one place, and the swap's answer; Part 0.3: the heading toward Q, the Your turn answer; Part 0.6: answers for %%your_turn 0.6.1. The car row says "heading" the new way. Prose pass (25): the guide already reads well; only these additions.

## (20): Module 0 prose pass
*2026-11-19 14:10* done

Topic sentences at the start of Parts 0.0, 0.2, 0.3, 0.4 and 0.5 and the calculator section; invitations instead of orders in a few prompts; the inner-product-with-itself pair now ends on a concluding sentence. The rest already read as prose and is unchanged.

## (31): Module 0's other "Your turn" cells
*2026-11-19 14:08* done

Part 0.3's cell has a line for the length-1 version; Part 0.4's has a place for two pairs; Part 0.6's exercise has its own `%%your_turn 0.6.1` cell that recomputes all three answers, and the coins moved to their own markdown cell.

## (4) refined: three uses of "heading", each said exactly
*2026-11-19 14:06* changed

The user added "heading toward a point Q": from P, the direction of Q - P, and the heading (Q - P)/||Q - P||. Part 0.1 lists the three phrases; Part 0.3 gives the formula; AGENTS.md's Words row says to always say which.

## (11), (12), (14), (15), (16): many routes, one place
*2026-11-19 14:04* done

Part 0.2: the swap is a `%%your_turn 0.2.1` workspace; a new "Many routes, one place" writes 0 + v = p as element-wise addition, then three routes to (5, 2) with `%guess_first` and a picture, and a concluding sentence on grouping. No new coin.

## (4)-(7), (10): heading in the direction of a vector, and the heading
*2026-11-19 14:02* done

Part 0.1 admits both everyday uses and says how the course uses the word, and reads a point one slot at a time. Part 0.3 defines the heading as the length-1 vector. Deep 9's first output is now `go` (length at most 1, (0, 0) stands still). AGENTS.md's Words table has the row.

## (19), (30): Module 0's introduction and Part 0.0's workspaces
*2026-11-19 13:59* done

The opening invites (a question, then "guess first") instead of giving a rule, and says how to keep work in Colab (part of (33)). Part 0.0: `%guess_first` is introduced after the calculator cell; the speed, color and seven-segment exercises each get their own cell, the digit already drawing a 7.

## (37), (38), (41), (44): the predict magics, their tests and the build override
*2026-11-19 13:50* done

`python/src/vecdraw/_predict.py` with `%guess_first` and `%%your_turn`, 12 tests; the setup cells load it; `run_notebooks.py` sets VECDRAW_ALWAYS_RUN=1. Kept the first-run fingerprint (decided 2026-11-19: after a restart a kid may need one more change); from the second unchanged run the message says "add or delete a ; at the end of a line" (the user's wording; `;;` is a syntax error, and a `;` on the last line hides a bare value in IPython).

## (18), (29), (47) conventions in AGENTS.md's Style
*2026-11-19 13:39* done

Style now has a Prose subsection, a "Your turn" rule, and "inner product, dot product" as two names with one per chapter. (47) stays open for balancing the chapters.

## (26) the coin count in teacher guide 00
*2026-11-19 13:37* done

The opening now says 71 Mastery Coins, like the "What changed" list and the notebook.

## decisions for step 1; (47), (48), (49) created
*2026-11-19 13:35* planning

(4) heading: admit both uses (a captain's compass angle; a velocity), then say "heading in the direction of v" or "the heading" = length-1 vector. (9) extend Part 0.1, one short piece in Part 0.2. (16) no new coin. (42) `%guess_first`, `%%your_turn`. (45) the third number counts "Your turn" exercises, not cells. (47) either "inner product" or "dot product", one per chapter, balanced across the course. (48) renumber modules from 0. (49) a stale cross-reference in Module 4.

## (45) changed: a human-readable name on the line, `%%your_turn 0.5.1`; (36) runs only after a change
*2026-11-19 12:53* changed

The author writes the name, so (39) is only a check (shape, no repeats). `%%your_turn` never runs an unchanged cell; its message goes in (42).

## (45) decided: the notebook's own cell id, written on the `%%your_turn` line
*2026-11-19 12:50* changed

The editor's `cellId` reaches the kernel only when sent (tested: sent gives the id, unsent gives None; nbclient sends none, Colab unknown). So a readable cell id goes on the magic line, written and checked by (39). (46) created: a Colab probe, optional.

## (36) changed: `%%your_turn` fingerprints the cell on its first run; (45) created
*2026-11-19 12:49* changed

No written hash: the first run's fingerprint is the original, then the same logic. (45): knowing which cell is which after an edit; nbclient sends no cell id, Colab untested.

## (44) Hide the magics' memory from the kids
*2026-11-19 12:47* created

Child of (36). The memory is a private `_asked` inside a private module, loaded with `%load_ext`; `from vecdraw import *` would otherwise leak a public submodule name. (37) updated to match.

## (36) reworked: a line magic and a cell magic, both asking once and then running
*2026-11-19 12:46* changed

`%you_predict <expression>` (no hash) and `%%your_turn <hash>`; first run asks for a prediction, second run shows the answer. Steps renumbered under (36): (37)-(41) rewritten, (42) names, (43) which cells.

## (36) A cell magic that runs a "Your turn" cell only once it has changed
*2026-11-19 12:43* created

Child of (27), steps (37)-(41). Make writes the hashes; the fingerprint ignores whitespace and comments; used only where needed (not the seven-segment cell), no `%%always`.

## (27) Every "Your turn" exercise gets its own place to work, with skeleton code in the early modules
*2026-11-19 12:37* created

New branch "Kid Comfort". A workspace cell after each "Your turn", with skeleton code in the first modules (a 7 to change into a 4), so kids can save their notebook and see their work. Steps (28)-(35); the audit found three "Your turn" exercises with no cell of their own.

## restructured into a hierarchy
*2026-11-19 09:23* planning

Grouped by aspect (Content, Style, Fixes), then module and part. Split (0) into (4)-(8), (1) into (9)-(12), (2) into (13)-(17) and (3) into (18)-(25). Added (26), a coin count found while checking. While splitting: Part 0.1 already has "One list of numbers, two ways to read it", which overlaps (1); and "heading" means a length-1 vector in Part 0.3 but can be (0, 0) in Deep 9.

## (3) All modules: read like good English prose, starting with Module 0's introduction
*2026-11-19 09:22* created

Module 0's "The one rule: predict, then run" reads as a command; make it friendly. Every module: a grabbing opening sentence, topic sentences for introductory paragraphs, concluding sentences where they fit; prose with math inside.

## (2) Lesson 0: show the associative property of vector addition with directions and destinations
*2026-11-18 14:38* created

Build on item (1): add directions first and then start from 0, or walk them one at a time from 0; every way reaches the same destination. Check Part 0.2's "Does the order matter?" first.

## (1) Lesson 0: a short "clarification" section after vector addition: one written vector, two meanings
*2026-11-18 14:38* created

A vector in parentheses as a direction (a dot from 0, one axis at a time) and as a point (0 + v = p by element-wise addition). After Part 0.2, or earlier.

## (0) Lesson 0: introduce the word "heading" early, where vectors first mean a direction
*2026-11-18 14:38* created

Heading = the direction a vector points, from a position (itself a vector). Starts the intuition direction to position: 0 + v = p.

## session started
*2026-11-18 14:38* planning

Scratch list for small lesson changes, each described in at most two short paragraphs. Collected now; formalized and applied later. Nothing in the lessons is edited yet.
