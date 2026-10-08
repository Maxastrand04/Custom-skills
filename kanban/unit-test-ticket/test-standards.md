# Test standards

Shared contract. The baseline `unit-test-ticket` tidies tests against. `architect-ticket` reads it so it never writes a structure-sensitive test, and `refactor-ticket` reads it at its true-to-spec pass and module halt.

## Test rules

Applied to the acceptance file and to the module test file of every changed source file. Fix each one unless it says report only.

- **Tautological test.** Passes whatever the code does. Shapes: asserting something always true, like `assert x == x` or `len(items) >= 0`, asserting nothing at all, asserting a value the test set up itself, such as a mock's own return value, and swallowing the exception that should fail it. Delete it.
- **Structure-sensitive test.** Knows how the code is built rather than what it does, so a pure refactor turns it red. Shapes: counting or ordering calls to the project's own modules, mocking one of the project's own modules instead of a boundary such as a database, network, clock or filesystem, reading internal state instead of return values or observable effects, snapshotting an internal data structure, and calling a private function or reading a private field. Mocking a boundary is fine. Delete it, unless it is the only test of a behaviour a caller can see; then rewrite it through the public interface.
- **Too few tests.** A public branch uncovered, or boundary and illegal values untested: null, zero, negative, wrong type. Write the missing test through the public interface, but only where current behaviour is clearly deliberate, such as a documented error or a guard clause. Otherwise report it as undefined behaviour, because pinning an accidental crash turns a bug into a spec.
- **Too many assertions in one test.** Execution stops at the first failure, so the rest never run. Split into one test per assertion, then delete any split test that duplicates one already in the file.
- **Not self-evaluating.** Results checked with conditionals, or by making a human read output. Replace them with assertions.
- **Test writes to standard output.** Remove the output.
- **Bug fixed with no test.** Every fix in the diff should arrive with a test that fails without it. Write it.
- **Design worsened for testability.** Visibility widened or a seam added purely so a test can reach something. Report only, since undoing it is a design decision.

**Break check.** Every test written or rewritten under these rules must be seen red once. Break the line it covers, or for a bug-fix test revert the fix, run the test, watch it fail, then restore the code. A test that stays green is tautological.

Private functions and trivial accessors are never tested directly. The public interface's tests cover them.
