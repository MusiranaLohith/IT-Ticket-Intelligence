from pathlib import Path


FRONTEND = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System/deployment/frontend"
)

CSS = FRONTEND / "style.css"
BACKUP = FRONTEND / "style.css.before-deploy-op038"


if not CSS.exists():
    raise SystemExit(
        f"FAIL: style.css not found: {CSS}"
    )


current = CSS.read_text(
    encoding="utf-8"
)


if BACKUP.exists():
    raise SystemExit(
        f"FAIL: backup already exists: {BACKUP}"
    )


BACKUP.write_text(
    current,
    encoding="utf-8"
)


HEADER_CONTRAST_CSS = r"""

/* =========================================================
   DEPLOY-OP-038
   HEADER / PRIMARY TEXT CONTRAST CORRECTION
   =========================================================

   Presentation only.
   No application logic.
   No API logic.
   No model logic.
   No runtime changes.
   ========================================================= */


/* =========================================================
   TOP HEADER
   ========================================================= */

.topbar {

    background:
        linear-gradient(
            180deg,
            #ffffff 0%,
            #f5f9fd 100%
        ) !important;

    border-top:
        3px solid
        #0d47b5 !important;

    border-bottom:
        1px solid
        #b9c9dc !important;

    box-shadow:
        0 5px 18px
        rgba(
            18,
            31,
            52,
            0.08
        ) !important;
}


/* =========================================================
   BRAND TITLE
   ========================================================= */

.brand-title {

    color:
        #14213a !important;

    font-weight:
        900 !important;

    letter-spacing:
        -0.025em;

    text-shadow:
        none !important;
}


/* =========================================================
   BRAND SUBTITLE
   ========================================================= */

.brand-subtitle {

    color:
        #4d617b !important;

    font-weight:
        500 !important;

    opacity:
        1 !important;
}


/* =========================================================
   PROTOTYPE STATUS
   ========================================================= */

.prototype-status {

    color:
        #1457c7 !important;

    background:
        linear-gradient(
            180deg,
            #ffffff 0%,
            #eef5ff 100%
        ) !important;

    border:
        1px solid
        #9fb8dc !important;

    font-weight:
        900 !important;

    letter-spacing:
        0.075em;

    opacity:
        1 !important;

    box-shadow:
        0 2px 7px
        rgba(
            33,
            103,
            232,
            0.08
        ),
        inset 0 1px 0
        rgba(
            255,
            255,
            255,
            0.95
        ) !important;
}


/* =========================================================
   MAIN PANEL HEADING
   ========================================================= */

#single-ticket-panel h1 {

    color:
        #16233b !important;

    font-weight:
        900 !important;

    letter-spacing:
        -0.025em;

    text-shadow:
        none !important;
}


#single-ticket-panel .section-header p {

    color:
        #526783 !important;

    font-weight:
        500 !important;

    opacity:
        1 !important;
}


/* =========================================================
   SECTION HEADINGS
   ========================================================= */

.panel h2,
.panel h3 {

    color:
        #18263e !important;

    text-shadow:
        none !important;
}


/* =========================================================
   FORM LABELS
   ========================================================= */

.form-group label {

    color:
        #23344e !important;

    font-weight:
        800 !important;
}


/* =========================================================
   INPUT PLACEHOLDERS
   ========================================================= */

input::placeholder,
textarea::placeholder {

    color:
        #8da0b8 !important;

    opacity:
        1 !important;
}


/* =========================================================
   SECTION TAG
   ========================================================= */

.section-tag {

    color:
        #27415f !important;

    background:
        linear-gradient(
            180deg,
            #f5f9fd,
            #e8f0f8
        ) !important;

    border:
        1px solid
        #b8c9dc !important;

    font-weight:
        900 !important;
}


/* =========================================================
   GENERAL SUPPORTING TEXT
   ========================================================= */

.panel p {

    text-shadow:
        none;
}


/* =========================================================
   FOOTER CONTRAST
   ========================================================= */

.footer {

    color:
        #52647a !important;

    background:
        linear-gradient(
            180deg,
            #f7f9fb,
            #edf2f6
        ) !important;

    border-top:
        1px solid
        #bdc9d6 !important;
}


/* =========================================================
   END DEPLOY-OP-038
   ========================================================= */

"""


new_source = (
    current.rstrip()
    + "\n\n"
    + HEADER_CONTRAST_CSS.lstrip()
    + "\n"
)


CSS.write_text(
    new_source,
    encoding="utf-8"
)


print("============================================================")
print("DEPLOY-OP-038 — HEADER CONTRAST CORRECTION")
print("============================================================")
print("STATUS: PASS")
print(f"CSS_UPDATED: {CSS}")
print(f"BACKUP_CREATED: {BACKUP}")
print("HEADER_BACKGROUND_CORRECTED: True")
print("BRAND_TITLE_CONTRAST_CORRECTED: True")
print("BRAND_SUBTITLE_CONTRAST_CORRECTED: True")
print("PROTOTYPE_BADGE_CONTRAST_CORRECTED: True")
print("MAIN_HEADING_CONTRAST_CORRECTED: True")
print("FORM_LABEL_CONTRAST_CORRECTED: True")
print("SHARP_CORNERS_PRESERVED: True")
print("APP_JS_MODIFIED: False")
print("BACKEND_MODIFIED: False")
print("FROZEN_RUNTIME_MODIFIED: False")
print("MODEL_LOGIC_MODIFIED: False")
print(f"NEW_CSS_SIZE_BYTES: {CSS.stat().st_size}")
print("============================================================")