#!/usr/bin/env python3
"""Build classroom copies of the Cambridge chapter tests (VCE Physics Units 1&2).

Usage:
    python3 build_tests.py          # every chapter in CHAPTERS
    python3 build_tests.py 2        # only Chapter 2

For each chapter this writes, beside this script:
    ChNN Test (student).pdf     Cambridge's paper as laid out, answer section removed,
                                exact A4, even page count (blank page added if needed)
    ChNN Test (solutions).pdf   our corrected solutions (HTML printed by headless Chrome)
    ChNN Test (solutions).html  the self-contained HTML it was printed from
    ChNN test teacher notes.md  timing, read-outs, Cambridge errors, coverage
    png/                        renders of every page, for checking by eye

To add a chapter: copy a CHAPTERS entry, set the docx path, the text that starts
Cambridge's answer section ("Answers"), answer phrases that must NOT appear in the
student copy, the questions (our solutions) and the notes. Then run and look at the PNGs.

How the student copy is made (lessons from out/booklet/build_booklet.py):
 1. A temp copy of the docx is patched: (a) everything from the page break before
    "Answers" to the end of the body is deleted, so no answer text is ever laid out;
    (b) the header banner is pinned so LibreOffice puts Cambridge's header text below
    the red banner, as Word does. Question content is not touched.
 2. LibreOffice converts it with a private fontconfig ("Times New Roman Bold" mapped to
    Liberation Serif Bold). libreoffice-math must be installed or Word equations vanish.
 3. Trailing empty pages are dropped, every page is scaled to exactly 210 x 297 mm, and
    a blank page is added if the count is odd.

Licensed Cambridge content: output is for the school's shared drive only. Do not commit
the PDFs, HTML, PNGs or this folder's outputs to any git repo.
"""

import base64
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import pdfplumber
from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import RectangleObject

HERE = Path(__file__).resolve().parent
VENDOR = Path("/home/claude/physics/tools/interactives/vendor")
INDEX = Path("/home/claude/physics/data/index")
CHROME = "/usr/bin/google-chrome"
A4_W, A4_H = 595.2756, 841.8898          # exactly 210 x 297 mm in points
MM = 72 / 25.4

FONTS_CONF = """<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig>
  <include ignore_missing="yes">/etc/fonts/fonts.conf</include>
  <match target="pattern">
    <test name="family"><string>Times New Roman Bold</string></test>
    <edit name="family" mode="assign" binding="strong"><string>Liberation Serif</string></edit>
    <edit name="weight" mode="assign" binding="strong"><const>bold</const></edit>
  </match>
</fontconfig>
"""

# =====================================================================================
# Per-chapter data. Our own wording: no em or en dashes, m/s not m s^-1, no division sign.
# Each question: q, marks, sec (section for the marks table), crit (first = main criterion),
# stem (short reminder), ans (final answer), and optionally why (MC reason), steps
# (Values/Formula/Substitute/Solve as LaTeX or text), points (one per mark), note, flag.
# =====================================================================================

CH1_MIRAGE_IMG = "word/media/image5.jpeg"   # Cambridge's own answer diagram for Q15

