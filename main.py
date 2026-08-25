import cv2
import mediapipe as mp
import math
import numpy as np
from collections import deque

# ============================================================
# MEDIAPIPE
# ============================================================

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.55,
    min_tracking_confidence=0.55
)

# ============================================================
# CAMERA
# ============================================================

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Camera open nahi ho raha.")
    exit()

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# ============================================================
# VARIABLES
# ============================================================

background = None

movement_history = deque(maxlen=30)

portal_active = False
opening = False
closing = False

portal_scale = 0.0

rotation = 0.0

# Portal position
portal_x = None
portal_y = None
portal_radius = None

# Last stable position
last_center_x = None
last_center_y = None
last_radius = None

# Tracking loss
tracking_lost_frames = 0
MAX_TRACKING_LOSS = 25

# ============================================================
# FIRE PARTICLES
# ============================================================

fire_particles = []

for _ in range(240):

    fire_particles.append({
        "angle": np.random.uniform(
            0,
            2 * math.pi
        ),

        "distance": np.random.uniform(
            0.96,
            1.08
        ),

        "speed": np.random.uniform(
            0.8,
            3.5
        ),

        "rise": np.random.uniform(
            0,
            30
        ),

        "size": np.random.uniform(
            1,
            4
        ),

        "life": np.random.uniform(
            20,
            80
        ),

        "noise": np.random.uniform(
            0,
            100
        )
    })


# ============================================================
# DISTANCE
# ============================================================

def distance(p1, p2):

    return math.hypot(
        p2[0] - p1[0],
        p2[1] - p1[1]
    )


# ============================================================
# CIRCULAR SCORE
# ============================================================

def circular_score(points):

    if len(points) < 15:
        return 0

    total = 0

    for i in range(1, len(points)):

        total += distance(
            points[i - 1],
            points[i]
        )

    direct = distance(
        points[0],
        points[-1]
    )

    return total / max(
        direct,
        1
    )


# ============================================================
# FINGER EXTENSION
# ============================================================

def finger_extended(
    hand,
    tip,
    pip
):

    lm = hand.landmark

    wrist = lm[0]

    tip_distance = math.hypot(
        lm[tip].x - wrist.x,
        lm[tip].y - wrist.y
    )

    pip_distance = math.hypot(
        lm[pip].x - wrist.x,
        lm[pip].y - wrist.y
    )

    return tip_distance > pip_distance * 1.05


# ============================================================
# FIST DETECTION
# ============================================================

def is_fist(hand):

    # Four fingers
    extended = 0

    fingers = [
        (8, 6),
        (12, 10),
        (16, 14),
        (20, 18)
    ]

    for tip, pip in fingers:

        if finger_extended(
            hand,
            tip,
            pip
        ):

            extended += 1

    # 0 or 1 extended finger = fist
    return extended <= 1


# ============================================================
# OPEN PALM
# ============================================================

def is_open_palm(hand):

    extended = 0

    fingers = [
        (8, 6),
        (12, 10),
        (16, 14),
        (20, 18)
    ]

    for tip, pip in fingers:

        if finger_extended(
            hand,
            tip,
            pip
        ):

            extended += 1

    return extended >= 3


# ============================================================
# RESET PARTICLE
# ============================================================

def reset_particle(p):

    p["angle"] = np.random.uniform(
        0,
        2 * math.pi
    )

    p["distance"] = np.random.uniform(
        0.96,
        1.08
    )

    p["speed"] = np.random.uniform(
        0.8,
        3.5
    )

    p["rise"] = np.random.uniform(
        0,
        8
    )

    p["size"] = np.random.uniform(
        1,
        4
    )

    p["life"] = np.random.uniform(
        25,
        90
    )

    p["noise"] = np.random.uniform(
        0,
        100
    )


# ============================================================
# FIRE EFFECT
# ============================================================

