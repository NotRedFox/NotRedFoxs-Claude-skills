I'm trying to get a notification on my phone when my washing machine finishes. I want creative approaches. Do not tell me it's impossible or has never been done; if one route is blocked, suggest another.

Real constraints:
- The washing machine is old: no Wi-Fi, no app, no API, no data port.
- I do not want to open the machine or touch mains wiring.
- The alert must reach my main phone, so whatever sits near the washer needs to get a message out over home Wi-Fi.
- A few minutes late is fine. Early alerts are not.

What I have to work with:
- An old Android phone (accelerometer, microphone, camera, Wi-Fi). It can run Termux.
- A Raspberry Pi (model unknown).
- My main phone.
- Home Wi-Fi that probably reaches the washer, and a socket nearby.
- Possibly a small budget for a cheap part, but I would rather use what I have.

Already tried (do not suggest these again):
| Approach | What happened |
|---|---|
| Vendor app or API | None exists for this machine |
| Existing Play Store app using a phone on the washer | None maintained found; only old Windows Phone apps and vendor Wi-Fi adapter apps |
| Old phone on the lid, alert after N minutes of no vibration | On simulated cycles, soak and refill pauses cause false alerts: 30 of 100 early at 6 min, 7 of 100 at 10 min |
| Old phone on the lid, alert after a 1 minute hard spin followed by 6 minutes still | 200 of 200 simulated cycles correct, about 6 minutes late; not yet tried on the real machine |
| Microphone listens for the end beep | Works on simulated audio down to about -5 dB vs room noise; many old machines do not beep |
| Smart meter data from the electricity supplier | Probably 30 minute resolution, too coarse; not checked |
| Plug-in power meter or smart plug | Known to work for others; costs money; not tried |
| Phone camera watching an end light | Not tried; depends on the machine having one |
| Timer from the program length | Not tried; run time varies with load |
| Pi with a vibration switch or USB mic | Planned as a backup; not tried |

What I need from you:
1. Give me 10 approaches I haven't tried. At least 4 should borrow from unrelated fields.
2. For each, give the smallest test that would prove or kill it in under an hour.
3. Rank them by how cheap that test is.
4. Stay legal and within accounts and devices I own.
