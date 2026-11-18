<!-- Copyright © 2026-present CAehi.us -->
<!-- SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0 -->
# Course design: problems first, theorems as shortcuts

This is how new study material for *Linear Algebra Circle* should be written.
It is for anyone adding a part, a Deep End task or a whole module, human or AI
agent. Read it together with `AGENTS.md` ("Rules that never bend" and "Style");
this file says what to write, `AGENTS.md` says how it must look.

## The direction

In the course author's words:

> Put this type of thinking through a real-world problem step by step, figuring
> out what we need, as the primary driving direction and pattern for these study
> materials. We obviously eventually expect the student to develop a yearning to
> come up with those "theorems" that just answer the questions directly without
> hassle. [...] They develop an appreciation for math, organization, rules, and
> theoretic analysis that all enhances our ability to do these things as we
> develop the course.

So the order is: a problem the kids care about, then the question it forces,
then the slow way, then the structure, then the rule. A theorem should arrive
as relief from work the kids have already done by hand, not as a fact to memorize.

## The pattern, step by step

The model is the chase in Notebook 00's Deep End ("Deep 7: The chase",
"Deep 9: Write the chaser's brain", "Deep 10: Did they meet?") together with
Part 0.3's "Beyond the coins: other ways to measure size" and "Deep 8: Other
sizes, same rules?". Each step below names what that example does.

1. **A real problem, small enough to build.** Something a kid would want to
   make anyway: a game, a robot, a picture. *Chase:* an NPC runs laps on a square
   track; you write the chaser. A radar base station at $(0, 0)$ reports where the
   NPC is, so the move from you to it is something you must work out yourself
   ("radar echo minus me").
2. **Build it and play with it.** Give a runnable harness and a first, naive
   attempt, and let the kids change numbers and rules. *Chase:* Deep 9's `chase`
   cell and the first rule "look straight at it and walk straight at it". The
   prompts ask for predictions and experiments: try slower speeds, aim ahead,
   wait at one spot, change `step_time`, run away until the safety limit stops it.
3. **Hit a real question.** Playing raises a question the code has to answer
   and the kids cannot yet. *Chase:* "did we touch during this time step, at the
   same moment?" Being on the NPC's path is not enough; it has to be there then.