CHAPTERS = {
    1: {
        "code": "Ch01",
        "title": "Chapter 1 Test: Electromagnetic radiation",
        "docx": "/home/claude/cambridge/TEACHER ONLY/Chapter 1 Test.docx",
        "textbook": "/home/claude/cambridge/Ch01 Textbook chapter.pdf",
        "answers_marker": "Answers",
        "total": 28,
        "n_questions": 17,
        "sections": ["1A", "1B", "1C"],
        # phrases only found in Cambridge's answer section
        "answer_phrases": ["Answers", "Use Snell", "42.86", "= 1.13", "majority is received",
                           "This is an example of a mirage", "violet light (1 mark)",
                           "gamma rays (1 mark)", "An electrical field is a physical field"],
        # text that must still be there (first and last question)
        "must_have": ["Which of the following is an example of a longitudinal wave",
                      "Calculate the refractive index of the liquid", "Total:"],
        "images": {"mirage": CH1_MIRAGE_IMG},
        "questions": [
            {"q": "1", "marks": 1, "sec": "1A", "crit": ["1A.3", "1A.1"], "mc": "A",
             "stem": "Which is a longitudinal wave?", "ans": "A, sound waves",
             "why": "Sound: particles vibrate along the direction the wave travels. Ocean waves and EM waves (radio, gamma) are treated as transverse."},
            {"q": "2", "marks": 1, "sec": "1A", "crit": ["1A.4"], "mc": "D",
             "stem": "Best description of the period.", "ans": "D, time for a wave shape to travel one wavelength",
             "why": "One full wave passes a point in one period. B describes frequency, C describes amplitude."},
            {"q": "3", "marks": 1, "sec": "1A", "crit": ["1A.5"], "mc": "B",
             "stem": "Which quantity does the medium not affect?", "ans": "B, frequency",
             "why": "The source sets the frequency. The medium sets the speed, so the wavelength changes with it."},
            {"q": "4", "marks": 1, "sec": "1B", "crit": ["1B.1"], "mc": "D",
             "stem": "Which statement about all EM waves is false?", "ans": "D, need a medium",
             "why": "EM waves are changing electric and magnetic fields; they travel through a vacuum.",
             "flag": "Option B is also false as printed: EM waves travel at $3.00 \\times 10^{8}$ m/s only in a vacuum (slower in glass or water). Read out before the test: \"In option B, read: in a vacuum.\" With that, D is the only false statement."},
            {"q": "5", "marks": 1, "sec": "1B", "crit": ["1B.3"], "mc": "A",
             "stem": "Visible light has longer wavelengths than ...", "ans": "A, ultraviolet",
             "why": "UV is about 10 to 400 nm, visible about 400 to 700 nm. Microwaves, infrared and radio are all longer than visible."},
            {"q": "6", "marks": 1, "sec": "1B", "crit": ["1B.3"], "mc": "D",
             "stem": "Lowest frequency.", "ans": "D, radio waves",
             "why": "Radio has the longest wavelength, so the lowest frequency."},
            {"q": "7", "marks": 1, "sec": "1C", "crit": ["1C.1"], "mc": "B",
             "stem": "Angle of reflection compared with angle of incidence.", "ans": "B, equal",
             "why": "Law of reflection: both angles are measured from the normal and are equal."},
            {"q": "8", "marks": 1, "sec": "1C", "crit": ["1A.5", "1C.3"], "mc": "B",
             "stem": "Air into water: speed down, frequency fixed, so the wavelength ...", "ans": "B, decreases",
             "why": "$\\lambda = \\frac{v}{f}$: $v$ drops and $f$ stays the same, so $\\lambda$ drops.",
             "note": "The stem writes $c = f\\lambda$. In water the speed is $v$, not $c$. Not worth a read-out; mention when going over the test."},
            {"q": "9", "marks": 1, "sec": "1C", "crit": ["1C.7"], "mc": "C",
             "stem": "Partial internal reflection.", "ans": "C, the ray splits into a reflected ray and a refracted ray",
             "why": "A describes dispersion. B: light does not refract through a mirror. D describes the critical angle, not partial reflection."},
            {"q": "10", "marks": 1, "sec": "1C", "crit": ["1C.12"], "mc": "C",
             "stem": "What lets optical fibres carry light a long way?", "ans": "C, total internal reflection",
             "why": "Light inside the core meets the boundary above the critical angle, so all of it reflects and stays in the fibre."},
            {"q": "11a", "marks": 1, "sec": "1A", "crit": ["1A.6"],
             "stem": "Wavelength from $v = 10$ m/s, $f = 0.20$ Hz.", "ans": "$\\lambda = 50$ m",
             "steps": [("Values", "$v = 10\\ \\text{m/s}$, $f = 0.20\\ \\text{Hz}$"),
                       ("Formula", "$\\lambda = \\dfrac{v}{f}$"),
                       ("Substitute", "$\\lambda = \\dfrac{10}{0.20}$"),
                       ("Solve", "$\\lambda = 50\\ \\text{m}$")],
             "points": ["1 mark: 50 m."]},
            {"q": "11b", "marks": 1, "sec": "1A", "crit": ["1A.6"],
             "stem": "Frequency from $v = 15$ m/s, $\\lambda = 35$ cm.", "ans": "$f = 43$ Hz",
             "steps": [("Values", "$v = 15\\ \\text{m/s}$, $\\lambda = 35\\ \\text{cm} = 0.35\\ \\text{m}$"),
                       ("Formula", "$f = \\dfrac{v}{\\lambda}$"),
                       ("Substitute", "$f = \\dfrac{15}{0.35}$"),
                       ("Solve", "$f = 42.86\\ldots \\approx 43\\ \\text{Hz}$")],
             "points": ["1 mark: 43 Hz (accept 42.9 or 42.86). 0.43 Hz means cm were not changed to m: no mark."],
             "flag": "Cambridge's answer says 42.86 Hz; corrected to 43 Hz because the data have 2 significant figures. Not wrong, just over-precise: accept it."},
            {"q": "11c", "marks": 1, "sec": "1A", "crit": ["1A.6"],
             "stem": "Speed from $f = 3.0 \\times 10^{3}$ Hz, $\\lambda = 1.2$ m.", "ans": "$v = 3.6 \\times 10^{3}$ m/s",
             "steps": [("Values", "$f = 3.0 \\times 10^{3}\\ \\text{Hz}$, $\\lambda = 1.2\\ \\text{m}$"),
                       ("Formula", "$v = f\\lambda$"),
                       ("Substitute", "$v = (3.0 \\times 10^{3})(1.2)$"),
                       ("Solve", "$v = 3.6 \\times 10^{3}\\ \\text{m/s}$")],
             "points": ["1 mark: $3.6 \\times 10^{3}$ m/s (3600 m/s)."],
             "flag": "Cambridge's working says (1.2)(3.0 × 3); corrected because it is a misprint for $3.0 \\times 10^{3}$. Their final answer is right."},
            {"q": "12", "marks": 2, "sec": "1B", "crit": ["1B.1"],
             "stem": "How are the electric and magnetic fields of an EM wave related?",
             "ans": "They vibrate at right angles to each other and to the direction of travel; each changing field makes the other.",
             "points": ["1 mark: the electric and magnetic fields are at right angles (perpendicular) to each other, and both are at right angles to the direction of travel, so the wave is transverse.",
                        "1 mark: a changing electric field makes a changing magnetic field, which makes a changing electric field, and so on, so the wave keeps itself going (no medium needed, speed $c$ in a vacuum)."],
             "flag": "Cambridge's answer defines each field and says a changing magnetic field makes a changing electric field and so on, but never says the fields are at right angles to each other and to the direction of travel; corrected because that is the core of criterion 1B.1 and of the textbook (1B). Under this scheme Cambridge's own answer earns 1 of 2."},
            {"q": "13", "marks": 2, "sec": "1B", "crit": ["1B.2"],
             "stem": "Why is \"all the Sun's energy reaching Earth is UV\" wrong?",
             "ans": "The energy is spread over the spectrum: mostly infrared (about 48%) and visible (about 44%); UV is only about 7%.",
             "points": ["1 mark: the Sun's energy arrives across several regions, mainly infrared and visible light.",
                        "1 mark: UV is only a small share (about 7%), so the statement is wrong."],
             "flag": "Cambridge's answer says the majority arrives as visible light (44%), with the rest infrared and microwaves; corrected because the textbook (1B, text under Figure 1B-4) gives infrared 48%, visible 44%, UV 7%, other about 1%. Infrared is the largest share, no region is a majority, and microwaves are a negligible part. (The figure's own labels give about 49%, 43%, 7%; either set is fine.) Do not take marks off a student who copies the textbook's word \"majority\" for infrared plus visible together."},
            {"q": "14a", "marks": 1, "sec": "1B", "crit": ["1B.3"],
             "stem": "Shortest wavelength.", "ans": "Gamma rays", "points": ["1 mark: gamma rays."]},
            {"q": "14b", "marks": 1, "sec": "1B", "crit": ["1B.3"],
             "stem": "Highest frequency.", "ans": "Gamma rays", "points": ["1 mark: gamma rays."]},
            {"q": "14c", "marks": 1, "sec": "1B", "crit": ["1B.3"],
             "stem": "Lowest energy (photons).", "ans": "Radio waves", "points": ["1 mark: radio waves."],
             "note": "\"Photons\" is not taught in 1B. Lowest energy goes with lowest frequency."},
            {"q": "15", "marks": 3, "sec": "1C", "crit": ["1C.11"],
             "stem": "Explain the \"water on the road\" image of the truck.",
             "ans": "A mirage: refraction in layers of air of different temperature makes an image of the truck below the road.",
             "points": ["1 mark: air near the hot road is hotter than the air above it, so it has a lower refractive index.",
                        "1 mark: light from the truck travelling down into hotter layers bends away from the normal at each layer until it totally internally reflects and travels up to the eye.",
                        "1 mark: the eye traces the ray back in a straight line, so it sees an upside down image of the truck below the road surface, which looks like a reflection in water."],
             "img": "mirage", "img_caption": "Cambridge's answer diagram."},
            {"q": "16a", "marks": 1, "sec": "1C", "crit": ["1C.10", "1C.9"],
             "stem": "Name the process in the prism photo.", "ans": "Dispersion (accept refraction)",
             "points": ["1 mark: dispersion (colour dispersion) or refraction."]},
            {"q": "16b", "marks": 1, "sec": "1C", "crit": ["1C.10"],
             "stem": "Which colour is deviated most?", "ans": "Violet", "points": ["1 mark: violet."]},
            {"q": "16c", "marks": 2, "sec": "1C", "crit": ["1C.10"],
             "stem": "Outline how white light separates into colours.",
             "ans": "Each colour has a different refractive index in glass, so each refracts by a different angle, at both faces.",
             "points": ["1 mark: different colours (wavelengths) travel at different speeds in glass, so the glass has a slightly different refractive index for each colour (violet slowest, largest $n$; red fastest, smallest $n$).",
                        "1 mark: so each colour refracts by a different angle when it enters the prism and again when it leaves, violet bending most, which spreads white light into a spectrum."],
             "flag": "Cambridge's answer says each colour emerges at a slightly different point along the edge; corrected because the cause of the spread is the different angle of refraction for each colour. Different exit points alone would give parallel beams that overlap again (as in a rectangular block). Their wording follows the textbook (1C), so accept it for the first mark."},
            {"q": "17", "marks": 1, "sec": "1C", "crit": ["1C.5", "1C.4"],
             "stem": "Refractive index of the liquid from the ray diagram (60° in air, 50° in the liquid).",
             "ans": "$n_2 = 1.13$",
             "steps": [("Values", "$n_1 = 1.00$, $\\theta_1 = 60^\\circ$, $\\theta_2 = 50^\\circ$"),
                       ("Formula", "$n_1 \\sin\\theta_1 = n_2 \\sin\\theta_2$"),
                       ("Substitute", "$1.00 \\times \\sin 60^\\circ = n_2 \\sin 50^\\circ$"),
                       ("Solve", "$n_2 = \\dfrac{\\sin 60^\\circ}{\\sin 50^\\circ} = \\dfrac{0.866}{0.766} = 1.13$")],
             "points": ["1 mark: 1.13 (no unit)."],
             "note": "The diagram is not to scale: the ray in the liquid is drawn about 38° from the normal but labelled 50°. A student who measures with a protractor gets about 1.4. Students should use the labels."},
        ],
        "notes": {
            "time": "Cambridge gives no time. 28 marks at about 1.5 minutes a mark is about 40 minutes; allow up to 60.",
            "readouts": [
                "Q4, option B: read \"travel at a speed of 3.00 × 10⁸ m/s in a vacuum\". As printed, B is also false, so the question would have two answers.",
            ],
            "optional": [
                "Q14: \"photons with the lowest energy\" means the region with the lowest frequency (photons are not taught until later).",
                "Q17: \"use the angles written on the diagram; it is not drawn to scale.\"",
            ],
            "errors": [
                "**Q13 (wrong).** Cambridge: \"a majority is received as visible light (44%) with the rest made up of infrared and microwaves\". Textbook 1B (text under Figure 1B-4): infrared 48%, visible 44%, UV 7%, other about 1%. So infrared is the largest share, no single region is a majority, and microwaves are negligible. Corrected answer: mostly infrared and visible, UV only about 7%.",
                "**Q12 (incomplete).** Cambridge's answer never says the fields are at right angles to each other and to the direction of travel (textbook 1B: \"always at right angles to each other ... perpendicular to the direction of travel\"). Added as the first marking point.",
                "**Q16c (weak).** Cambridge says each colour leaves \"at a slightly different point along the edge\". The spread comes from each colour refracting by a different angle (different $n$ for each wavelength). Marking points rewritten.",
                "**Q11c (misprint in working).** \"(1.2)(3.0×3)\" should be (1.2)(3.0 × 10³) = 3.6 × 10³ m/s. Final answer right.",
                "**Q11b (precision).** 15 / 0.35 = 42.857 Hz; with 2 significant figure data the answer is 43 Hz. Cambridge's 42.86 Hz is acceptable.",
                "**Q4 (question).** Option B is also false outside a vacuum; read-out above. Cambridge's key (D) is right once that is fixed.",
                "**Q17 (diagram).** Measured from the image: incident ray about 61° from the normal (labelled 60°), ray in the liquid about 38° (labelled 50°). Cambridge's answer 1.13 uses the labels and is right. An index of 1.13 is low for a real liquid (water is 1.33); the drawn angle would give about 1.4.",
                "All other answers (Q1 to Q3, Q5 to Q10, Q11a, Q14, Q15, Q16a, Q16b) checked and correct.",
            ],
            "diagrams": [
                "Q11 wave picture: colour labels (pink, green, blue) go grey but stay readable. The numbers do not come from the picture, so nothing is lost.",
                "Q15 truck photo: prints as a grey photo; fine, the question is in words.",
                "Q16 prism photo: the spectrum loses its colours in black and white. Q16b (violet) is recall, so it still works, but print in colour if you can.",
                "Q17 ray diagram: not to scale (see above). The pink liquid prints as light grey; angle labels stay clear.",
            ],
            "layout": [
                "Questions run pages 1 to 6; the answers (Cambridge pages 7 and 8) are removed. 6 pages = 3 sheets double-sided.",
                "Working space is Cambridge's own ruled lines: Q12 and Q13 have 4 lines each; Q11a, b, c, Q14a, b, c, Q16a, b and the 2-mark Q16c have one line each; Q17 has 3. Q16c is tight.",
            ],
            "other": [
                "`Chapter 1 Suggested responses.docx` does not answer the test (it answers check-ins, section and review questions).",
                "The lesson index (`data/index/ch01/ch01.json`, field `test`) records the test as 16 questions; it has 17 (Q1 to Q17). Not changed here.",
            ],
        },
    },
    2: {
        "code": "Ch02",
        "title": "Chapter 2 Test: Thermal energy and electromagnetic radiation",
        "docx": "/home/claude/cambridge2/TEACHER ONLY/Chapter 2 Test.docx",
        "textbook": "/home/claude/cambridge2/Ch02 Textbook chapter.pdf",
        "answers_marker": "Answers",
        "total": 22,
        "n_questions": 13,
        "sections": ["2A", "2B"],
        "answer_phrases": ["Answers", "835 000", "1047", "5650", "7.77", "A land mass with",
                           "Therefore, using Wien", "Q = mL"],
        "must_have": ["Which of the following temperatures are within",
                      "what would the peak radiated wavelength be", "Total:"],
        "images": {},
        "questions": [
            {"q": "1", "marks": 1, "sec": "2A", "crit": ["2A.3"], "mc": "D",
             "stem": "Which pair of temperatures is within 1°C?", "ans": "D, −23°C and 250 K",
             "why": "$-23 + 273 = 250$ K. A uses a negative kelvin temperature (impossible); B and C are 100 degrees apart."},
            {"q": "2", "marks": 1, "sec": "2A", "crit": ["2A.1"], "mc": "A",
             "stem": "The thermal energy of a zinc block equals ...", "ans": "A, sum of the random potential and kinetic energies of its molecules",
             "why": "This is the textbook definition (2A). D (random translational kinetic energy only) is what temperature measures."},
            {"q": "3", "marks": 1, "sec": "2A", "crit": ["2A.4"], "mc": "C",
             "stem": "Why does wood feel warmer than copper at the same temperature?", "ans": "C, wood is a poor conductor",
             "why": "Copper conducts thermal energy away from your hand quickly, so it feels colder; wood conducts it away slowly. Both are at room temperature, so D is wrong; copper's specific heat capacity is lower than wood's, so A is wrong."},
            {"q": "4", "marks": 1, "sec": "2B", "crit": ["2B.1", "2A.4"], "mc": "B",
             "stem": "Which statement about EM radiation is false?", "ans": "B, only emitted by blackbodies",
             "why": "Every object above 0 K emits EM radiation; a blackbody is just a perfect emitter and absorber."},
            {"q": "5", "marks": 1, "sec": "2A", "crit": ["2A.4"], "mc": "D",
             "stem": "Heat transfer in fluids is ...", "ans": "D, possible by convection, conduction and radiation",
             "why": "Fluids conduct (poorly), convect, and emit and absorb radiation."},
            {"q": "6", "marks": 1, "sec": "2A", "crit": ["2A.6"], "mc": "D",
             "stem": "Which have the same value?", "ans": "D, specific latent heats of melting and fusion",
             "why": "Melting and fusion are two names for the same change of state, so they have one value.",
             "flag": "Options A and C are printed the same (\"vaporisation and fusion\"). A misprint; it does not change the answer. If one was meant to read \"vaporisation and condensation\", that would also be correct (textbook 2A says those values are the same), so do not fix it by guessing. Read-out below."},
            {"q": "7", "marks": 1, "sec": "2A", "crit": ["2A.9", "2A.8"], "mc": "A",
             "stem": "500 W heater, 1.0 kg water, 20°C to boiling: time?", "ans": "A, 11 minutes",
             "why": "Energy to heat the water, then time from power:",
             "steps": [("Values", "$m = 1.0\\ \\text{kg}$, $c = 4190\\ \\text{J/(kg K)}$, $\\Delta T = 100 - 20 = 80\\ \\text{K}$, $P = 500\\ \\text{W}$"),
                       ("Formula", "$Q = mc\\Delta T$, then $t = \\dfrac{Q}{P}$"),
                       ("Substitute", "$Q = 1.0 \\times 4190 \\times 80 = 3.35 \\times 10^{5}\\ \\text{J}$, $\\;t = \\dfrac{3.35 \\times 10^{5}}{500}$"),
                       ("Solve", "$t = 670\\ \\text{s} = 11.2\\ \\text{min}$, closest to A")]},
            {"q": "8", "marks": 1, "sec": "2B", "crit": ["2B.1"], "mc": "D",
             "stem": "What is necessary for a blackbody?", "ans": "D, emits and absorbs all radiation perfectly",
             "why": "Textbook 2B: a blackbody emits with maximum efficiency and absorbs all frequencies that fall on it.",
             "flag": "The textbook's margin definition (2B) is \"a theoretical object that perfectly absorbs all radiation falling on it\", which means the same as option C. A student who learnt the glossary can defend C. Decide before marking whether to accept C as well (suggested: yes)."},
            {"q": "9", "marks": 1, "sec": "2B", "crit": ["2B.4"], "mc": "B",
             "stem": "How do greenhouse gases contribute to global warming?", "ans": "B, absorb infrared and re-radiate some back to Earth",
             "why": "Earth's surface radiates infrared; greenhouse gases absorb it and send some back down."},
            {"q": "10", "marks": 1, "sec": "2B", "crit": ["2B.2"], "mc": "C",
             "stem": "Wien's law shows that ...", "ans": "C, peak wavelength increases as temperature decreases",
             "why": "$\\lambda_{max} = \\dfrac{b}{T}$, so a lower temperature gives a longer peak wavelength."},
            {"q": "11a", "marks": 2, "sec": "2A", "crit": ["2A.10", "2A.8"],
             "stem": "Energy to melt 2.5 kg of ice at 273 K ($L = 334$ kJ/kg).", "ans": "$Q = 8.35 \\times 10^{5}$ J (835 kJ)",
             "steps": [("Values", "$m = 2.5\\ \\text{kg}$, $L_{fusion} = 334\\ \\text{kJ/kg} = 3.34 \\times 10^{5}\\ \\text{J/kg}$"),
                       ("Formula", "$Q = mL$"),
                       ("Substitute", "$Q = 2.5 \\times 3.34 \\times 10^{5}$"),
                       ("Solve", "$Q = 8.35 \\times 10^{5}\\ \\text{J} = 835\\ \\text{kJ}$")],
             "points": ["1 mark: $Q = mL$ with the right values substituted.",
                        "1 mark: $8.35 \\times 10^{5}$ J or 835 kJ, with unit (accept $8.4 \\times 10^{5}$ J)."]},
            {"q": "11b", "marks": 2, "sec": "2A", "crit": ["2A.9", "2A.8"],
             "stem": "Energy to heat the water from 273 K to 373 K ($c = 4190$ J/(kg K)).", "ans": "$Q = 1.05 \\times 10^{6}$ J (1048 kJ)",
             "steps": [("Values", "$m = 2.5\\ \\text{kg}$, $c = 4190\\ \\text{J/(kg K)}$, $\\Delta T = 373 - 273 = 100\\ \\text{K}$"),
                       ("Formula", "$Q = mc\\Delta T$"),
                       ("Substitute", "$Q = 2.5 \\times 4190 \\times 100$"),
                       ("Solve", "$Q = 1.0475 \\times 10^{6}\\ \\text{J} \\approx 1.05 \\times 10^{6}\\ \\text{J}$ (1048 kJ)")],
             "points": ["1 mark: $Q = mc\\Delta T$ with $\\Delta T = 100$ K.",
                        "1 mark: $1.05 \\times 10^{6}$ J (accept 1047 kJ, 1048 kJ or $1.0 \\times 10^{6}$ J), with unit."],
             "flag": "Cambridge's answer says 1 047 500 J = 1047 kJ; corrected to 1048 kJ because 1047.5 rounds up. A slip, not a physics error: accept either."},
            {"q": "11c", "marks": 2, "sec": "2A", "crit": ["2A.10", "2A.6"],
             "stem": "Energy to turn the water at 373 K into steam ($L = 2260$ kJ/kg).", "ans": "$Q = 5.65 \\times 10^{6}$ J (5650 kJ)",
             "steps": [("Values", "$m = 2.5\\ \\text{kg}$, $L = 2260\\ \\text{kJ/kg} = 2.26 \\times 10^{6}\\ \\text{J/kg}$"),
                       ("Formula", "$Q = mL$"),
                       ("Substitute", "$Q = 2.5 \\times 2.26 \\times 10^{6}$"),
                       ("Solve", "$Q = 5.65 \\times 10^{6}\\ \\text{J} = 5650\\ \\text{kJ}$")],
             "points": ["1 mark: $Q = mL$ with the latent heat of vaporisation (condensation).",
                        "1 mark: $5.65 \\times 10^{6}$ J or 5650 kJ, with unit."],
             "note": "The question gives the latent heat \"of condensation\" for vaporising. That is correct: textbook 2A says the two values are the same. Cambridge's working line \"= 5 650 000\" has no unit; their final 5650 kJ is right."},
            {"q": "12", "marks": 3, "sec": "2A", "crit": ["2A.4"],
             "stem": "Explain how natural convection gives sea breezes on sunny days.",
             "ans": "Land heats more than the sea; warm air over the land rises; cooler, denser air from over the sea moves in along the surface.",
             "points": ["1 mark: land has a lower specific heat capacity than water, so in the Sun it warms more than the sea, and so does the air above it.",
                        "1 mark: the warm air over the land expands, becomes less dense and rises.",
                        "1 mark: cooler, denser air from over the sea flows in along the surface to replace it (the sea breeze); air sinks over the sea to complete the convection current."],
             "note": "Cambridge's answer is correct. Its sentence \"which in turn pulls in air from above the land\" is muddled (that air returns high up, not at the surface); do not copy it to students."},
            {"q": "13", "marks": 3, "sec": "2B", "crit": ["2B.2", "2A.3"],
             "stem": "Peak wavelength of a blackbody at 100°C ($b = 2.90 \\times 10^{-3}$ m K).", "ans": "$\\lambda_{max} = 7.77 \\times 10^{-6}$ m (infrared)",
             "steps": [("Values", "$T = 100 + 273 = 373\\ \\text{K}$, $b = 2.90 \\times 10^{-3}\\ \\text{m K}$"),
                       ("Formula", "$\\lambda_{max} = \\dfrac{b}{T}$"),
                       ("Substitute", "$\\lambda_{max} = \\dfrac{2.90 \\times 10^{-3}}{373}$"),
                       ("Solve", "$\\lambda_{max} = 7.77 \\times 10^{-6}\\ \\text{m}$ (7.77 µm)")],
             "points": ["1 mark: 100°C converted to 373 K.",
                        "1 mark: $\\lambda_{max} = \\dfrac{b}{T}$ with the values substituted.",
                        "1 mark: $7.77 \\times 10^{-6}$ m, with unit."],
             "note": "Using 100 instead of 373 gives $2.90 \\times 10^{-5}$ m: at most 1 mark. Using 373.15 K gives the same answer to 3 significant figures. Cambridge's working writes 2.9 for the given 2.90; same answer."},
        ],
        "notes": {
            "time": "Cambridge gives no time. 22 marks at about 1.5 minutes a mark is about 30 to 35 minutes, well under the 60 minutes planned.",
            "readouts": [
                "Q6: \"Options A and C are printed the same. That is a printing error; there is still one correct answer.\"",
            ],
            "optional": [
                "Q13 and Q11: \"Use the back page if you need more room\" (Cambridge gives one or two lines for each part; see layout).",
            ],
            "errors": [
                "No answer in the Chapter 2 key is wrong. Every question worked; details below.",
                "**Q11b (rounding slip).** Cambridge: 1 047 500 J = 1047 kJ. 1047.5 kJ rounds to 1048 kJ. Accept either.",
                "**Q11c (missing unit).** Working line \"= 5 650 000\" has no unit; final 5650 kJ is right.",
                "**Q6 (question misprint).** Options A and C are identical. The key (D) is right as printed.",
                "**Q8 (ambiguous key).** Key D (emits and absorbs perfectly). The textbook's margin definition of a blackbody is \"perfectly absorbs all radiation falling on it\", which is option C. Suggest accepting C too.",
                "**Q12 (muddled sentence).** Correct overall; the line \"which in turn pulls in air from above the land\" could mislead (the return flow is high up).",
                "**No marking guide.** Cambridge gives marks per part (2, 2, 2, 3, 3) but no marking points. Marking points in the solutions copy are ours.",
                "Checked and correct: Q1 (−23 + 273 = 250), Q2 to Q5, Q7 (1.0 × 4190 × 80 = 335 200 J; 335 200 / 500 = 670 s = 11.2 min), Q9, Q10, Q11a (2.5 × 334 000 = 835 000 J), Q11c (2.5 × 2 260 000 = 5 650 000 J), Q13 (2.90 × 10⁻³ / 373 = 7.77 × 10⁻⁶ m).",
            ],
            "diagrams": [
                "The test has no diagrams. The only picture is Cambridge's header banner.",
            ],
            "layout": [
                "Questions run pages 1 to 3; the answers (Cambridge pages 4 and 5) are removed; page 4 is a blank added so the paper prints double-sided on 2 sheets.",
                "Q6 starts at the bottom of page 1 (stem and option A) and finishes on page 2. That is how the file lays out in LibreOffice; Word also counts 5 pages, so it is likely the same in Word.",
                "Working space is tight: two ruled lines for each 2-mark part of Q11 and for the 3-mark Q12, and one line for the 3-mark Q13. Students will need the blank back page (page 4) for working.",
            ],
            "other": [
                "`Chapter 2 Suggested responses.pdf` does not answer the test (it answers check-ins, section and review questions).",
                "The textbook gives Wien's constant as 2.898 × 10⁻³ m K in the formula box but 2.90 × 10⁻³ m K in the checklist; the test gives 2.90 × 10⁻³, so no conflict here.",
                "The textbook table uses 273.15 K; its worked examples and this test use 273. Both give the same answers here.",
            ],
        },
    },
}

