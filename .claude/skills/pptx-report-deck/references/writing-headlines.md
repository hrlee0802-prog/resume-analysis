# Writing headlines and picking keywords

Each content slide's headline banner is the one sentence someone reads if
they read nothing else on the slide. Two rules keep a whole deck coherent.

## Stay factual, not interpretive

Describe what the chart or table shows, in the numbers it shows. Don't
editorialize, and don't reach for a conclusion the data doesn't directly
state.

- Good: `"성별은 남성 67명(67%), 여성 33명(33%)이다."`
- Bad: `"남성이 압도적으로 많아 성비 불균형이 우려된다."` (that's an
  opinion about the data, not a description of it)

The one exception is an explicit "insights" or "so what" section, where
the user has asked for interpretation -- even there, ground every claim
in a specific number from the deck rather than a vague generalization.

## Keywords are numbers, not narrative

`set_text_with_keywords` bolds/colors whatever substrings you pass as
`keywords`. Pick the numbers a reader's eye should land on -- usually
the count and percent for the top 1-3 categories in that slide's chart
or table -- not adjectives or connective phrases.

- Good keywords: `"67명(67%)"`, `"84명"`, `"5.4년"`
- Bad keywords: `"가장 많다"`, `"이다"` (not numbers; bolding prose reads
  as shouting, not emphasis)

**The keyword string must appear verbatim in the headline text.**
`split_keywords` does a plain substring search -- if the headline says
`"67명(67%)"` but you pass keyword `"67명 (67%)"` (extra space), it won't
match and that number silently won't get bolded. Write the headline and
its keyword list together, copy-pasting the exact substring, and check
the rendered slide rather than assuming a near-miss will work.

## One headline, one idea

If a chart has more than 2-3 numbers worth citing, put the extra detail
in the table companion slide (see the outline-design guidance in
SKILL.md) rather than cramming a run-on sentence into the headline banner
-- it's one line at ~19pt across the full slide width; more than about
25-30 Korean characters (or ~40-50 Latin characters) starts wrapping
awkwardly depending on the template's banner height.
