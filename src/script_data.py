"""Narration for "How Your Body Works".

This file is the single source of truth for the spoken script. The narration
generator, the caption builder, and the scene renderer all read from it, and
visual cues refer to the line ids below.
"""

TITLE = "How Your Body Works"

# Silence (seconds) inserted after each line unless the line overrides it.
DEFAULT_GAP = 0.5
# Extra lead-in and tail silence per scene.
SCENE_LEAD = 0.8
SCENE_TAIL = 1.2

SCENES = [
    {
        "id": "intro",
        "title": "Intro",
        "lead": 4.0,  # title card before the first line
        "lines": [
            ("intro_1", "Have you ever wondered what your body does while you play?"),
            ("intro_2", "Meet Maya. She's eleven, and a ball is flying her way.", 0.9),
            ("intro_3", "Many body parts will work together to catch it."),
            ("intro_4", "Let's slow it down and look inside."),
        ],
    },
    {
        "id": "eyes",
        "title": "Eyes, brain and nerves",
        "lines": [
            ("eyes_1", "It starts with light bouncing off the ball and into Maya's eyes."),
            ("eyes_2", "At the back of the eye, a thin layer called the retina reacts to light."),
            ("eyes_3", "It turns light into electrical signals that travel along the optic nerve to the brain."),
            ("eyes_4", "A nerve is a bundle of long, thin fibers from cells called neurons, which carry messages.", 0.7),
            ("eyes_5", "Her brain processes the signals, so Maya can judge where the ball is going."),
            ("eyes_6", "Then her brain sends signals down the spinal cord and along nerves to her muscles."),
        ],
    },
    {
        "id": "muscles",
        "title": "Muscles and bones",
        "lines": [
            ("mus_1", "Muscles can only pull, never push."),
            ("mus_2", "When a signal reaches a muscle, it contracts, meaning it gets shorter."),
            ("mus_3", "Tough cords called tendons attach muscles to bones. A shortening muscle pulls a bone, moving a joint."),
            ("mus_4", "Muscles on the front of her thigh straighten her knee. Muscles on the back bend it.", 0.7),
            ("mus_5", "They take turns, and Maya runs."),
            ("mus_6", "Arm muscles lift her hands, and her fingers close around the ball."),
            ("mus_7", "Got it!", 1.2),
        ],
    },
    {
        "id": "lungs",
        "title": "Lungs",
        "lines": [
            ("lung_1", "To release energy from food, her working muscle cells need oxygen."),
            ("lung_2", "So Maya breathes faster and deeper."),
            ("lung_3", "Air flows through her nose and mouth, down her windpipe, and into her lungs."),
            ("lung_4", "The lungs hold millions of tiny air sacs called alveoli."),
            ("lung_5", "Their walls are so thin that oxygen passes through into the blood."),
            ("lung_6", "Meanwhile, carbon dioxide, a waste gas from working cells, moves the other way and is breathed out."),
        ],
    },
    {
        "id": "heart",
        "title": "Heart and blood",
        "lines": [
            ("heart_1", "The heart is a fist-sized muscle that pumps blood through tubes called blood vessels."),
            ("heart_2", "The right side pumps blood to the lungs to pick up oxygen."),
            ("heart_3", "The left side pumps that oxygen-rich blood to her body, including her leg muscles."),
            ("heart_4", "Blood also delivers nutrients and carries carbon dioxide away."),
            ("heart_5", "While Maya runs, her heart beats faster, sending more blood to her muscles."),
        ],
    },
    {
        "id": "digestion",
        "title": "Digestion",
        "lines": [
            ("dig_1", "Those nutrients come from Maya's lunch."),
            ("dig_2", "Digestion breaks food into pieces small enough for the body to use."),
            ("dig_3", "Her teeth crush the food."),
            ("dig_4", "Her stomach squeezes and mixes it with acid and enzymes, substances that help break food apart."),
            ("dig_5", "In the small intestine, nutrients such as sugars pass into the blood."),
        ],
    },
    {
        "id": "kidneys",
        "title": "Kidneys",
        "lines": [
            ("kid_1", "Blood also flows through the kidneys, two bean-shaped organs in her lower back."),
            ("kid_2", "They filter the blood, removing waste and extra water, which leave the body as urine."),
            ("kid_3", "They also help balance water and salts in her blood."),
            ("kid_4", "If Maya sweats a lot, her kidneys return more water to the blood, so she makes less urine."),
        ],
    },
    {
        "id": "recovery",
        "title": "Recovery",
        "lines": [
            ("rec_1", "Now Maya sits down to rest."),
            ("rec_2", "Her muscles need less oxygen now, so her breathing and heart rate gradually slow."),
            ("rec_3", "It takes a few minutes. She keeps breathing a little faster to clear extra carbon dioxide and catch up on oxygen."),
            ("rec_4", "Then she's back to her resting pace."),
        ],
    },
    {
        "id": "recap",
        "title": "Recap",
        "lines": [
            ("cap_1", "So, one quick catch took teamwork."),
            ("cap_2", "Her eyes and brain helped her spot the ball, and nerves carried signals."),
            ("cap_3", "Muscles pulled on bones."),
            ("cap_4", "Her lungs took in oxygen, and her heart pumped it around."),
            ("cap_5", "Digestion supplied nutrients, and her kidneys helped keep her blood balanced.", 1.0),
            ("cap_6", "Something to think about: when you're asleep, what happens to your breathing and heartbeat, and why?"),
        ],
        "tail": 6.0,  # hold on the question card
    },
]

def iter_lines():
    for scene in SCENES:
        for entry in scene["lines"]:
            line_id, text = entry[0], entry[1]
            gap = entry[2] if len(entry) > 2 else DEFAULT_GAP
            yield scene, line_id, text, gap


def word_count():
    return sum(len(text.split()) for _, _, text, _ in iter_lines())


if __name__ == "__main__":
    print("words:", word_count())
    for scene in SCENES:
        print(scene["id"], sum(len(e[1].split()) for e in scene["lines"]))
