# IMPLICIT fixture provenance

This fixture is a B08-owned derivative of the attributed HYBRID fixture in
`../mdfixer-hybrid/`. The small C program keeps the same observable arithmetic,
while the Makefile deliberately uses a GNU Make pattern rule so the case tests
the `IMPLICIT` declaration style independently.

The immutable input identity is the per-file SHA-256 manifest stored in
`../../oracle/mdfixer-implicit.expected.json`. The verification runner checks
that manifest before every experiment; build outputs are excluded.