# =====================================================================================
# Student copy
# =====================================================================================


def log(msg):
    print(msg, flush=True)


def fix_header(xml, header_dist_twips):
    """Pin Cambridge's header banner so LibreOffice puts the header text under it
    (copied from out/booklet/build_booklet.py)."""
    m = re.search(r'<wp:anchor\b.*?</wp:anchor>', xml, re.S)
    if not m:
        return xml, "no anchored picture in header"
    anchor = m.group(0)
    if "wrapSquare" not in anchor and "wrapTopAndBottom" not in anchor:
        return xml, "header picture does not wrap text"
    pv = re.search(r'<wp:positionV relativeFrom="paragraph">\s*<wp:posOffset>(-?\d+)</wp:posOffset>', anchor)
    ext = re.search(r'<wp:extent cx="\d+" cy="(\d+)"', anchor)
    if not pv or not ext:
        return xml, "header picture not positioned from paragraph"
    off, cy = int(pv.group(1)), int(ext.group(1))
    top_emu = header_dist_twips * 635 + off
    clear_twips = round((top_emu + cy) / 635) - header_dist_twips
    if clear_twips <= 0:
        return xml, "picture does not reach the header text"
    xml = xml.replace(anchor, anchor.replace(
        pv.group(0), f'<wp:positionV relativeFrom="page"><wp:posOffset>{top_emu}</wp:posOffset>'))
    paras = list(re.finditer(r'<w:p\b[^>]*>.*?</w:p>', xml, re.S))
    ia = next(i for i, p in enumerate(paras) if "<wp:anchor" in p.group(0))
    if ia + 1 >= len(paras):
        return xml, "no header text after the picture"
    nxt = paras[ia + 1]
    clear_twips -= 276
    ptxt = nxt.group(0)
    if "<w:spacing" in ptxt:
        return xml, "header text paragraph already has spacing; left as is"
    if "<w:pPr>" in ptxt:
        ptxt2 = ptxt.replace("<w:pPr>", f'<w:pPr><w:spacing w:before="{clear_twips}"/>', 1)
    else:
        ptxt2 = re.sub(r'(<w:p\b[^>]*>)', rf'\1<w:pPr><w:spacing w:before="{clear_twips}"/></w:pPr>', ptxt, 1)
    xml = xml[:nxt.start()] + ptxt2 + xml[nxt.end():]
    return xml, f"header text moved below banner ({clear_twips} twips)"


