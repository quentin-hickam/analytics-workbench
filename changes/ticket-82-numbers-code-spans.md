### Fixed

- `check-draft`'s `numbers` check pairs a code span's backticks across its whole paragraph, as the draft renders it. It used to pair them only within a line and the lines around it, so in hard-wrapped prose a code span closing on an earlier line paired its closing backtick with the next span's opening one, and a number between them, such as `37%` in a line after `` `status =`` wrapped to `` 'active'` ``, was skipped as code.
