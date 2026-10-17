### Changed

- In chat, the agent puts an untested cause, label or recollection as a question, records recollections as the user's, and names codes by meaning. Headline claims retain exceptions and stay within their results.

### Fixed

- Positive sentinel checks exempt ID-like columns only when at least 80% of their non-null values are distinct, so code columns such as RatecodeID can raise placeholder candidates.
