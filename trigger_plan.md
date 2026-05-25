## EEG Trigger codes for Gambling experiment 
| Condition | Event type | Trigger code |
|---|---|---|
| auto | spin_start | 11 |
| manual | spin_start | 21 |
| auto | partial_stop_win | 121 |
| manual | partial_stop_win | 221 |
| auto | partial_stop_near_miss | 122 |
| manual | partial_stop_near_miss | 222 |
| auto | partial_stop_miss | 123 |
| manual | partial_stop_miss | 223 |
| auto | full_stop_win | 131 |
| manual | full_stop_win | 231 |
| auto | full_stop_near_miss | 132 |
| manual | full_stop_near_miss | 232 |
| auto | full_stop_miss | 133 |
| manual | full_stop_miss | 233 |
| auto | accept_extra_spins | 101 |
| manual | accept_extra_spins | 201 |
| auto | decline_extra_spins | 102 |
| manual | decline_extra_spins | 202 |

## A note about code generation
- The first decimal corresponds to condition: auto; 1, manual; 2
- The second decimal corresponds to extraspins; 0, spinstart; 1, partial stop; 2, full stop; 3