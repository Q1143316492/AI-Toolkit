# Python Development Guidelines & AI Assistant Instructions

## AI Assistant Behavior
- **Tool Usage**: Call MCP tools directly without asking permission
- **Comments**: Only add comments for complex logic; clean code needs minimal comments
- **Error Handling**: Implement proper exception handling and input validation

## Environment
- **Python**: Use python3.11+, UTF-8 no-BOM, 160 char limit
- **Structure**: docstring → imports → constants → classes → functions → main
- **Imports**: stdlib → 3rd party → local (space separated, prefer `import module`)

## Naming Conventions (Hungarian Notation)
### Variables & Types
- **Constants**: `MAX_LEVEL = 100`
- **Global**: `g_nCount = 0`, `g_dictPlayers = {}`
- **Private**: `_g_bDebug = False`, `self._m_nData = 0`
- **Local**: `szName = ""` (sz=str, n=int, b=bool, n=float, dt=datetime, fun=function)
- **Objects**: `PlayerObj`, `ItemObj` (Special: `Player`, `Scene` no Obj suffix)

### Functions
- **Public**: `def CreatePlayer(szName, nLevel):`
- **Private**: `def _ValidateInput(self, szInput):`
- **Classes**: `class PlayerCharacter(object):`

## Best Practices

### Comments & Documentation
- **Comment when**: Complex algorithms, business logic, non-obvious decisions
- **Don't comment**: Self-explanatory code
- **Style**: Explain WHY, not WHAT
