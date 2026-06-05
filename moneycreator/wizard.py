from pathlib import Path

import yaml

from .pipeline import slugify

VOICE_OPTIONS = [
    ("Adam", "clear male voice, good default"),
    ("Bella", "warm female voice, if available in your MOSS install"),
    ("Nicole", "calm narration voice, if available in your MOSS install"),
    ("Michael", "deep male narration, if available in your MOSS install"),
]

FONT_OPTIONS = [
    ("DejaVu Sans Condensed", "clean default, included on many Linux systems"),
    ("DejaVu Sans", "wide readable subtitle font"),
    ("Liberation Sans", "simple neutral subtitle font"),
    ("Arial", "Windows-friendly subtitle font"),
]

CATEGORY_STOCK_TERMS = {
    "finance": ["personal finance", "saving money", "calculator money", "budgeting laptop"],
    "economy": ["city market shopping", "grocery prices", "economy money", "people buying food"],
    "society": ["city crowd walking", "social media phone", "people using phones", "focused person laptop"],
    "ai": ["artificial intelligence", "person using laptop", "technology screen", "startup office"],
    "business": ["business meeting", "startup office", "entrepreneur laptop", "city office"],
    "motivation": ["person running", "sunrise city", "focused person laptop", "success mindset"],
}


def ask(prompt, default=None):
    suffix = f" [{default}]" if default not in (None, "") else ""
    value = input(f"{prompt}{suffix}: ").strip()
    return value or default


def choose(title, options, default_index=1):
    print(f"\n{title}")
    for i, item in enumerate(options, 1):
        if isinstance(item, tuple):
            name, desc = item
            print(f"  {i}. {name} - {desc}")
        else:
            print(f"  {i}. {item}")
    raw = ask("Choose number", str(default_index))
    try:
        idx = int(raw)
        if 1 <= idx <= len(options):
            chosen = options[idx - 1]
            return chosen[0] if isinstance(chosen, tuple) else chosen
    except ValueError:
        pass
    return options[default_index - 1][0] if isinstance(options[default_index - 1], tuple) else options[default_index - 1]


def script_from_topic(topic, minutes, category):
    seconds = max(15, int(float(minutes) * 60))
    if seconds <= 30:
        return (
            f"{topic} is not just an idea. It is a signal most people ignore. "
            "Look at the pattern, understand the incentive, and you will make better decisions before the crowd reacts."
        )
    return (
        f"{topic} matters because small decisions compound into large outcomes. "
        "First, understand the problem clearly. Second, find the hidden incentive behind it. "
        "Third, act before the trend becomes obvious. The people who win are not always early; "
        "they are the ones who keep learning while everyone else is distracted."
    )


def guess_category(topic):
    text = topic.lower()
    for category, terms in {
        "finance": ["money", "finance", "wealth", "invest", "income", "cash"],
        "economy": ["inflation", "prices", "economy", "market"],
        "ai": ["ai", "artificial", "automation", "tool"],
        "business": ["business", "startup", "sales", "customer"],
        "motivation": ["motivation", "discipline", "success", "habit"],
    }.items():
        if any(term in text for term in terms):
            return category
    return "society"


def build_config_interactive():
    print("\nMoneyCreatorFree Interactive Wizard")
    print("Answer a few questions and the tool will create a ready-to-render YAML config.\n")

    topic = ask("Video topic", "Why most people stay broke")
    category_default = guess_category(topic)
    category = ask("Category", category_default)
    minutes = ask("Video length in minutes", "0.25")
    language = ask("Language for voice/subtitles", "English")
    voice = choose("Suggested MOSS voices", VOICE_OPTIONS, 1)
    font = choose("Suggested subtitle fonts", FONT_OPTIONS, 1)
    font_size = int(ask("Subtitle font size", "42"))
    whisper_model = choose("Whisper subtitle model", ["tiny", "base", "small", "medium"], 1)

    default_terms = CATEGORY_STOCK_TERMS.get(category.lower(), CATEGORY_STOCK_TERMS["society"])
    print("\nSuggested stock search terms:")
    print(", ".join(default_terms))
    custom_terms = ask("Stock terms, comma-separated (Enter to accept suggestions)", "")
    terms = [t.strip() for t in custom_terms.split(",") if t.strip()] or default_terms

    default_script = script_from_topic(topic, minutes, category)
    print("\nSuggested script:")
    print(default_script)
    custom_script = ask("Paste custom script, or press Enter to use suggested script", "")
    script = custom_script or default_script

    run_id = slugify(topic)[:48]
    duration_target = max(15, int(float(minutes) * 60))
    return {
        "id": run_id,
        "topic": topic,
        "category": category,
        "duration_target": duration_target,
        "language": language,
        "script": script,
        "voice": {"provider": "moss", "name": voice},
        "subtitle": {"provider": "whisper", "whisper_model": whisper_model, "font": font, "font_size": font_size},
        "stock": {"provider": "pexels", "clips_per_term": 1, "terms": terms},
        "render": {"aspect": "9:16", "title_font": "DejaVuSansCondensed-Bold"},
        "qa": {"strict": True, "duration_tolerance": 5},
    }


def save_config(config, output_path=None):
    path = Path(output_path or Path("examples") / f"{config['id']}.yaml")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(config, sort_keys=False, allow_unicode=True))
    return path