def draw_fire(
    frame,
    cx,
    cy,
    radius,
    rotation
):

    h, w = frame.shape[:2]

    # ========================================================
    # GLOW
    # ========================================================

    glow = np.zeros_like(frame)

    cv2.circle(
        glow,
        (cx, cy),
        radius + 40,
        (0, 25, 255),
        25
    )

    cv2.circle(
        glow,
        (cx, cy),
        radius + 18,
        (0, 100, 255),
        12
    )

    glow = cv2.GaussianBlur(
        glow,
        (51, 51),
        0
    )

    frame[:] = cv2.addWeighted(
        frame,
        1.0,
        glow,
        0.65,
        0
    )

    # ========================================================
    # FLAMES
    # ========================================================

    flame_count = 90

    for i in range(flame_count):

        angle = (
            rotation * 0.012
            +
            i * (
                2 * math.pi /
                flame_count
            )
        )

        wave = math.sin(
            rotation * 0.06
            +
            i * 1.8
        )

        wave2 = math.sin(
            rotation * 0.11
            +
            i * 3.0
        )

        length = int(
            5
            +
            abs(wave) * 15
            +
            abs(wave2) * 10
        )

        r = (
            radius
            +
            math.sin(
                rotation * 0.05
                +
                i
            ) * 4
        )

        x1 = int(
            cx
            +
            math.cos(angle) * r
        )

        y1 = int(
            cy
            +
            math.sin(angle) * r
        )

        x2 = int(
            x1
            +
            math.cos(angle)
            * length
        )

        y2 = int(
            y1
            +
            math.sin(angle)
            * length
            -
            length * 0.25
        )

        if (
            0 <= x1 < w
            and
            0 <= y1 < h
            and
            0 <= x2 < w
            and
            0 <= y2 < h
        ):

            cv2.line(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 50, 255),
                7
            )

            cv2.line(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 155, 255),
                4
            )

            cv2.line(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 230, 255),
                1
            )

    # ========================================================
    # SPARKS
    # ========================================================

    for p in fire_particles:

        p["rise"] += p["speed"]

        p["life"] -= 1

        p["angle"] += np.random.uniform(
            -0.025,
            0.025
        )

        if (
            p["life"] <= 0
            or
            p["rise"] > radius * 0.9
        ):

            reset_particle(p)

        angle = p["angle"]

        r = (
            radius
            *
            p["distance"]
        )

        wobble = math.sin(
            p["rise"] * 0.15
            +
            p["noise"]
        ) * 6

        px = int(
            cx
            +
            math.cos(angle) * r
            +
            wobble
        )

        py = int(
            cy
            +
            math.sin(angle) * r
            -
            p["rise"]
        )

        if not (
            0 <= px < w
            and
            0 <= py < h
        ):

            continue

        size = max(
            1,
            int(p["size"])
        )

        if size >= 4:

            color = (
                0,
                230,
                255
            )

        elif size >= 2:

            color = (
                0,
                150,
                255
            )

        else:

            color = (
                0,
                70,
                255
            )

        cv2.circle(
            frame,
            (px, py),
            size,
            color,
            -1
        )

        if size >= 3:

            cv2.circle(
                frame,
                (px, py),
                1,
                (200, 255, 255),
                -1
            )


# ============================================================
# START
# ============================================================

