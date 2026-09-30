# Storyboard: How Your Body Works

Format: 1920x1080, 30 fps, about 4 minutes. Every scene is drawn in code
(`src/render.py`) so the character and diagrams stay consistent. Line ids
(for example `eyes_3`) refer to `src/script_data.py`; the timed script with
exact start times is generated into `script/timed_script.md`.

## Visual rules

- **Character:** Maya, 11. Medium-brown skin, dark-brown hair in a high
  ponytail, orange T-shirt, teal shorts, white sneakers with a coral stripe.
  Drawn as one reusable puppet (`draw_maya`) so proportions never change.
  Reference sheet: `assets/reference/maya_character_sheet.png`.
- **Ball:** red and yellow beach-style ball.
- **Palette:** soft sky blue, grass green, warm orange accents, navy outlines.
- **Diagram colour key (fixed for the whole video):**
  - Nerve signals: yellow glowing pulses moving along the nerve.
  - Air in: light blue arrows. Air out: grey-lilac arrows.
  - Blood with more oxygen: red. Blood with less oxygen: purple. A small
    legend explains this, because real blood is always a shade of red.
  - Oxygen: blue dots labelled O2. Carbon dioxide: grey dots labelled CO2.
  - Nutrients: yellow dots.
  - Muscle pull: orange arrow along the muscle, pointing toward the bone it
    pulls; curved arrow at the joint for the movement it causes.
- **Labels:** only the terms spoken in that moment, fading in as the word is
  said and fading out when no longer needed.
- **Captions:** burned in at the bottom, two lines maximum, timed from the
  narration's word timestamps.
- No realistic organs, blood, or medical imagery. Organs are simple,
  friendly shapes inside a pale body outline.

## Scenes

| # | Scene | Lines | Visuals |
|---|-------|-------|---------|
| 1 | Intro | `intro_1`–`intro_4` | Title card "How Your Body Works" over a park. Maya stands on the grass; name tag "Maya, 11". A ball arcs in from the right. On "slow it down" the ball freezes with a pause icon and a circular wipe opens into the body. |
| 2 | Eyes, brain, nerves | `eyes_1`–`eyes_6` | Side view of a head outline with a large simple eye. Yellow light rays go from the ball into the eye and land on the retina (label **retina**). Pulses run along the **optic nerve** to the **brain**. Zoom card: a nerve as a cable of fibres (label **neurons**). Then a full-body outline of Maya: pulses travel brain → **spinal cord** → nerves to leg and arm muscles. |
| 3 | Muscles and bones | `mus_1`–`mus_7` | Leg diagram: thigh bone, shin bone, knee joint. Front thigh muscle and back thigh muscle with **tendons**. The active muscle shortens and thickens, pull arrow toward the hip, curved arrow at the knee. Labels **muscle**, **tendon**, **bone**, **joint**. Front muscle straightens the knee, back muscle bends it. Then back in the park: Maya runs (alternating legs) and catches the ball. "Got it!" pop. |
| 4 | Lungs | `lung_1`–`lung_6` | Front upper-body outline. Air path nose/mouth → **windpipe** → **lungs**, which expand and relax with each breath; blue arrows in, lilac arrows out. Zoom circle: a cluster of **alveoli** (air sacs) wrapped by a small blood vessel. Blue O2 dots cross into the blood; grey CO2 dots cross into the air sac and leave on the out-breath. |
| 5 | Heart and blood | `heart_1`–`heart_5` | Loop diagram: heart in the centre, lungs above, leg muscles below. Right side of the heart (on the viewer's left, labelled "right side") sends purple blood up to the lungs; red blood returns to the left side, which sends it down to the muscles; purple blood returns. Dots flow along the vessels in the correct direction. Heart beats; a heart-rate counter rises from about 85 to about 150 beats per minute. Colour legend in the corner. |
| 6 | Digestion | `dig_1`–`dig_5` | Lunch plate (sandwich, apple). Front body outline with mouth, food pipe, **stomach**, **small intestine** (large intestine drawn faintly, unlabeled). A food piece goes in, teeth break it into bits, stomach squeezes (wobble) and bits get smaller (label **enzymes**). In the small intestine yellow **nutrient** dots pass into a red blood vessel and flow away. |
| 7 | Kidneys | `kid_1`–`kid_4` | Back view of the lower body. Two bean-shaped **kidneys** with a red vessel in and a purple vessel out, tubes down to the bladder. Blood dots enter; yellow waste dots and water drops go down as **urine**; cleaned blood leaves. Balance scale "water / salts". Then Maya sweating in the sun; a water-drop gauge shows more water returned to the blood and a smaller urine drop. |
| 8 | Recovery | `rec_1`–`rec_4` | Park. Maya sits on the grass holding the ball, chest rising and falling more slowly over time. Two small charts: heart rate and breathing rate, both curving down gradually (not a sudden drop), reaching a resting level. |
| 9 | Recap and question | `cap_1`–`cap_6` | Six icon cards (eye + brain, muscle + bone, lungs, heart, stomach, kidneys) light up in turn as they are named. Final card: Maya asleep under a starry window with a thought bubble and the question on screen. Held for about six seconds. |
