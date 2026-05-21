# BanCalculatorOW Rules

## Core Model

The calculator treats both teams as:

- Region
- My Team
- Opponent Team

The user should be able to think in user-centered terms instead of Team 1 and Team 2.

## Region Scope

- The calculator should support region selection.
- For now, only `Korea` is enabled.
- Team and map data should be filtered by the selected region.
- The current shared reference is based on `OWCS Korea 2026`.

## Draft Flow

### Series Format

- The calculator should support at least:
  - Best of 5
  - Best of 7
- Regular season should default to `Best of 5`.
- Later playoff-style series can use `Best of 7`.
- The selected format should automatically control how many game slots appear in the interface.

### Game 1

- The user chooses:
  - Region
  - Series format
  - My Team name
  - Opponent Team name
  - Which team has first-ban control
  - Which map is played

### Game 2 and Later

- The user enters the previous game winner.
- The calculator infers the previous game loser.
- The previous game loser gains:
  - map pick authority
  - the choice to first ban or second ban

That means the user should be able to set:

- previous game winner
- current map
- current first-ban team

The app should visually explain that the current first-ban decision belongs to the previous game loser.

## Ban Rules

- Each game has two bans total.
- One ban comes from each team.
- Bans apply to both teams for that game.
- The first ban and second ban must come from different role groups.
- A team cannot repeat its own previous bans in the same match series.
- A team may still ban a hero that was previously banned by the opponent in an earlier game.

## Map Rules

The calculator should only allow maps from the current OWCS map pool.

### Control

- Busan
- Lijiang Tower
- Oasis

### Hybrid

- Blizzard World
- Midtown
- Numbani

### Flashpoint

- Aatlis
- Suravasa

### Push

- Esperanca
- Runasapi

### Escort

- Havana
- Rialto
- Watchpoint: Gibraltar

## UI Requirements

- My Team and Opponent Team should be the top-level identity model.
- Region should be a top-level selector above team selection.
- Series format should be selectable near the top of the screen.
- The current game should show:
  - selected map
  - selected first-ban team
  - selected second-ban team
  - first-ban role group
  - second-ban role group
  - first-ban hero
  - second-ban hero
- The screen should also show:
  - all previous bans by My Team
  - all previous bans by Opponent Team
  - heroes currently unavailable this game
  - a match score tracker
  - clickable per-game result controls

## Match Result Tracking

- The calculator should let the user record game winners inside the current series.
- Each game slot should allow:
  - My Team win
  - Opponent Team win
  - unset
- The visible number of game slots should follow the selected series format.
- Later game authority should be based on the recorded previous game result.

## Recommended App Behavior

- Let the user edit the current game manually.
- Auto-fill the current game's map control and ban-order control from the previous game result.
- Keep manual override available.
- Make the chosen authority easy to understand with plain labels such as:
  - "Previous game loser: Opponent Team"
  - "Opponent Team chooses map"
  - "Opponent Team chooses first ban or second ban"
