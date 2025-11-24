# Planner Flow Audit - Comprehensive Review

## Current Flow Issues Identified

### 1. Missing Counts 0/0 Logic
**Problem**: When missing_first=0 and missing_back=0, the system still shows warnings and allows constraint violations.

**Root Cause**: 
- Strict mode fails due to advanced constraints (not missing products)
- System enters best-effort mode even when all slots are filled
- `on_decision=lambda msg: True` allows violations even when user chose "no relaxations"

**Expected Behavior**:
- If missing counts are 0/0, strict mode should succeed OR
- If strict mode fails with 0/0, it's due to advanced constraints, and user should explicitly choose to allow violations

### 2. "Continue Without Relaxations" Button Behavior
**Problem**: User chooses "continue without relaxations" but plan is still generated with violations.

**Root Cause**:
- When `selected_suggestions = []`, we still call `run_planner` with `on_decision=lambda msg: True`
- This allows violations during plan generation
- Config values aren't changed, but violations are allowed

**Expected Behavior**:
- "Continue without relaxations" should mean: retry strict mode with original config
- If strict mode fails, return error (don't generate plan with violations)
- OR: Show explicit warning that plan will have violations and ask for confirmation

### 3. Constraint Violations in Final Plan
**Problem**: Plan shows FAILED constraints even when user didn't approve relaxations.

**Root Cause**:
- `check_advanced_first_constraints` is called with `decide=lambda msg: True` in best-effort mode
- This allows violations to pass through
- Config values remain original, but plan violates them

**Expected Behavior**:
- If user chose "no relaxations", constraints should be enforced
- If constraints can't be satisfied, plan generation should fail
- Validation report should match actual config values

### 4. Dialog Button Mapping
**Current Buttons**:
1. "Hayır, ayarları manuel düzelteceğim" → choice="manual" → abort
2. "Seçili esnetmeleri uygula ve tekrar dene" → choice="retry_strict" → apply relaxations, retry strict
3. "Evet, seçili esnetmelerle best-effort ile devam et" → choice="continue_best" → apply relaxations, best-effort
4. "Devam et (kısıtları görmezden gel, esnetme yapma)" → choice="continue_best", selected=[] → no relaxations, but still allows violations

**Issue**: Button 4 should enforce strict constraints, not allow violations.

## Proposed Fix Strategy

### Phase 1: Fix "Continue Without Relaxations"
- When selected_suggestions=[], use `on_decision=None` (strict mode)
- If strict mode fails, return error (don't proceed with violations)
- Only allow violations when user explicitly chooses "best-effort with relaxations"

### Phase 2: Fix Missing Counts 0/0 Logic
- When 0/0, retry strict mode first
- If strict fails, show clear message that constraints can't be satisfied
- Don't auto-proceed to best-effort

### Phase 3: Ensure Config Consistency
- Track original config throughout
- Never modify config unless relaxations are explicitly applied
- Validation report should use actual config values used in plan generation

### Phase 4: Add Comprehensive Tests
- Test: 0/0 missing counts, strict mode fails → should retry strict, not proceed
- Test: User chooses "no relaxations" → should enforce strict constraints
- Test: User chooses "best-effort with relaxations" → should apply relaxations and allow violations
- Test: Preferred FIRST products should respect day/time