def para_text(p):
    return re.sub(r'<[^>]+>', '', p)


def cut_answers(doc, marker):
    """Delete the body from the answer heading (and the page break paragraph(s) just
    before it) up to the final sectPr. Returns (new_xml, removed_text)."""
    body_end = doc.rfind("<w:sectPr")
    # top-level children of w:body: paragraphs and tables
    bstart = doc.find("<w:body>") + len("<w:body>")
    items, i = [], bstart
    pat = re.compile(r'<w:(p|tbl)\b[^>]*?(?:/>|>)')
    while i < body_end:
        m = pat.search(doc, i, body_end)
        if not m:
            break
        tag = m.group(1)
        if m.group(0).endswith("/>"):
            end = m.end()
        else:
            depth, j = 0, m.start()
            op = re.compile(rf'<w:{tag}\b[^>]*?(/?)>|</w:{tag}>')
            while True:
                n = op.search(doc, j)
                if n.group(0).startswith("</"):
                    depth -= 1
                elif not n.group(1):
                    depth += 1
                j = n.end()
                if depth == 0:
                    break
            end = j
        items.append((m.start(), end))
        i = end
    hits = [k for k, (s, e) in enumerate(items) if para_text(doc[s:e]).strip() == marker]
    if len(hits) != 1:
        sys.exit(f"expected one '{marker}' heading, found {len(hits)}")
    k = hits[0]
    # walk back over empty paragraphs that only carry the page break
    while k > 0 and not para_text(doc[items[k - 1][0]:items[k - 1][1]]).strip() \
            and ('w:type="page"' in doc[items[k - 1][0]:items[k - 1][1]]):
        k -= 1
    cut_from = items[k][0]
    removed = para_text(doc[cut_from:body_end])
    return doc[:cut_from] + doc[body_end:], removed


