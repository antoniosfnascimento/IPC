# Usability Test Plan (CityFlow MVP)

This document defines the empirical observation grid for lab usability tests or guerrilla testing with real users (or students playing the established personas).

The goal is to measure cognitive effort and interface friction, not the backend math (already validated in QA).

| Test scenario | Frontend task | Expected time (benchmark) | Critical errors (red flags) | Empirical success criterion |
| :--- | :--- | :--- | :--- | :--- |
| **CT-01: Quick initial constraint setup** | "Open the app and set it up to avoid stairs and very irregular pavements." | **< 20 seconds** | 1. User wanders the map screen unable to find the profile icon.<br>2. User is confused by the technical wording of the interface (does not understand *incline* or *surface*). | The user finds the profile menu unprompted, focuses on the base slider, adjusts, presses "Save", and returns to the map visibly relaxed with their choice without asking the moderator. |
| **CT-02: Real-time citizen intervention** | "Imagine you are walking and find a torn-up pavement. Warn other users." | **< 10 seconds** | 1. Temporal frustration — the user spends more than 10 s "looking for" the alert button (not bold enough / does not meet the WCAG touch target).<br>2. Miss-click — the alert gets cancelled. | The user's gaze drops to the bottom primary red button. The finger lands on it first try without needing to zoom in. The user reads the dynamic toast "Obstacle mapped". |
| **CT-03: Quick route understanding (Easy-Read)** | (User gets a phone with high-contrast on and a route already pre-loaded.) "Follow the directions and tell me the next turn." | **< 15 seconds** | 1. Visual overload — the user tries to read every street name around the origin (cognitive load).<br>2. Difficulty distinguishing the geometric polyline from the basemap due to clashing colour contrast (4.5:1 violation). | The user does not hesitate in front of the visual noise; focuses on the isolated top instruction and physically points to the real direction ("I have to turn right here"), mentally engaging the motor process. |

### Session log (HCI investigators)
CT-01, CT-02 and CT-03 must be formally timed. If the P90 (90th percentile of users) exceeds the *Expected time*, the interface must go back to the drawing board (component refactoring).
