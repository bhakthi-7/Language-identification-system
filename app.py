"""Streamlit user interface for the Language Identification System.

Run with:  streamlit run app.py
"""

from datetime import datetime

import streamlit as st

import config
from detector import (
    STATUS_INCONCLUSIVE,
    STATUS_LOW_CONFIDENCE,
    InvalidInputError,
    get_detector,
)
from utils import load_samples, truncate

st.set_page_config(page_title=config.APP_TITLE, page_icon="🌐", layout="centered")

CSS = """
<style>
.result-card {border:1px solid #e5e7eb; border-radius:14px; padding:1.4rem 1.6rem;
  background:#f8f9ff; margin:0.6rem 0 1rem 0;}
.result-card .label {font-size:0.8rem; color:#6b7280; text-transform:uppercase; letter-spacing:.06em;}
.result-card .language {font-size:2.2rem; font-weight:700; color:#312e81; line-height:1.2;}
.result-card .meta {color:#4b5563; margin-top:.2rem;}
.footer {text-align:center; color:#9ca3af; font-size:.85rem; margin-top:2.5rem;}
textarea {font-size:1.05rem !important;}
</style>
"""


@st.cache_resource(show_spinner="Loading language model…")
def load_detector():
    """Load the model once per server process."""
    return get_detector()


def init_state() -> None:
    """Create session-state keys on first run."""
    st.session_state.setdefault("text_input", "")
    st.session_state.setdefault("history", [])
    st.session_state.setdefault("result", None)
    st.session_state.setdefault("error", None)


def set_sample(text: str) -> None:
    """Callback: place an example text in the input box."""
    st.session_state.text_input = text
    st.session_state.result = None
    st.session_state.error = None


def clear_all() -> None:
    """Callback: reset the input and the current result."""
    st.session_state.text_input = ""
    st.session_state.result = None
    st.session_state.error = None


def run_detection() -> None:
    """Callback: validate and classify the current text."""
    text = st.session_state.text_input
    st.session_state.result = None
    st.session_state.error = None
    try:
        result = load_detector().detect(text)
    except InvalidInputError as exc:
        st.session_state.error = str(exc)
        return
    st.session_state.result = result
    label = result.language if result.language else "Inconclusive"
    st.session_state.history.insert(
        0,
        {
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Text": truncate(text, 50),
            "Result": label,
            "Score": f"{result.score:.2f}" if result.score is not None else "–",
        },
    )
    del st.session_state.history[config.HISTORY_LIMIT :]


def render_result(result) -> None:
    """Show the result card, warnings and alternative predictions."""
    if result.status == STATUS_INCONCLUSIVE:
        st.warning("**Inconclusive.** No language could be identified reliably.")
    else:
        iso = f"ISO 639 code: <b>{result.code}</b>"
        script = f" &nbsp;·&nbsp; Script: <b>{result.script}</b>" if result.script else ""
        st.markdown(
            f"""<div class="result-card">
            <div class="label">Detected language</div>
            <div class="language">{result.language}</div>
            <div class="meta">{iso}{script}</div></div>""",
            unsafe_allow_html=True,
        )
        st.progress(
            min(max(result.score, 0.0), 1.0),
            text=f"Model confidence score: {result.score:.1%}",
        )
        st.caption(
            "This is the model's normalised score, not a calibrated probability."
        )
        if result.status == STATUS_LOW_CONFIDENCE:
            st.info("Low-reliability result, see the note below.")

    for message in result.warnings:
        st.warning(message)

    if result.candidates:
        st.markdown("**Top candidates**")
        st.table(
            [
                {"Language": c.language, "Code": c.code, "Score": f"{c.score:.4f}"}
                for c in result.candidates
            ]
        )


def main() -> None:
    """Render the page."""
    init_state()
    st.markdown(CSS, unsafe_allow_html=True)
    st.title(f"🌐 {config.APP_TITLE}")
    st.write(config.APP_SUBTITLE + ". Supports English, Kannada, Hindi and many more.")

    samples = load_samples()
    st.markdown("**Try an example**")
    featured = ["English", "Kannada", "Hindi"]
    cols = st.columns(len(featured))
    for col, name in zip(cols, featured):
        col.button(name, key=f"sample_{name}", on_click=set_sample,
                   args=(samples[name],), use_container_width=True)
    others = [n for n in samples if n not in featured]
    st.selectbox(
        "More languages", ["Select a language…"] + others, key="other_sample",
        on_change=lambda: set_sample(samples[st.session_state.other_sample])
        if st.session_state.other_sample in samples else None,
    )

    st.text_area(
        "Enter or paste text",
        key="text_input",
        height=170,
        max_chars=config.MAX_INPUT_CHARS,
        placeholder="Type or paste text in any language…",
    )

    left, right = st.columns([3, 1])
    left.button("Detect Language", type="primary", on_click=run_detection,
                use_container_width=True)
    right.button("Clear", on_click=clear_all, use_container_width=True)

    if st.session_state.error:
        st.error(st.session_state.error)
    if st.session_state.result is not None:
        render_result(st.session_state.result)

    with st.expander("Detection history (this session)"):
        if st.session_state.history:
            st.table(st.session_state.history)
        else:
            st.write("No detections yet.")

    with st.expander("About and limitations"):
        st.markdown(
            "- Longer, complete sentences give the most reliable results.\n"
            "- Very short inputs (a word or two) can be misclassified.\n"
            "- Mixed-language text is reported as a single language, which may "
            "not be the one you consider dominant.\n"
            "- Romanised text (e.g. Hindi typed in English letters) is not "
            "reliably supported."
        )

    st.markdown(
        '<div class="footer">NLP-based language-identification application '
        "· Powered by py3langid and Streamlit</div>",
        unsafe_allow_html=True,
    )


main()