4. **Try it the slow way first: by hand, brute force, pictures.** Let the
   question be hard for a while. *Chase:* the teacher guide's Deep End table
   says kids start with the picture: the touch circle sweeps a rounded rectangle
   during a step, and crossing it is necessary but not enough (Deep 10,
   question 1). Deep 4 ("Is the
   shortcut ever longer?") is the brute-force version of the same habit: 1000
   random pairs before any proof.
5. **Notice the structure and name it.** A change of view makes the hard part
   simple. *Chase:* ride along with the NPC. The move from you to it at moment
   $s$ of the step is $\mathbf{r}_0 + s\mathbf{d}$, which is linear in $s$
   (Deep 10, question 2). Meeting exactly is two equations in one unknown, so it
   almost never happens; that is *why* the chase needs a touch range (question 3).
6. **State the rule.** Now the math falls out, and it has a name. *Chase:* a
   box touch zone (a square one is an $L_\infty$ size at most $R$) turns into a
   **system of linear inequalities** in $s$ (question 4). A round one turns into a
   curve in $s$ whose lowest point comes from inner products (question 6). Deep 9
   lets kids switch between the two shapes, and question 7 asks for both in 3D.
7. **Test the rule in code, with numbers, before trusting it.** *Chase:* kids
   finish `my_caught_in_box` and run it on five prepared cases next to
   `closest_during_step`. *Norms:* "Your turn" in Part 0.3's "Beyond the coins"
   and Deep 8 have kids check $\lVert \mathbf{v} \rVert_\infty \le \lVert \mathbf{v} \rVert_2 \le \lVert \mathbf{v} \rVert_1$
   and the shortcut rule with their own `lp_norm`, `max_norm` and `count_norm`,
   and find where the rules break ($L_0$, $p = 0.5$).
8. **Use the rule to answer the original question quickly.** *Chase:* one
   function call decides "caught" for every step of every chase, for any rule a
   kid writes.
9. **Reflect on what the rule bought.** Ask what was hard before and is easy
   now, and what the rule does not cover. *Chase:* why does the square catch
   whenever the circle does (the square holds the circle)? Why does
   `closest_during_step` keep $s$ between 0 and 1? Each Deep task ends with
   "*This leads to: ...*" so kids see the road ahead.

Not every unit needs all nine steps at full size. A coin-sized problem may do
steps 3 to 7 in a few lines. But the order should hold: the need comes before
the rule.

The rover notebooks (01 to 04) already follow this order at the scale of a
whole notebook: "Reach the charger" and "Let the computer do the boring part"
come first, and only then "The name for this" gives the word *linear combination*.

## How the pattern fits the existing conventions

- **Predict, then run.** Text before a code cell asks for a prediction
  (`AGENTS.md`, "Style"). In the pattern this is how steps 2 and 7 work: the kid
  commits to a guess, then the code answers. Committed notebooks carry no
  outputs (rule 3), so the guess is real.
- **Mastery Coins are fluency, not discovery.** Coins (`### Mastery Coins 0.3`,
  then `#### M 0.3.1` and so on; bronze, silver, gold) practise skills that a
  part has already built, on paper unless marked **(code)**. They can carry
  small real stories (M 0.3.9 is a chaser NPC's velocity), but they are not where
  new ideas are found.
- **Discovery lives in "Beyond the coins" and the Deep End.** A
  `### Beyond the coins: ...` section after a part's coins holds extra material
  off the coin track (Part 0.3's $L_p$ norms). "The Deep End" at the bottom of a
  notebook holds longer, open tasks with fewer hints ("You do not have to do
  these"). Most of the problem-first work goes here.
- **The teacher guide holds the answers.** `00_teacher_guide.ipynb` has the
  coin answer key (one row per coin, enforced by `check-coins`), answers to
  "Beyond the coins" (for example "Answers to Deep 8"), and a Deep End table of
  "What kids find" and "Leads to", which records the expected route, including
  the wrong turns (Deep 10's rounded rectangle). Numbers in it are recomputed
  in the "Check the key" cell, which must print "All N checks passed." (Deep 10
  checks the box test, `caught_in_box`, there).
- **Style.** Vectors bold ($\mathbf{r}_0$, $\mathbf{d}$), numbers and moments
  thin ($s$, $R$), inner product $\langle \mathbf{a}, \mathbf{b} \rangle$, length
  $\lVert \mathbf{a} \rVert$. No raised dot or times cross: $(3)(4)$, $2\mathbf{a}$,
  $s\mathbf{d}$. A new word is bold where it is defined, in plain words (Part 0.3
  defines **theorem** as "a fact that is always true" right where it first needs it).

## Checklist for a new problem or unit

**The problem**

- [ ] A kid would want to build or win it without being told it is math.
- [ ] The math question comes *out of* playing with it; removing the story would
      remove the question.
- [ ] There is a slow way (by hand, by loop, by picture) that kids can actually
      try before the rule.

**Student notebook**

- [ ] A runnable harness: the boring setup in one cell, with a comment per idea,
      that kids can run without reading all of it (Deep 9's setup cell).
- [ ] A first naive attempt that works, or fails in an interesting way.
- [ ] Prompts that ask for predictions and experiments, in order of difficulty.
- [ ] The question stated in words before any formula.
- [ ] A stub for the kid to finish (`# finish me`) with test cases that show
      where two answers differ (Deep 10's five cases: square and circle disagree
      only on case 4).
- [ ] The theorem, when it comes, with a "test it yourself" cell (`a <= b`
      prints `True` or `False`; `np.isclose` for decimals, as Deep 5 explains).
- [ ] A "*This leads to: ...*" line pointing at where the idea returns.
- [ ] Kid-readable code: plain loops and plain names, as `AGENTS.md` rule 4 asks
      of `vecdraw`. New Python ideas (`def`, `for`, `if`) get one sentence where
      they first appear.

**Teacher guide**

- [ ] Answers for every coin (one table row each) and for "Beyond the coins".
- [ ] A Deep End row: what kids find, *including the usual first wrong idea*,
      and what it leads to.
- [ ] Every number in those answers recomputed in the "Check the key" cell,
      with a reference solution for any stub kids finish.

**Runnable under `make check`**

- [ ] Every student cell runs as committed, stubs included: a stub must execute
      and print something sensible, not raise (`run_notebooks.py` stops on the
      first error, with a 180 s cell timeout).
- [ ] Simulations are deterministic and finish quickly (fixed numbers or a fixed
      seed, a time limit such as `max_time`, a safety limit such as `too_far`).
- [ ] `make strip` before committing; no outputs.

**Choosing the numbers**

- [ ] Tune by simulation so the experiments show something surprising. The chase
      was tuned so that "slower is not always worse": speeds 0.2 and 0.1 miss, but
      0.15 and 0.05 catch. A naive rule should catch a faster NPC (4.8 s), and
      "aim ahead" should fail at the corners.
- [ ] Prepare test cases that separate the ideas (one case inside the square
      but outside the circle).
- [ ] Prefer whole numbers and Pythagorean triples where kids work by hand
      ($(3, 4)$, $(6, 8)$, $(5, 12)$); save messy decimals for the computer.
- [ ] Write down the tuned outcomes in the teacher guide, and check them in
      "Check the key" where it is practical.

## Anti-patterns

- **Theorem first, no need.** A rule stated before any question it answers. If a
  theorem must come early (as in "Beyond the coins"), point forward to the
  problem that will need it.
- **Decorative real world.** A story that can be deleted without changing the
  math ("A wizard wants to know $\lVert (3, 4) \rVert$"). Fine for a bronze coin;
  not for a unit that is meant to drive discovery.
- **Hiding the brute-force stage.** Going straight to the clever reframing. The
  slow way is what makes the reframing feel like relief, and the wrong first
  idea (the rounded rectangle) is worth having.
- **Giving away coin answers in examples.** Worked examples in a part must use
  different numbers from its coins. Answers live only in the teacher guide.
- **Untested trust.** A theorem kids are told but never get to break. Always
  include a case where a nearby rule fails ($L_0$ and scaling; $p = 0.5$ and the
  shortcut rule).
- **A harness kids cannot change.** If every interesting number is buried in a
  function, there is nothing to play with. Put the knobs (`my_speed`,
  `step_time`, `touch_range`) at the top.
- **Dead ends with no exit.** A Deep task with no "This leads to" and no Deep End
  row in the teacher guide.
- **New notation for convenience.** No `\cdot`, no `\times`, no new symbols for
  ideas the course already names. Follow `AGENTS.md` "Style".

## How the course grows

The course itself should grow the way a kid's understanding does.

1. **Notice repeated questions.** When kids' work (or the Deep End table's
   "What kids find") keeps running into the same question, the course has found
   a need. The chase kept asking "when are these two moving things closest?"
2. **Let the slow answer stand for a while.** Keep the brute-force or ad hoc
   version in the material until it has been used in more than one place.
3. **Add the tool or theorem that answers it directly**, in the part or module
   where it fits, and go back and point the earlier tasks at it ("This leads to:
   ..."). Deep 7 points at Module 1, where linear combinations work out exactly
   where everyone ends up.
4. **Record the route in the teacher guide**, so the next teacher knows both the
   shortcut and the long way kids took to want it.

A new module should open with a problem that the previous modules cannot quite
answer, and close with the name and the rule that do.
