### Changed

- A `lower` or `upper` role on a Horizontal bar, Line, Column, or Stacked bar now says that the form draws no intervals and that interval columns need a Bar with intervals, and an unnamed column there says so in case it holds interval bounds. The unnamed-column row names the roles its form takes. `deck-rules.md` states that only Bar with intervals takes interval columns.
- A line chart leaves zero off its axis only when **Axis:** says `non-zero baseline` and gives the reason. `deck-rules.md` and the findings template's **Axis:** placeholder use that wording, and the reference renderer reads it the same way and puts the reason in the source line.

### Fixed

- A chart specification's fields are list items at the depth of its first field, each one paragraph. An item nested under a field, a blank line before it or not, or a later paragraph inside one, is now a `charts` row naming its line that says to join it to the field or move it below the specification, and the fields after it still count instead of becoming slide bullets; a field-named item back at a shallower depth is a slide bullet.
- The reference renderer's bar, column, and line value axes span zero and every value and interval bound, so negative values are no longer cut off below a zero minimum; a negative value in a Stacked bar is refused. `deck-rules.md` states the rule for those forms only, leaving Scatter axes as they were, and says a Stacked bar's parts are zero or more.
- The `check-draft --help` epilog lists the `charts` rows for a file column no **Data:** role names and for text nested in a field.