SYMBOL_FONT = {0x6C: "\u03bb", 0xB4: "\u00d7", 0xB0: "\u00b0", 0x71: "\u03b8", 0x44: "\u0394", 0x6D: "\u03bc",
               0x61: "\u03b1", 0x62: "\u03b2", 0x67: "\u03b3", 0x70: "\u03c0", 0x57: "\u03a9", 0xB1: "\u00b1",
               0xBB: "\u2248", 0x2D: "\u2212"}


def fix_math_syms(doc):
    """LibreOffice drops a Symbol-font character (w:sym) inside a Word equation run
    (m:r): Cambridge's "v = f lambda" lost its lambda. Swap each for the same character
    as plain math text. Returns (new_xml, count)."""
    count = 0

    def one(m):
        nonlocal count
        run = m.group(0)
        def sym(n):
            nonlocal count
            code = int(n.group(1), 16) & 0xFF
            if code not in SYMBOL_FONT:
                sys.exit(f"unknown Symbol character {n.group(1)} in an equation")
            count += 1
            return f"<m:t>{SYMBOL_FONT[code]}</m:t>"
        return re.sub(r'<w:sym w:font="Symbol" w:char="([0-9A-Fa-f]{4})"/>', sym, run)
    doc = re.sub(r'<m:r>(?:(?!</m:r>).)*?</m:r>', one, doc, flags=re.S)
    return doc, count


