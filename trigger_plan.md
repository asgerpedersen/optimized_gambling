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
| auto | pleasure_rating_1 | 191 |
| manual | pleasure_rating_1 | 291 |
| auto | pleasure_rating_2 | 192 |
| manual | pleasure_rating_2 | 292 |
| auto | pleasure_rating_3 | 193 |
| manual | pleasure_rating_3 | 293 |
| auto | pleasure_rating_4 | 194 |
| manual | pleasure_rating_4 | 294 |
| auto | pleasure_rating_5 | 195 |
| manual | pleasure_rating_5 | 295 |
| auto | pleasure_rating_6 | 196 |
| manual | pleasure_rating_6 | 296 |

## A note about code generation
- The first decimal corresponds to condition: auto; 1, manual; 2
- The second decimal corresponds to extraspins; 0, spinstart; 1, partial stop; 2, full stop; 3