print("========================================")
print("       AI FIRE PORTAL")
print("========================================")
print("B = Capture background")
print("C = Open portal")
print("X = Close portal")
print("Q = Exit")
print("")
print("Circular motion = Open")
print("Open palms = Open")
print("Both palms closed = Close")
print("========================================")


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    ret, frame = cap.read()

    if not ret:
        break

    frame = cv2.flip(
        frame,
        1
    )

    h, w, _ = frame.shape

    original_frame = frame.copy()

    # ========================================================
    # MEDIAPIPE
    # ========================================================

    rgb = cv2.cvtColor(
        original_frame,
        cv2.COLOR_BGR2RGB
    )

    results = hands.process(
        rgb
    )

    positions = []

    fist_count = 0
    palm_count = 0

    # ========================================================
    # HANDS
    # ========================================================

    if results.multi_hand_landmarks:

        for hand in results.multi_hand_landmarks:

            wrist = hand.landmark[0]

            x = int(
                wrist.x * w
            )

            y = int(
                wrist.y * h
            )

            positions.append(
                (x, y)
            )

            if is_fist(hand):

                fist_count += 1

            if is_open_palm(hand):

                palm_count += 1


    # ========================================================
    # TWO HANDS
    # ========================================================

    if len(positions) == 2:

        tracking_lost_frames = 0

        x1, y1 = positions[0]
        x2, y2 = positions[1]

        # ----------------------------------------------------
        # TARGET CENTER
        # ----------------------------------------------------

        target_x = (
            x1 + x2
        ) // 2

        target_y = (
            y1 + y2
        ) // 2

        # ----------------------------------------------------
        # HAND DISTANCE
        # ----------------------------------------------------

        hand_distance = distance(
            positions[0],
            positions[1]
        )

        # ----------------------------------------------------
        # MUCH LARGER SIZE RANGE
        # ----------------------------------------------------

        target_radius = int(
            hand_distance * 0.78
        )

        # Minimum
        target_radius = max(
            60,
            target_radius
        )

        # Maximum
        target_radius = min(
            target_radius,
            min(
                target_x,
                target_y,
                w - target_x,
                h - target_y
            )
        )

        # ----------------------------------------------------
        # POSITION
        # ----------------------------------------------------

        if portal_x is None:

            portal_x = target_x
            portal_y = target_y

            portal_radius = target_radius

        else:

            # VERY RESPONSIVE MOVEMENT
            portal_x += (
                target_x
                -
                portal_x
            ) * 0.72

            portal_y += (
                target_y
                -
                portal_y
            ) * 0.72

            # VERY RESPONSIVE SIZE
            portal_radius += (
                target_radius
                -
                portal_radius
            ) * 0.90

        center_x = int(
            portal_x
        )

        center_y = int(
            portal_y
        )

        radius = int(
            portal_radius
        )

        # Save
        last_center_x = center_x
        last_center_y = center_y
        last_radius = radius

        # ----------------------------------------------------
        # CIRCLE TRACKING
        # ----------------------------------------------------

        movement_history.append(
            (
                center_x,
                center_y
            )
        )

        score = circular_score(
            movement_history
        )

        # ----------------------------------------------------
        # OPEN PALMS
        # ----------------------------------------------------

        if (
            palm_count == 2
            and
            background is not None
            and
            not portal_active
            and
            not opening
            and
            not closing
        ):

            opening = True

        # ----------------------------------------------------
        # CIRCULAR MOTION
        # ----------------------------------------------------

        if (
            len(movement_history) >= 15
            and
            score > 1.5
            and
            background is not None
            and
            not portal_active
            and
            not opening
            and
            not closing
        ):

            opening = True

        # ----------------------------------------------------
        # BOTH FISTS = CLOSE
        # ----------------------------------------------------

        if (
            fist_count == 2
            and
            (
                portal_active
                or
                opening
            )
        ):

            closing = True
            opening = False

    else:

        score = 0

        tracking_lost_frames += 1


    # ========================================================
    # OPEN ANIMATION
    # ========================================================

    if opening:

        portal_scale += 0.12

        if portal_scale >= 1.0:

            portal_scale = 1.0

            opening = False

            portal_active = True


    # ========================================================
    # CLOSE ANIMATION
    # ========================================================

    if closing:

        portal_scale -= 0.14

        if portal_scale <= 0:

            portal_scale = 0

            closing = False

            portal_active = False

            movement_history.clear()

            rotation = 0

            portal_x = None
            portal_y = None
            portal_radius = None

            last_center_x = None
            last_center_y = None
            last_radius = None


    # ========================================================
    # OUTPUT
    # ========================================================

    frame = original_frame.copy()


    # ========================================================
    # PORTAL
    # ========================================================

    if (
        (
            portal_active
            or
            opening
            or
            closing
        )
        and
        last_center_x is not None
        and
        last_center_y is not None
        and
        last_radius is not None
    ):

        center_x = last_center_x
        center_y = last_center_y
        radius = last_radius

        rotation += 2.5

        animated_radius = int(
            radius
            *
            portal_scale
        )

        animated_radius = max(
            1,
            animated_radius
        )

        # ====================================================
        # VANISH
        # ====================================================

        if (
            background is not None
            and
            animated_radius > 5
        ):

            mask = np.zeros(
                (
                    h,
                    w
                ),
                dtype=np.uint8
            )

            cv2.circle(
                mask,
                (
                    center_x,
                    center_y
                ),
                animated_radius,
                255,
                -1
            )

            frame[
                mask == 255
            ] = background[
                mask == 255
            ]

        # ====================================================
        # FIRE
        # ====================================================

        if animated_radius > 10:

            draw_fire(
                frame,
                center_x,
                center_y,
                animated_radius,
                rotation
            )

        # ====================================================
        # MAIN RING
        # ====================================================

        cv2.circle(
            frame,
            (
                center_x,
                center_y
            ),
            animated_radius,
            (0, 145, 255),
            7
        )

        # ====================================================
        # INNER RING
        # ====================================================

        if animated_radius > 15:

            cv2.circle(
                frame,
                (
                    center_x,
                    center_y
                ),
                animated_radius - 12,
                (0, 230, 255),
                2
            )

        # ====================================================
        # OUTER RING
        # ====================================================

        cv2.circle(
            frame,
            (
                center_x,
                center_y
            ),
            animated_radius + 20,
            (0, 55, 255),
            3
        )

        # ====================================================
        # ROTATING ARCS
        # ====================================================

        angle = rotation % 360

        cv2.ellipse(
            frame,
            (
                center_x,
                center_y
            ),
            (
                animated_radius + 8,
                animated_radius + 8
            ),
            0,
            angle,
            angle + 110,
            (0, 220, 255),
            7
        )

        cv2.ellipse(
            frame,
            (
                center_x,
                center_y
            ),
            (
                animated_radius + 22,
                animated_radius + 22
            ),
            0,
            angle + 180,
            angle + 285,
            (0, 80, 255),
            5
        )


    # ========================================================
    # HAND LANDMARKS
    # ========================================================

    if (
        results.multi_hand_landmarks
        and
        not portal_active
        and
        not opening
        and
        not closing
    ):

        for hand in results.multi_hand_landmarks:

            mp_draw.draw_landmarks(
                frame,
                hand,
                mp_hands.HAND_CONNECTIONS
            )


    # ========================================================
    # STATUS
    # ========================================================

    if portal_active:

        status = "FIRE PORTAL ACTIVE"

    elif opening:

        status = "PORTAL OPENING"

    elif closing:

        status = "PORTAL CLOSING"

    else:

        status = "PORTAL READY"


    cv2.putText(
        frame,
        status,
        (
            20,
            45
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.85,
        (0, 180, 255),
        3
    )


    # ========================================================
    # DEBUG
    # ========================================================

    if len(positions) == 2:

        cv2.putText(
            frame,
            f"Hand Distance: {int(hand_distance)}",
            (
                20,
                80
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (220, 220, 220),
            2
        )

        cv2.putText(
            frame,
            f"Portal Radius: {int(radius)}",
            (
                20,
                110
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (220, 220, 220),
            2
        )

        cv2.putText(
            frame,
            f"Fists: {fist_count}",
            (
                20,
                140
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (220, 220, 220),
            2
        )


    # ========================================================
    # BACKGROUND STATUS
    # ========================================================

    if background is None:

        cv2.putText(
            frame,
            "B = CAPTURE CLEAN BACKGROUND",
            (
                20,
                h - 20
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )

    else:

        cv2.putText(
            frame,
            "BACKGROUND READY",
            (
                20,
                h - 20
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )


    # ========================================================
    # SHOW
    # ========================================================

    cv2.imshow(
        "AI Hand Controlled Fire Portal",
        frame
    )

    key = cv2.waitKey(1) & 0xFF


    # ========================================================
    # B = BACKGROUND
    # ========================================================

    if key == ord("b"):

        background = original_frame.copy()

        movement_history.clear()

        portal_active = False
        opening = False
        closing = False

        portal_scale = 0

        rotation = 0

        portal_x = None
        portal_y = None
        portal_radius = None

        last_center_x = None
        last_center_y = None
        last_radius = None

        print(
            "Clean background captured!"
        )


    # ========================================================
    # C = OPEN
    # ========================================================

    if key == ord("c"):

        if background is None:

            print(
                "Pehle B dabao."
            )

        else:

            opening = True
            closing = False

            print(
                "Portal opening..."
            )


    # ========================================================
    # X = CLOSE
    # ========================================================

    if key == ord("x"):

        closing = True
        opening = False

        print(
            "Portal closing..."
        )


    # ========================================================
    # Q = EXIT
    # ========================================================

    if key == ord("q"):

        break


# ============================================================
# CLEANUP
# ============================================================

cap.release()

cv2.destroyAllWindows()

hands.close()