def prepare_docx(src, dst, marker):
    zin = zipfile.ZipFile(src)
    doc = zin.read("word/document.xml").decode("utf8")
    hd = re.search(r'<w:pgMar[^>]*w:header="(\d+)"', doc)
    header_dist = int(hd.group(1)) if hd else 708
    doc, removed = cut_answers(doc, marker)
    doc, nsym = fix_math_syms(doc)
    notes = [f"{nsym} Symbol characters in equations made plain"]
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for it in zin.infolist():
            data = zin.read(it.filename)
            if it.filename == "word/document.xml":
                data = doc.encode("utf8")
            elif re.fullmatch(r"word/header\d*\.xml", it.filename):
                new, note = fix_header(data.decode("utf8"), header_dist)
                notes.append(f"{it.filename}: {note}")
                data = new.encode("utf8")
            zout.writestr(it, data)
    return removed, notes


def convert(docx, outdir, tmp):
    env = dict(os.environ, FONTCONFIG_FILE=str(tmp / "fonts.conf"))
    subprocess.run(["soffice", f"-env:UserInstallation=file://{tmp}/lo_profile", "--headless",
                    "--convert-to", "pdf", "--outdir", str(outdir), str(docx)],
                   env=env, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    pdf = outdir / (Path(docx).stem + ".pdf")
    if not pdf.exists():
        sys.exit(f"LibreOffice did not produce {pdf}")
    return pdf


def to_exact_a4(page):
    w, h = float(page.mediabox.width), float(page.mediabox.height)
    if abs(w - A4_W) > 0.001 or abs(h - A4_H) > 0.001:
        if abs(w - A4_W) > 3 or abs(h - A4_H) > 3:
            sys.exit(f"Page is not A4: {w} x {h} pt")
        page.add_transformation(Transformation().scale(A4_W / w, A4_H / h))
    box = RectangleObject([0, 0, A4_W, A4_H])
    for name in ("mediabox", "cropbox", "trimbox", "bleedbox", "artbox"):
        setattr(page, name, box)
    return page


def page_is_empty(pdf_path, pageno, header_bottom=90, footer_top=790):
    with pdfplumber.open(pdf_path) as pdf:
        p = pdf.pages[pageno]
        words = [w for w in p.extract_words() if header_bottom < w["top"] < footer_top]
        pics = [im for im in p.images if im["bottom"] > header_bottom and im["top"] < footer_top]
        rects = [r for r in p.rects + p.lines if r["top"] > header_bottom and r["bottom"] < footer_top]
        return not words and not pics and not rects


def build_student(ch, tmp, problems):
    build = tmp / ch["code"]
    build.mkdir()
    dst = build / f"{ch['code']} Test.docx"
    removed, notes = prepare_docx(ch["docx"], dst, ch["answers_marker"])
    log(f"  removed answer section: {len(removed)} characters, starts '{removed.strip()[:40]}'")
    log("  " + "; ".join(notes))
    pdf = convert(dst, build, tmp)
    n = len(PdfReader(pdf).pages)
    keep = list(range(n))
    while len(keep) > 1 and page_is_empty(pdf, keep[-1]):
        log(f"  dropped empty trailing page {keep.pop() + 1}")
    writer = PdfWriter()
    for k in keep:
        writer.add_page(to_exact_a4(PdfReader(pdf).pages[k]))
    added_blank = False
    if len(writer.pages) % 2:
        writer.add_blank_page(width=A4_W, height=A4_H)
        added_blank = True
    writer.add_metadata({"/Title": f"{ch['title']} (student)"})
    out = HERE / f"{ch['code']} Test (student).pdf"
    with open(out, "wb") as f:
        writer.write(f)
    # checks
    r = PdfReader(out)
    for i, p in enumerate(r.pages, 1):
        w, h = float(p.mediabox.width), float(p.mediabox.height)
        if abs(w / MM - 210) > 0.005 or abs(h / MM - 297) > 0.005:
            problems.append(f"{out.name} page {i} is {w / MM:.3f} x {h / MM:.3f} mm")
    if len(r.pages) % 2:
        problems.append(f"{out.name}: odd page count")
    with pdfplumber.open(out) as p:
        text = "\n".join((pg.extract_text() or "") for pg in p.pages)
    for phrase in ch["answer_phrases"]:
        if phrase in text:
            problems.append(f"{out.name}: answer phrase still present: {phrase!r}")
    flat = re.sub(r"\s+", " ", text)
    for phrase in ch["must_have"]:
        if phrase not in flat:
            problems.append(f"{out.name}: expected text missing: {phrase!r}")
    return out, len(keep), added_blank, text


# =====================================================================================
# Solutions copy
# =====================================================================================

def b64file(path):
    return base64.b64encode(Path(path).read_bytes()).decode()


def fonts_css():
    out = []
    for fam, w, f in [("Inter", 400, "inter-latin-400-normal.woff2"), ("Inter", 600, "inter-latin-600-normal.woff2"),
                      ("Inter", 700, "inter-latin-700-normal.woff2"),
                      ("Space Grotesk", 700, "space-grotesk-latin-700-normal.woff2")]:
        out.append(f"@font-face{{font-family:'{fam}';font-weight:{w};src:url(data:font/woff2;base64,{b64file(VENDOR / f)}) format('woff2')}}")
    kcss = (VENDOR / "katex.min.css").read_text()
    kcss = re.sub(r'@font-face\{[^}]*\}', '', kcss)
    for f in sorted(os.listdir(VENDOR)):
        if f.startswith("KaTeX_"):
            fam = f[:-6].rsplit("-", 1)[0]
            out.append(f"@font-face{{font-family:'{fam}';font-style:{'italic' if 'Italic' in f else 'normal'};"
                       f"font-weight:{'bold' if 'Bold' in f else 'normal'};src:url(data:font/woff2;base64,{b64file(VENDOR / f)}) format('woff2')}}")
    return "".join(out) + kcss


def katex_render(chunks):
    """Render every $...$ in a list of strings with KaTeX in node (throwOnError)."""
    maths = sorted({m for s in chunks for m in re.findall(r'\$([^$]+)\$', s)})
    if not maths:
        return {}
    js = ("const k=require(process.argv[1]);const m=JSON.parse(require('fs').readFileSync(0,'utf8'));"
          "process.stdout.write(JSON.stringify(m.map(x=>k.renderToString(x,{throwOnError:true}))))")
    r = subprocess.run(["node", "-e", js, str(VENDOR / "katex.min.js")], input=json.dumps(maths),
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit("KaTeX failed:\n" + r.stderr[-2000:])
    return dict(zip(maths, json.loads(r.stdout)))


def rich(s, K):
    """Escape our text and swap $...$ for pre-rendered KaTeX."""
    parts = re.split(r'(\$[^$]+\$)', s)
    return "".join(K[p[1:-1]] if p.startswith("$") and p.endswith("$") and len(p) > 2 else html.escape(p)
                   for p in parts)


def our_strings(ch):
    out = [ch["title"]]
    for q in ch["questions"]:
        for key in ("stem", "ans", "why", "note", "flag", "img_caption"):
            if q.get(key):
                out.append(q[key])
        for _, v in q.get("steps", []):
            out.append(v)
        out += q.get("points", [])
    for v in ch["notes"].values():
        out += v if isinstance(v, list) else [v]
    return out


def load_criteria(ch):
    d = json.loads((INDEX / f"ch{int(ch['code'][2:]):02d}" / f"ch{int(ch['code'][2:]):02d}.json").read_text())
    return [(c["code"] if "code" in c else c["id"], c["text"]) for c in d["criteria"]]


def coverage(ch):
    crit = load_criteria(ch)
    main, also = {}, {}
    for q in ch["questions"]:
        main.setdefault(q["crit"][0], []).append(q)
        for c in q["crit"][1:]:
            also.setdefault(c, []).append(q)
    rows = []
    for code, text in crit:
        qs = main.get(code, [])
        rows.append({"code": code, "text": text, "qs": [q["q"] for q in qs],
                     "marks": sum(q["marks"] for q in qs), "also": [q["q"] for q in also.get(code, [])]})
    per_sec = {s: sum(q["marks"] for q in ch["questions"] if q["sec"] == s) for s in ch["sections"]}
    return rows, per_sec


CSS = """
@page{size:210mm 297mm;margin:14mm 15mm 14mm 15mm}
*{box-sizing:border-box}
body{margin:0;font-family:'Inter',sans-serif;font-size:9.6pt;line-height:1.4;color:#14213d}
h1{font-family:'Space Grotesk',sans-serif;font-size:17pt;margin:0 0 1mm;color:#0b2545}
.sub{color:#555;margin-bottom:4mm;font-size:9pt}
h2{font-family:'Space Grotesk',sans-serif;font-size:12pt;margin:5mm 0 2mm;padding-bottom:1mm;border-bottom:1.5px solid #0b2545;color:#0b2545}
table{border-collapse:collapse;width:100%}
.mc td,.mc th,.cov td,.cov th{border:1px solid #c9d2e0;padding:1.2mm 2mm;vertical-align:top;text-align:left}
.mc th,.cov th{background:#eef2f8;font-weight:600}
.mc>tbody>tr>td:first-child{font-weight:700;width:9mm}
.mc>tbody>tr>td:nth-child(2){font-weight:700;width:8mm;text-align:center}
.mc tr{break-inside:avoid}
.mc .steps td{border:none;padding:0.4mm 3mm 0.4mm 0;background:none}
.q{border-left:3px solid #2b6cb0;padding:1.5mm 0 1.5mm 3mm;margin:0 0 3.5mm;break-inside:avoid}
.qh{display:flex;gap:3mm;align-items:baseline;margin-bottom:1mm}
.qn{font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:11pt}
.mk{font-size:8.5pt;color:#555}
.cr{font-size:8.5pt;color:#2b6cb0;margin-left:auto}
.stem{color:#555;font-style:italic;margin-bottom:1mm}
.ans{font-weight:700;margin:1mm 0}
.steps{width:auto;margin:1mm 0 1mm 0}
.steps td{padding:0.6mm 3mm 0.6mm 0;vertical-align:middle}
.steps td:first-child{font-weight:600;color:#555;width:22mm}
ul.pts{margin:1mm 0 0;padding-left:5mm}
ul.pts li{margin:0.5mm 0}
.flag{border:1.2px solid #b7791f;background:#fff8e6;border-radius:2mm;padding:1.5mm 2.5mm;margin-top:1.5mm;font-size:9pt}
.flag b{color:#8a5a00}
.note{font-size:9pt;color:#444;margin-top:1mm}
.fig{margin-top:1.5mm}
.fig img{width:85mm}
.fig .cap{font-size:8pt;color:#666}
.cov td.z{color:#b00020;font-weight:600}
.cov{font-size:8.8pt}.cov td,.cov th{padding:0.8mm 2mm}
.foot{margin-top:6mm;font-size:8pt;color:#777}
.mcflag td{background:#fff8e6}
"""


def solution_html(ch, docx_zip):
    K = katex_render(our_strings(ch) + [t for _, t in load_criteria(ch)])
    R = lambda s: rich(s, K)
    qs = ch["questions"]
    mcs = [q for q in qs if q.get("mc")]
    sas = [q for q in qs if not q.get("mc")]
    h = [f"<h1>{html.escape(ch['title'])}: solutions</h1>",
         f"<div class='sub'>Cambridge Senior Science Physics VCE Units 1&amp;2. {len(set(q['q'].rstrip('abcdefgh') for q in qs))} questions, "
         f"{ch['total']} marks. Teacher copy: corrected answers, working and marking points. Not for students before the test.</div>"]
    if mcs:
        h.append(f"<h2>Multiple choice ({sum(q['marks'] for q in mcs)} marks, 1 each)</h2>")
        h.append("<table class='mc'><tr><th>Q</th><th>Ans</th><th>Why</th><th>Criteria</th></tr>")
        for q in mcs:
            why = R(q.get("why", ""))
            if q.get("steps"):
                why += "<table class='steps'>" + "".join(f"<tr><td>{html.escape(a)}</td><td>{R(b)}</td></tr>" for a, b in q["steps"]) + "</table>"
            if q.get("note"):
                why += f"<div class='note'>{R(q['note'])}</div>"
            if q.get("flag"):
                why += f"<div class='flag'><b>Check:</b> {R(q['flag'])}</div>"
            h.append(f"<tr><td>{q['q']}</td><td>{q['mc']}</td><td>{why}</td><td>{', '.join(q['crit'])}</td></tr>")
        h.append("</table>")
    if sas:
        h.append(f"<h2>Short answer ({sum(q['marks'] for q in sas)} marks)</h2>")
        for q in sas:
            parts = [f"<div class='q'><div class='qh'><span class='qn'>Q{q['q']}</span>"
                     f"<span class='mk'>{q['marks']} mark{'s' if q['marks'] > 1 else ''}</span>"
                     f"<span class='cr'>{', '.join(q['crit'])}</span></div>",
                     f"<div class='stem'>{R(q['stem'])}</div>",
                     f"<div class='ans'>Answer: {R(q['ans'])}</div>"]
            if q.get("steps"):
                parts.append("<table class='steps'>" + "".join(
                    f"<tr><td>{html.escape(a)}</td><td>{R(b)}</td></tr>" for a, b in q["steps"]) + "</table>")
            if q.get("points"):
                parts.append("<ul class='pts'>" + "".join(f"<li>{R(p)}</li>" for p in q["points"]) + "</ul>")
            if q.get("img"):
                data = base64.b64encode(docx_zip.read(ch["images"][q["img"]])).decode()
                parts.append(f"<div class='fig'><img src='data:image/jpeg;base64,{data}'>"
                             f"<div class='cap'>{html.escape(q.get('img_caption', ''))}</div></div>")
            if q.get("note"):
                parts.append(f"<div class='note'>{R(q['note'])}</div>")
            if q.get("flag"):
                parts.append(f"<div class='flag'><b>Corrected:</b> {R(q['flag'])}</div>")
            parts.append("</div>")
            h.append("".join(parts))
    rows, per_sec = coverage(ch)
    h.append("<h2 style='break-before:page'>What the test covers</h2>")
    h.append("<p>Marks are counted against each question's main criterion. \"Also\" lists questions that touch a criterion "
             "without being counted there. Red rows are not tested.</p>")
    h.append("<table class='cov'><tr><th>Criterion</th><th>Questions</th><th>Marks</th><th>Also</th></tr>")
    for r in rows:
        z = " class='z'" if not r["qs"] and not r["also"] else ""
        h.append(f"<tr><td{z}><b>{r['code']}</b> {R(r['text'])}</td><td>{', '.join(r['qs']) or 'none'}</td>"
                 f"<td>{r['marks']}</td><td>{', '.join(r['also'])}</td></tr>")
    h.append(f"<tr><th>Total</th><th></th><th>{sum(r['marks'] for r in rows)}</th><th></th></tr></table>")
    h.append("<h2>Marks by section</h2><table class='cov'><tr>" + "".join(f"<th>{s}</th>" for s in per_sec) +
             "<th>Total</th></tr><tr>" + "".join(f"<td>{v}</td>" for v in per_sec.values()) +
             f"<td>{sum(per_sec.values())}</td></tr></table>")
    h.append("<div class='foot'>Questions and original answers: Cambridge Senior Science Physics VCE Units 1&amp;2, "
             "Chapter test, Cambridge University Press &amp; Assessment 2023. Working, marking points and corrections: teacher. "
             "Licensed school resource: shared drive only.</div>")
    page = (f"<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'><title>{html.escape(ch['title'])} solutions</title>"
            f"<style>{fonts_css()}{CSS}</style></head><body>{''.join(h)}</body></html>")
    total_cov = sum(r["marks"] for r in rows)
    return page, rows, per_sec, total_cov


def print_pdf(html_path, pdf_path, tmp):
    subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", f"--user-data-dir={tmp}/chrome",
                    "--no-pdf-header-footer", f"--print-to-pdf={pdf_path}", html_path.as_uri()],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# =====================================================================================
# Teacher notes
# =====================================================================================

def notes_md(ch, n_student_pages, added_blank, n_sol_pages, rows, per_sec):
    N = ch["notes"]
    L = [f"# {ch['title']}: teacher notes", "",
         "Nothing here has been tried with a class yet.", "",
         "## Files", "",
         f"- `{ch['code']} Test (student).pdf`: Cambridge's paper, answers removed, {n_student_pages} pages"
         + (" (last page blank, added for double-sided printing)" if added_blank else "") + ".",
         f"- `{ch['code']} Test (solutions).pdf`: corrected solutions and coverage table, {n_sol_pages} pages. Teacher only.",
         "", "## Timing and marks", "",
         f"- {ch['n_questions']} questions, {ch['total']} marks. Marks by section: "
         + ", ".join(f"{s} {v}" for s, v in per_sec.items()) + ".",
         f"- {N['time']}",
         "", "## Read out before the test", ""]
    L += [f"- {x}" for x in N["readouts"]] or ["- Nothing."]
    L += ["", "Optional, if students ask:", ""] + [f"- {x}" for x in N["optional"]]
    L += ["", "## Cambridge answer key: errors and checks", ""] + [f"- {x}" for x in N["errors"]]
    L += ["", "## Criteria not tested", ""]
    none = [r for r in rows if not r["qs"] and not r["also"]]
    touched = [r for r in rows if not r["qs"] and r["also"]]
    L += [f"- **{r['code']}** {r['text']}" for r in none] or ["- None."]
    if touched:
        L += ["", "Tested, but its marks are counted under another criterion in the table:", ""]
        L += [f"- **{r['code']}** {r['text']} (Q{', Q'.join(r['also'])})" for r in touched]
    L += ["", "## Diagrams and printing", ""] + [f"- {x}" for x in N["diagrams"]]
    L += ["", "## Layout", ""] + [f"- {x}" for x in N["layout"]]
    L += ["", "## Other", ""] + [f"- {x}" for x in N["other"]]
    L += ["", "Licensed Cambridge content: keep on the school shared drive, not in any git repo.", ""]
    return "\n".join(L)


# =====================================================================================
# main
# =====================================================================================

def main():
    only = [int(a) for a in sys.argv[1:] if a.isdigit()]
    if not list(Path("/usr/lib/libreoffice/program").glob("libsmlo.so")):
        sys.exit("LibreOffice Math is missing (apt-get install libreoffice-math).")
    tmp = Path(tempfile.mkdtemp(prefix="tests_"))
    (tmp / "fonts.conf").write_text(FONTS_CONF)
    png = HERE / "png"
    png.mkdir(exist_ok=True)
    problems = []
    for num, ch in CHAPTERS.items():
        if only and num not in only:
            continue
        log(f"{ch['code']}:")
        # our wording checks
        for s in our_strings(ch):
            if "\u2013" in s or "\u2014" in s:
                problems.append(f"{ch['code']}: dash in our text: {s[:60]}")
            if "\u00f7" in s or "m s^" in s or "m s\u207b" in s or "\\text{m s}" in s:
                problems.append(f"{ch['code']}: banned notation in our text: {s[:60]}")
        if sum(q["marks"] for q in ch["questions"]) != ch["total"]:
            problems.append(f"{ch['code']}: question marks add to {sum(q['marks'] for q in ch['questions'])}, not {ch['total']}")
        # student
        spdf, nkeep, blank, _ = build_student(ch, tmp, problems)
        nst = len(PdfReader(spdf).pages)
        log(f"  student: {nst} pages ({nkeep} from Cambridge{' + 1 blank' if blank else ''})")
        # solutions
        zf = zipfile.ZipFile(ch["docx"])
        page, rows, per_sec, total_cov = solution_html(ch, zf)
        if total_cov != ch["total"]:
            problems.append(f"{ch['code']}: coverage table adds to {total_cov}")
        if "katex-error" in page:
            problems.append(f"{ch['code']}: katex-error in solutions")
        visible = re.sub(r'<style>.*?</style>', '', page, flags=re.S)
        visible = re.sub(r'<span class="katex-mathml">.*?</math></span>', '', visible, flags=re.S)
        for bad in ["\u00f7", "m s\u207b", "m s^", "m s<sup"]:
            if bad in visible:
                problems.append(f"{ch['code']}: '{bad}' in solutions")
        hpath = HERE / f"{ch['code']} Test (solutions).html"
        hpath.write_text(page)
        sol = HERE / f"{ch['code']} Test (solutions).pdf"
        print_pdf(hpath, sol, tmp)
        # Chrome writes A4 as 8.26 x 11.69 in (0.1 mm narrow): set exact A4
        wr = PdfWriter()
        for p in PdfReader(sol).pages:
            wr.add_page(to_exact_a4(p))
        wr.add_metadata({"/Title": f"{ch['title']} (solutions)"})
        with open(sol, "wb") as f:
            wr.write(f)
        rs = PdfReader(sol)
        for i, p in enumerate(rs.pages, 1):
            w, h = float(p.mediabox.width), float(p.mediabox.height)
            if abs(w / MM - 210) > 0.05 or abs(h / MM - 297) > 0.05:
                problems.append(f"{sol.name} page {i} is {w / MM:.2f} x {h / MM:.2f} mm")
        with pdfplumber.open(sol) as p:
            stext = "\n".join((pg.extract_text() or "") for pg in p.pages)
        for bad in ["\u00f7", "m s\u207b", "m s\u2212"]:
            if bad in stext:
                problems.append(f"{sol.name}: '{bad}' in PDF text")
        log(f"  solutions: {len(rs.pages)} pages")
        # notes
        md = notes_md(ch, nst, blank, len(rs.pages), rows, per_sec)
        if "\u2013" in md or "\u2014" in md:
            problems.append(f"{ch['code']}: dash in teacher notes")
        (HERE / f"{ch['code']} test teacher notes.md").write_text(md)
        # renders
        for old in png.glob(f"{ch['code']}-*.png"):
            old.unlink()
        subprocess.run(["pdftoppm", "-r", "100", "-png", str(spdf), str(png / f"{ch['code']}-student")], check=True)
        subprocess.run(["pdftoppm", "-r", "100", "-png", str(sol), str(png / f"{ch['code']}-solutions")], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    if problems:
        log("PROBLEMS:\n  " + "\n  ".join(problems))
        sys.exit(1)
    log("All checks passed.")


if __name__ == "__main__":
    main()
