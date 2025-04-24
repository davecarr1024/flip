# flip Project Notes

This file tracks architectural decisions, design goals, and future directions for the `flip` project.

---

## 🧠 Philosophy

- **Simulated CPU with discrete components**: `flip` is a microprogrammed computer simulator with real-world inspired timing behavior. It's not just about final outputs — it's about simulating each tick of the clock and observing propagation through logic and memory.
- **Composable, inspectable, and testable**: Each component (`Register`, `Bus`, `Memory`, `Controller`, etc.) is independently testable and logs its behavior clearly at each tick.
- **Instruction-level simulation**: Instructions are defined at a microprogramming level, with per-step control signals. The instruction system allows branching on status flags and multiple addressing modes.

---

## ✅ Completed Features

- ✅ Fully working `Component` system with hierarchical composition and named paths
- ✅ Simulation tick structure with `tick_control`, `tick_write`, `tick_read`, `tick_process`, and `tick_clear`
- ✅ Logging system with indented traversal and human-readable trace output
- ✅ Register, Counter, ProgramCounter, Memory, and Bus components
- ✅ Instruction microprogramming system (`InstructionSet`, `Instruction`, `InstructionMode`, `InstructionImpl`, `Step`)
- ✅ Assembler that converts instruction microcode into addressable control signals
- ✅ Controller that executes instructions using microcode and status flags
- ✅ MinimalComputer architecture with working instructions: `NOP`, `HLT`, `TAX`, `TXA`, `TAY`, `TYA`
- ✅ Test coverage: 100% (including edge cases like open bus reads and missing control/status errors)

---

## 🛠️ In Progress / Planning

### ✨ DSL for Instruction Declaration

Current system is expressive but verbose. Desire for a more fluent, declarative builder pattern like:

```python
InstructionSet()
  .add("lda", 0x25)
    .mode(IMMEDIATE)
      .impl()
        .step("a.write", "bus.read")
Or even YAML/JSON-style static definitions someday.

🧠 Instruction Hierarchy and Naming
Current layers:

InstructionSet

Instruction (by name)

InstructionMode (by addressing mode + opcode)

InstructionImpl (by statuses)

Step (set of control strings)

Good flexibility, future-proofing for:

Branching instructions (e.g. BEQ)

Multiple addressing modes

Conditional microprogram paths

📜 Instruction Fetch & Execution
Header/footer steps defined on the InstructionSet apply to all instructions:

Header: 3 steps to fetch from memory via program_counter and load into instruction_buffer

Footer: resets the controller.step_counter

This guarantees consistent execution state at each instruction boundary.

🧪 Testing Patterns
All core components (Register, Memory, Controller, etc.) have isolated unit tests with full coverage.

Subtests used for multi-case assertion (pytest-subtests)

Controller and Assembler validate instruction decoding and dispatch logic, including detection of unknown controls/statuses

💡 Future Directions
🧱 Core Architecture
Build out more instructions: LDA, STA, ADC, BEQ, etc.

Add branching + relative addressing

Implement a MOV or LDA #value immediate loader

Expand status register modeling (e.g. zero, carry, negative flags)

🧰 Assembly Tooling
Build MinimalAssembler that takes structured program input and converts it into Memory

Define a minimal IR for programs (Program, Instruction, Label, etc.)

Add label resolution, relative/absolute branch handling, and macro support

💡 Visualization / Frontend
Pygame or other UI to show registers and bus updates per tick

Optional signal diagram output

Clock stepping controls (tick/pause/auto)

📌 Other Ideas
 Add notes.md to version control and track architectural decisions

 Break InstructionSet building into fixtures or fluent builders for easier tests

 Auto-generate instruction documentation from InstructionSet

 Consider export to hardware description formats (e.g. for FPGA simulation)

 Instruction-level debugger / trace viewer